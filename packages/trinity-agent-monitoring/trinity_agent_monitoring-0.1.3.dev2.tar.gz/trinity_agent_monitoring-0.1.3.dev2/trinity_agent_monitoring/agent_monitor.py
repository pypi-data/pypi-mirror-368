"""
Trinity Agent Monitoring - A comprehensive monitoring solution for AI agents
"""

import os
import time
import warnings
import logging
from typing import Dict, Any, Optional, List, Union, Callable
from functools import wraps
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from langfuse import get_client, observe
    from langfuse.langchain import CallbackHandler
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.warning("Langfuse not installed. Install with: pip install langfuse")

warnings.filterwarnings("ignore", message="You are trying to use a tool which is not available.")


class TrinityAgentMonitor:
    """
    Trinity Agent Monitoring - Provides comprehensive monitoring capabilities for AI agents
    """
    
    def __init__(self, 
                 public_key: str,
                 secret_key: str,
                 host: str = "https://dev.giggso.com:8382",
                 enable_logging: bool = True):
        """
        Initialize Trinity Agent Monitor with tracing components
        
        Args:
            public_key: Public key for the monitoring service
            secret_key: Secret key for the monitoring service
            host: Host URL for the monitoring service (default: https://dev.giggso.com:8382)
            enable_logging: Whether to enable logging (default: True)
        """
        self.public_key = public_key
        self.secret_key = secret_key
        self.host = host
        self.enable_logging = enable_logging
        
        # Set environment variables
        os.environ["LANGFUSE_PUBLIC_KEY"] = public_key
        os.environ["LANGFUSE_SECRET_KEY"] = secret_key
        os.environ["LANGFUSE_HOST"] = host
        
        if LANGFUSE_AVAILABLE:
            try:
                self.langfuse = get_client()
                self.handler = CallbackHandler()
                
                if self.langfuse.auth_check():
                    if self.enable_logging:
                        logger.info("Trinity Monitor: Connected to monitoring service")
                else:
                    logger.warning("Trinity Monitor: Authentication failed. Check your credentials.")
            except Exception as e:
                logger.error(f"Trinity Monitor: Failed to initialize Langfuse client: {e}")
                self.langfuse = None
                self.handler = None
        else:
            self.langfuse = None
            self.handler = None
            if self.enable_logging:
                logger.info("Trinity Monitor: Initialized in offline mode (Langfuse not available)")
    
    def get_callback_handler(self):
        """
        Get the callback handler for agent monitoring
        
        Returns:
            Langfuse callback handler
        """
        return self.handler
    
    def get_current_trace_id(self) -> Optional[str]:
        """
        Get the current trace ID
        
        Returns:
            Current trace ID or None if not available
        """
        if self.langfuse:
            return self.langfuse.get_current_trace_id()
        return None
    
    def flush(self):
        """
        Flush any pending monitoring data
        """
        if self.langfuse:
            try:
                self.langfuse.flush()
                if self.enable_logging:
                    logger.info("Trinity Monitor: Data flushed successfully")
            except Exception as e:
                logger.error(f"Trinity Monitor: Error flushing data: {e}")
                raise
    
    def get_last_trace(self):
        """
        Get the last trace from the global monitor
        
        Returns:
            Last trace or None if not available
        """
        if self.langfuse:
            traces = self.langfuse.api.trace.list(limit=1)
            return traces
        else:
            raise ValueError("Global monitor not initialized. Use set_monitor() first with your API keys.")
        
    def get_all_traces(self, limit: Optional[int] = None):
        """
        Get all traces from the global monitor
        
        Args:
            limit: Maximum number of traces to return (optional)
        """
        if self.langfuse:
            try:
                if limit:
                    traces = self.langfuse.api.trace.list(limit=limit)
                else:
                    traces = self.langfuse.api.trace.list()
                return traces
            except Exception as e:
                logger.error(f"Failed to get traces: {e}")
                raise
        else:
            raise ValueError("Global monitor not initialized. Use set_monitor() first with your API keys.")

    def get_tools_details(self, tool_details: str, tool_names: str) -> dict:
        """
        Uses regex to extract the tool description and tool's input and output schema from the tool_details
        
        Args:
            tool_details: Tool details from the trace
        """
        tool_names_list = [name.strip() for name in tool_names.split(',')] # Clean tool names
        
        # Pattern to capture:
        # 1. Function name (e.g., "get_current_weather")
        # 2. Parameters (e.g., "location: str")
        # 3. Return type (e.g., "str")
        # 4. The docstring/description (everything after " - " until the next function or the end of the string)
        pattern = re.compile(
            r'(\w+)\((.*?)\)\s*->\s*(.*?)\s*-\s*(.*?)(?=\n\w+\(|$(?s))',
            re.DOTALL  # Allows '.' to match newline characters
        )

        matches = pattern.finditer(tool_details)

        extracted_info = {}
        
        tool_name_iter = iter(tool_names_list)

        for match in matches:
            try:
                current_tool_name = next(tool_name_iter)
            except StopIteration:
                # Handle cases where there are more regex matches than provided tool names
                print("Warning: More tool details found than tool names provided.")
                break # Exit the loop if we run out of tool names

            function_name_from_regex = match.group(1)
            params = match.group(2)
            return_type = match.group(3)
            docstring = match.group(4).strip() # .strip() to remove leading/trailing whitespace

            extracted_info[current_tool_name] = {
                "function_name": function_name_from_regex, # Store the function name as extracted by regex
                "input_schema": params,
                "output_schema": return_type,
                "docstring": docstring
            }

        return extracted_info
    
    def get_trace_metrics(self, trace_id: str) -> Dict[str, Any]:
        """
        Get metrics for a completed trace
        
        Args:
            trace_id: ID of the trace to analyze
            
        Returns:
            Dictionary containing trace metrics
        """
        if not self.langfuse:
            return {"error": "Langfuse not available"}
        
        try:
            completed_trace = self.langfuse.api.trace.get(trace_id)
            
            tools_details = completed_trace.input['args'][0]['agent']['runnable']['middle'][0]['partial_variables']
            
            tools = tools_details['tool_names']
            tools_descriptions = tools_details['tools']

            tools_details = self.get_tools_details(tools_descriptions, tools)

            metrics = {
                "trace_name": completed_trace.name,
                "trace_id": trace_id,
                'tools_available': tools,
                'tools_details': tools_details,
                "tools_used": {},
                "total_tokens": 0,
                "total_cost": 0.0
            }

            total_tokens = 0
            total_cost = 0.0

            for obs in completed_trace.observations:
                
                if obs.end_time:
                    latency_ms = (obs.end_time - obs.start_time).total_seconds() * 1000 if obs.end_time and obs.start_time else "N/A"
                
                obs_dict = None
                input_content = None
                output_content = None
                cost = 0

                if obs.type == "GENERATION":
                    if obs.usage:
                        total_tokens += (obs.usage.total or 0)
                    
                    obs_dict = obs.dict()
                    
                    if 'calculatedTotalCost' in obs_dict and obs_dict['calculatedTotalCost'] is not None:
                        cost = obs_dict['calculatedTotalCost']
                        total_cost += cost
                    
                    if obs.input:
                        input_content = obs.input.get('prompt') if isinstance(obs.input, dict) else obs.input
                        if not input_content and isinstance(obs.input, dict) and obs.input.get('messages'):
                            input_content = obs.input['messages']
                    if obs.output:
                        output_content = obs.output.get('completion') if isinstance(obs.output, dict) else obs.output
                        if not output_content and isinstance(obs.output, dict) and obs.output.get('message'):
                            output_content = obs.output['message']
                
                obs_data = {
                    "name": obs.name,
                    "type": obs.type,
                    "Input": obs.input,
                    "Output": obs.output,
                    "Input Tokens": obs.usage.input if obs.usage else None,
                    "Output Tokens": obs.usage.output if obs.usage else None,
                    "Total Tokens": obs.usage.total if obs.usage else None,
                    "Cost": cost if cost else 0,
                    "Start Time": obs.start_time.isoformat() if obs.start_time else None,
                    "End Time": obs.end_time.isoformat() if obs.end_time else None,
                    "Latency": latency_ms,
                    "Metadata": obs.metadata if obs.metadata else None
                }
                
                metrics["total_tokens"] += (obs.usage.total or 0)
                metrics["total_cost"] += cost if cost else 0

                if obs.name in tools:
                    metrics["tools_used"][obs.name] = metrics["tools_used"].get(obs.name, 0) + 1
            
            return metrics
            
        except Exception as e:
            return {"error": f"Failed to get trace metrics: {str(e)}"}
    
    def monitor_agent(self, agent_name: str = "unknown_agent"):
        """
        Decorator to monitor agent execution
        
        Args:
            agent_name: Name of the agent being monitored
        """
        def decorator(func):
            @wraps(func)
            @observe()
            def wrapper(*args, **kwargs):
                if self.langfuse:
                    trace_id = self.get_current_trace_id()
                    print(f"Trinity Monitor: Starting trace for {agent_name} (ID: {trace_id})")
                
                try:
                    result = func(*args, **kwargs)
                    
                    if self.langfuse:
                        self.flush()
                        print(f"Trinity Monitor: {agent_name} execution completed successfully")
                    
                    return result
                    
                except Exception as e:
                    if self.langfuse:
                        print(f"Trinity Monitor: {agent_name} execution failed: {e}")
                    raise
            
            return wrapper
        return decorator


