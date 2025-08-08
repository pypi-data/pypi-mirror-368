"""Tool wrapper for FastMCP registration."""
from typing import Callable, Dict, Any
from fastmcp.tools import Tool


def wrap_tool(func: Callable, metadata: Dict[str, Any]) -> Tool:
    """Wrap a function as a FastMCP tool.
    
    Args:
        func: The function to wrap
        metadata: Tool metadata including name, description, and parameters
        
    Returns:
        FastMCP Tool instance
    """
    return Tool(
        name=metadata["name"],
        description=metadata["description"],
        inputSchema=metadata["parameters"],
        func=func
    )