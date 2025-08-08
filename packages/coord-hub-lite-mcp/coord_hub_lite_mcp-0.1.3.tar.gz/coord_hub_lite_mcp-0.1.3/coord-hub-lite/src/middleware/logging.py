"""Logging middleware for FastMCP server."""
import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Any, Callable, Dict, Optional
from datetime import datetime, timezone

import structlog
from fastmcp.server.middleware import Middleware, MiddlewareContext

# Context variable for correlation ID
_correlation_context: ContextVar[Dict[str, Any]] = ContextVar(
    "correlation_context", default={}
)

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Get a configured logger instance.
    
    Args:
        name: Logger name, defaults to module name
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


def generate_correlation_id() -> str:
    """Generate a unique correlation ID.
    
    Returns:
        UUID string for correlation tracking
    """
    return str(uuid.uuid4())


def get_correlation_context() -> Dict[str, Any]:
    """Get the current correlation context.
    
    Returns:
        Current context dictionary
    """
    return _correlation_context.get()


def _sanitize_params(params: Any) -> Any:
    """Sanitize sensitive parameters for logging.
    
    Args:
        params: Parameters to sanitize
        
    Returns:
        Sanitized parameters with sensitive values redacted
    """
    if not isinstance(params, dict):
        return params
        
    sensitive_fields = {
        "password", "api_key", "token", "secret", "credential",
        "authorization", "auth_token", "private_key"
    }
    
    sanitized = {}
    for key, value in params.items():
        if key.lower() in sensitive_fields:
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_params(value)
        else:
            sanitized[key] = value
    
    return sanitized


@asynccontextmanager
async def RequestLogger(correlation_id: str):
    """Context manager for request-scoped logging.
    
    Args:
        correlation_id: Correlation ID for the request
        
    Yields:
        Logger instance with correlation context
    """
    # Set correlation context
    token = _correlation_context.set({"correlation_id": correlation_id})
    logger = get_logger("request")
    
    try:
        yield logger
    finally:
        # Clear correlation context
        _correlation_context.reset(token)


class LoggingMiddleware(Middleware):
    """Middleware that logs all MCP requests and responses."""
    
    def __init__(self, include_payloads: bool = False, max_payload_length: int = 1000):
        """Initialize logging middleware.
        
        Args:
            include_payloads: Whether to log request/response payloads
            max_payload_length: Maximum length of payload to log
        """
        self.logger = get_logger("middleware.logging")
        self.include_payloads = include_payloads
        self.max_payload_length = max_payload_length
    
    async def on_message(self, context: MiddlewareContext, call_next):
        """Log all MCP messages."""
        start_time = time.perf_counter()
        
        # Generate correlation ID
        correlation_id = generate_correlation_id()
        
        # Create log context
        log_context = {
            "method": context.method,
            "type": context.type,
            "source": context.source,
            "correlation_id": correlation_id,
            "timestamp": context.timestamp.isoformat() if context.timestamp else datetime.now(timezone.utc).isoformat()
        }
        
        # Log request
        if self.include_payloads and hasattr(context.message, "__dict__"):
            params = _sanitize_params(context.message.__dict__)
            self.logger.info("mcp_request_received", **log_context, params=params)
        else:
            self.logger.info("mcp_request_received", **log_context)
        
        try:
            # Set correlation context
            async with RequestLogger(correlation_id):
                result = await call_next(context)
            
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Log success
            self.logger.info(
                "mcp_request_completed",
                **log_context,
                duration_ms=round(duration_ms, 2),
                status="success"
            )
            
            return result
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Log error
            self.logger.error(
                "mcp_request_failed",
                **log_context,
                duration_ms=round(duration_ms, 2),
                status="error",
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True
            )
            
            # Re-raise
            raise
    
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Log tool calls specifically."""
        tool_name = getattr(context.message, "name", "unknown")
        args = getattr(context.message, "arguments", {})
        
        self.logger.info(
            "tool_call_start",
            tool_name=tool_name,
            args=_sanitize_params(args) if self.include_payloads else None
        )
        
        result = await call_next(context)
        
        self.logger.info("tool_call_complete", tool_name=tool_name)
        return result
    
    async def on_read_resource(self, context: MiddlewareContext, call_next):
        """Log resource reads specifically."""
        resource_uri = getattr(context.message, "uri", "unknown")
        
        self.logger.info("resource_read_start", uri=resource_uri)
        
        result = await call_next(context)
        
        self.logger.info("resource_read_complete", uri=resource_uri)
        return result