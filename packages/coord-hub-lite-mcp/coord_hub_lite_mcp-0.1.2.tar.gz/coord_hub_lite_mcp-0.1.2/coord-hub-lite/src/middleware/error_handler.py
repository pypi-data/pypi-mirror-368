"""Error handling middleware for FastMCP server."""
import traceback
from datetime import datetime, timezone
from typing import Any, Dict
from fastmcp.server.middleware import Middleware, MiddlewareContext
from mcp import McpError
from mcp.types import ErrorData


class ErrorHandlingMiddleware(Middleware):
    """Middleware that catches and handles errors from handlers."""
    
    def __init__(self, include_traceback: bool = False):
        """Initialize error handling middleware.
        
        Args:
            include_traceback: Whether to include stack traces in error responses
        """
        self.include_traceback = include_traceback
    
    async def on_message(self, context: MiddlewareContext, call_next):
        """Handle all MCP messages with error catching."""
        try:
            # Call the next middleware/handler
            result = await call_next(context)
            return result
            
        except McpError:
            # Re-raise MCP errors as-is
            raise
            
        except ValueError as e:
            # Convert validation errors to MCP errors
            raise McpError(ErrorData(
                code=-32602,  # Invalid params
                message=str(e)
            ))
            
        except KeyError as e:
            # Convert missing field errors
            raise McpError(ErrorData(
                code=-32602,  # Invalid params
                message=f"Missing required field: {e}"
            ))
            
        except PermissionError as e:
            # Convert permission errors
            raise McpError(ErrorData(
                code=-32603,  # Internal error
                message=f"Permission denied: {e}"
            ))
            
        except Exception as e:
            # Log unexpected errors
            error_details = {
                "method": context.method,
                "error_type": type(e).__name__,
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if self.include_traceback:
                error_details["traceback"] = traceback.format_exc()
            
            # Convert to MCP error
            raise McpError(ErrorData(
                code=-32603,  # Internal error
                message=f"Internal error: {str(e)}"
            ))