# Convenience function to create a monitor instance
def create_monitor(public_key: str,
                  secret_key: str,
                  host: str = "https://dev.giggso.com:8382",
                  enable_logging: bool = True) -> TrinityAgentMonitor:
    """
    Create a new Trinity Agent Monitor instance
    
    Args:
        public_key: Public key for the monitoring service
        secret_key: Secret key for the monitoring service
        host: Host URL for the monitoring service (default: https://dev.giggso.com:8382)
        enable_logging: Whether to enable logging (default: True)
        
    Returns:
        TrinityAgentMonitor instance
    """
    return TrinityAgentMonitor(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
        enable_logging=enable_logging
    )


# Global monitor instance for easy access
_global_monitor = None

def get_monitor() -> TrinityAgentMonitor:
    """
    Get the global monitor instance, creating one if it doesn't exist
    
    Returns:
        TrinityAgentMonitor instance
    """
    global _global_monitor
    if _global_monitor is None:
        raise ValueError("Global monitor not initialized. Use set_monitor() first with your API keys.")
    return _global_monitor


def set_monitor(monitor: TrinityAgentMonitor):
    """
    Set the global monitor instance
    
    Args:
        monitor: TrinityAgentMonitor instance to set as global
    """
    global _global_monitor
    _global_monitor = monitor 