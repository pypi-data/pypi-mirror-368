"""
Security Wrapper Framework for MCP Tools

Provides comprehensive security integration for all MCP tools including:
- Authentication enforcement
- RBAC permission checking  
- Audit logging integration
- Rate limiting and input sanitization
- Security metrics collection

This framework eliminates the security bypass identified in Phase 7 analysis
by ensuring all MCP tools go through proper security validation.
"""

import asyncio
import functools
import time
from typing import Dict, Any, Optional, Callable, List, Tuple
from datetime import datetime, timezone

from fastmcp import Context

from src.middleware.mcp_auth import (
    MCPAuthMiddleware, SecurityContext, get_mcp_auth_middleware,
    require_authentication, require_permission, require_capability,
    MCPAuthenticationError, MCPAuthorizationError, MCPRateLimitError,
    MCPInputValidationError
)
from src.services.audit_service import AuditService
from src.database.session import get_async_session


class SecurityMetrics:
    """Collect security metrics for monitoring."""
    
    def __init__(self):
        """Initialize security metrics collector."""
        self._operations = {}
        self._successes = 0
        self._failures = 0
        self._auth_failures = 0
        self._permission_failures = 0
        self._rate_limit_failures = 0
        
    def record_operation(self, tool_name: str, agent_id: str) -> None:
        """Record a security operation."""
        key = f"{tool_name}:{agent_id}"
        self._operations[key] = self._operations.get(key, 0) + 1
    
    def record_success(self) -> None:
        """Record a successful operation."""
        self._successes += 1
    
    def record_failure(self, failure_type: str) -> None:
        """Record a failed operation."""
        self._failures += 1
        if failure_type == "authentication":
            self._auth_failures += 1
        elif failure_type == "authorization":
            self._permission_failures += 1
        elif failure_type == "rate_limit":
            self._rate_limit_failures += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current security metrics."""
        return {
            "total_operations": self._successes + self._failures,
            "successful_operations": self._successes,
            "failed_operations": self._failures,
            "authentication_failures": self._auth_failures,
            "authorization_failures": self._permission_failures,
            "rate_limit_failures": self._rate_limit_failures,
            "success_rate": self._successes / max(1, self._successes + self._failures),
            "operations_by_tool": self._operations
        }


# Global security metrics instance
security_metrics = SecurityMetrics()


class SecurityAuditLogger:
    """Handles security-specific audit logging for MCP operations."""
    
    def __init__(self):
        """Initialize security audit logger."""
        pass
    
    async def log_operation(
        self,
        tool_name: str,
        agent_id: str,
        operation_args: Dict[str, Any],
        result: Dict[str, Any],
        duration_ms: int,
        context: Optional[Context] = None
    ) -> None:
        """Log successful MCP tool operation.
        
        Args:
            tool_name: Name of the MCP tool
            agent_id: ID of the agent performing operation
            operation_args: Arguments passed to the tool
            result: Result returned by the tool
            duration_ms: Operation duration in milliseconds
            context: Optional MCP context
        """
        try:
            async with get_async_session() as session:
                audit_service = AuditService(session)
                
                meta_data = {
                    "tool_name": tool_name,
                    "operation_args": operation_args,
                    "success": result.get("success", False),
                    "duration_ms": duration_ms,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                await audit_service.create_audit_entry(
                    entity_type="mcp_tool",
                    entity_id=f"{tool_name}:{int(time.time())}",
                    action=tool_name,
                    actor=agent_id,
                    changes={"result": result},
                    meta_data=meta_data
                )
                
                if context:
                    await context.debug(f"Logged MCP operation: {tool_name}")
                    
        except Exception as e:
            # Don't fail the operation if audit logging fails
            if context:
                await context.warning(f"Failed to log MCP operation: {str(e)}")
    
    async def log_error(
        self,
        tool_name: str,
        agent_id: str,
        error: Exception,
        operation_args: Dict[str, Any],
        duration_ms: int,
        context: Optional[Context] = None
    ) -> None:
        """Log failed MCP tool operation.
        
        Args:
            tool_name: Name of the MCP tool
            agent_id: ID of the agent attempting operation
            error: Exception that occurred
            operation_args: Arguments passed to the tool
            duration_ms: Operation duration in milliseconds
            context: Optional MCP context
        """
        try:
            async with get_async_session() as session:
                audit_service = AuditService(session)
                
                await audit_service.log_error(
                    entity_type="mcp_tool",
                    entity_id=f"{tool_name}:{int(time.time())}",
                    error_type=type(error).__name__,
                    error_message=str(error),
                    actor=agent_id,
                    stack_trace=None,  # Don't include stack trace for security errors
                    context={
                        "tool_name": tool_name,
                        "operation_args": operation_args,
                        "duration_ms": duration_ms
                    }
                )
                
                if context:
                    await context.debug(f"Logged MCP error: {tool_name}")
                    
        except Exception as e:
            # Don't fail the operation if audit logging fails
            if context:
                await context.warning(f"Failed to log MCP error: {str(e)}")
    
    async def log_security_event(
        self,
        event_type: str,
        agent_id: Optional[str],
        tool_name: str,
        severity: str,
        details: Dict[str, Any],
        context: Optional[Context] = None
    ) -> None:
        """Log security-related event.
        
        Args:
            event_type: Type of security event (auth_failure, permission_denied, etc.)
            agent_id: ID of the agent (if known)
            tool_name: Name of the MCP tool
            severity: Severity level (low, medium, high, critical)
            details: Additional event details
            context: Optional MCP context
        """
        try:
            async with get_async_session() as session:
                audit_service = AuditService(session)
                
                meta_data = {
                    "event_type": event_type,
                    "severity": severity,
                    "tool_name": tool_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **details
                }
                
                await audit_service.create_audit_entry(
                    entity_type="security_event",
                    entity_id=f"{event_type}:{int(time.time())}",
                    action=event_type,
                    actor=agent_id or "unknown",
                    changes={},
                    meta_data=meta_data
                )
                
                if context:
                    await context.warning(f"Logged security event: {event_type}")
                    
        except Exception as e:
            # Don't fail the operation if audit logging fails
            if context:
                await context.warning(f"Failed to log security event: {str(e)}")


# Global security audit logger
security_audit_logger = SecurityAuditLogger()


def require_mcp_permission(permission: str) -> Callable:
    """Decorator to require specific permission for MCP tool.
    
    Args:
        permission: Required permission string (e.g., "task.create")
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract context and security_context from kwargs
            context = kwargs.get('context')
            security_context = kwargs.get('security_context')
            
            if not security_context:
                raise MCPAuthenticationError("Security context required")
            
            # Check permission
            await require_permission(security_context, permission, context)
            
            # Also check capability if defined
            if security_context.capabilities:
                await require_capability(security_context, permission, context)
            
            # Call original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def secure_mcp_tool(
    tool_func: Optional[Callable] = None,
    *,
    permission: Optional[str] = None,
    require_auth: bool = True,
    rate_limit: bool = True,
    input_validation: bool = True,
    audit_logging: bool = True
) -> Callable:
    """Comprehensive security wrapper for MCP tools.
    
    This decorator provides complete security integration including:
    - Authentication enforcement
    - Permission checking
    - Rate limiting
    - Input validation and sanitization  
    - Audit logging
    - Security metrics collection
    
    Can be used as:
        @secure_mcp_tool
        def my_tool(): pass
    
    Or with parameters:
        @secure_mcp_tool(permission="custom.permission")
        def my_tool(): pass
    
    Args:
        tool_func: MCP tool function to secure
        permission: Required permission (auto-detected from function name if None)
        require_auth: Whether to require authentication
        rate_limit: Whether to enforce rate limiting
        input_validation: Whether to validate and sanitize inputs
        audit_logging: Whether to log operations
        
    Returns:
        Secured MCP tool function or decorator
    """
    
    def decorator(func: Callable) -> Callable:
        # Auto-detect permission from function name if not provided
        func_permission = permission
        if func_permission is None:
            func_permission = _get_permission_from_function_name(func.__name__)
        
        @functools.wraps(func)
        async def secured_wrapper(*args, **kwargs):
            start_time = time.time()
            operation_args = {}
            security_context = None
            context = kwargs.get('context')
            
            try:
                # Step 1: Extract or create security context
                if 'security_context' in kwargs:
                    security_context = kwargs.pop('security_context')
                else:
                    # Check for development mode bypass
                    import os
                    if os.getenv('MCP_DEV_MODE', 'false').lower() == 'true':
                        # Development mode: create authenticated context without auth
                        from src.middleware.mcp_auth import SecurityContext
                        security_context = SecurityContext(
                            authenticated=True,
                            auth_method="dev_mode",
                            agent_id="dev-orchestrator",
                            role="admin",
                            permissions=["*"],  # All permissions in dev mode
                            capabilities=["*"]   # All capabilities in dev mode
                        )
                        if context:
                            await context.info("Using development mode authentication bypass")
                    else:
                        # Production mode: require proper authentication
                        auth_middleware = get_mcp_auth_middleware()
                        auth_header = kwargs.pop('auth_header', None)
                        security_context = await auth_middleware.create_security_context_from_mcp(
                            context=context,
                            auth_header=auth_header
                        )
                
                # Step 2: Authentication enforcement
                if require_auth:
                    await require_authentication(security_context, context)
                
                # Step 3: Permission checking
                if func_permission and security_context.authenticated:
                    await require_permission(security_context, func_permission, context)
                    
                    # Also check agent capabilities if defined
                    if security_context.capabilities:
                        await require_capability(security_context, func_permission, context)
                
                # Step 4: Rate limiting
                if rate_limit and security_context.authenticated and security_context.key_id:
                    auth_middleware = get_mcp_auth_middleware()
                    rate_result = await auth_middleware.api_key_manager.check_rate_limit(
                        security_context.key_id
                    )
                    if not rate_result["allowed"]:
                        await security_audit_logger.log_security_event(
                            event_type="rate_limit_exceeded",
                            agent_id=security_context.agent_id,
                            tool_name=func.__name__,
                            severity="medium",
                            details={"retry_after": rate_result.get("retry_after", 60)},
                            context=context
                        )
                        raise MCPRateLimitError(
                            f"Rate limit exceeded. Retry after {rate_result.get('retry_after', 60)} seconds"
                        )
                
                # Step 5: Input validation and sanitization
                if input_validation:
                    sanitized_args, sanitized_kwargs = await _validate_and_sanitize_inputs(
                        args, kwargs, context
                    )
                    args = sanitized_args
                    kwargs = sanitized_kwargs
                
                # Store operation args for audit logging
                operation_args = {
                    "args": [str(arg)[:100] for arg in args],  # Truncate for logging
                    "kwargs": {k: str(v)[:100] for k, v in kwargs.items() if k != 'context'}
                }
                
                # Step 6: Record security metrics
                if security_context.authenticated:
                    security_metrics.record_operation(func.__name__, security_context.agent_id)
                
                # Step 7: Execute the actual tool function
                if context:
                    await context.info(f"Executing secured MCP tool: {func.__name__}")
                
                result = await func(*args, **kwargs)
                
                # Step 8: Post-execution processing
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Record success metrics
                security_metrics.record_success()
                
                # Audit logging for successful operations
                if audit_logging and security_context.authenticated:
                    await security_audit_logger.log_operation(
                        tool_name=func.__name__,
                        agent_id=security_context.agent_id,
                        operation_args=operation_args,
                        result=result,
                        duration_ms=duration_ms,
                        context=context
                    )
                
                if context:
                    await context.info(f"MCP tool completed successfully: {func.__name__}")
                
                return result
                
            except (MCPAuthenticationError, MCPAuthorizationError, MCPRateLimitError, MCPInputValidationError) as e:
                # Security-specific errors
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Determine failure type
                if isinstance(e, MCPAuthenticationError):
                    failure_type = "authentication"
                    severity = "high"
                elif isinstance(e, MCPAuthorizationError):
                    failure_type = "authorization"
                    severity = "medium"
                elif isinstance(e, MCPRateLimitError):
                    failure_type = "rate_limit"
                    severity = "low"
                else:
                    failure_type = "input_validation"
                    severity = "medium"
                
                # Record failure metrics
                security_metrics.record_failure(failure_type)
                
                # Log security event
                await security_audit_logger.log_security_event(
                    event_type=failure_type + "_failure",
                    agent_id=security_context.agent_id if security_context else None,
                    tool_name=func.__name__,
                    severity=severity,
                    details={
                        "error": str(e),
                        "operation_args": operation_args,
                        "duration_ms": duration_ms
                    },
                    context=context
                )
                
                if context:
                    await context.error(f"Security error in MCP tool {func.__name__}: {str(e)}")
                
                # Return error response instead of raising exception
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                
            except Exception as e:
                # General errors
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Record failure metrics
                security_metrics.record_failure("general")
                
                # Log error
                if audit_logging and security_context and security_context.authenticated:
                    await security_audit_logger.log_error(
                        tool_name=func.__name__,
                        agent_id=security_context.agent_id,
                        error=e,
                        operation_args=operation_args,
                        duration_ms=duration_ms,
                        context=context
                    )
                
                if context:
                    await context.error(f"Error in MCP tool {func.__name__}: {str(e)}")
                
                # Return error response
                return {
                    "success": False,
                    "error": f"Tool execution failed: {str(e)}",
                    "error_type": "ExecutionError"
                }
        
        # Mark function as secured to prevent direct calls
        secured_wrapper._security_enabled = True
        secured_wrapper._original_function = func
        secured_wrapper._required_permission = func_permission
        
        return secured_wrapper
    
    # Handle both decorator patterns
    if tool_func is None:
        # Called with parameters: @secure_mcp_tool(permission="...")
        return decorator
    else:
        # Called without parameters: @secure_mcp_tool
        return decorator(tool_func)
async def _validate_and_sanitize_inputs(
    args: Tuple,
    kwargs: Dict[str, Any],
    context: Optional[Context] = None
) -> Tuple[Tuple, Dict[str, Any]]:
    """Validate and sanitize inputs for security.
    
    Args:
        args: Positional arguments
        kwargs: Keyword arguments
        context: Optional MCP context
        
    Returns:
        Tuple of (sanitized_args, sanitized_kwargs)
        
    Raises:
        MCPInputValidationError: If input validation fails
    """
    auth_middleware = get_mcp_auth_middleware()
    
    # Validate input sizes
    for arg in args:
        if not auth_middleware.validate_input_size(arg, context):
            raise MCPInputValidationError("Input data too large")
    
    for key, value in kwargs.items():
        if not auth_middleware.validate_input_size(value, context):
            raise MCPInputValidationError(f"Input parameter '{key}' too large")
    
    # Sanitize string inputs
    sanitized_args = []
    for arg in args:
        if isinstance(arg, str):
            sanitized_args.append(auth_middleware.sanitize_input(arg))
        else:
            sanitized_args.append(arg)
    
    sanitized_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, str):
            sanitized_kwargs[key] = auth_middleware.sanitize_input(value)
        else:
            sanitized_kwargs[key] = value
    
    return tuple(sanitized_args), sanitized_kwargs


def _get_permission_from_function_name(func_name: str) -> str:
    """Auto-detect required permission from function name.
    
    Args:
        func_name: Name of the function
        
    Returns:
        Required permission string
    """
    # Permission mapping for MCP tools
    permission_map = {
        "health_check": "health.check",
        "create_task": "task.create",
        "update_task_status": "task.update",
        "register_agent_tool": "agent.register",
        "find_available_agent_tool": "agent.find",
        "assign_task_tool": "assignment.create",
        "get_task_tree_tool": "assignment.read",
        "upload_plan": "plan.upload",
        "validate_plan": "plan.validate",
        "initialize_database_tool": "database.init"
    }
    
    return permission_map.get(func_name, f"tool.{func_name}")


def get_security_metrics() -> Dict[str, Any]:
    """Get current security metrics for monitoring.
    
    Returns:
        Dictionary of security metrics
    """
    return security_metrics.get_metrics()


def is_tool_secured(func: Callable) -> bool:
    """Check if a tool function is properly secured.
    
    Args:
        func: Function to check
        
    Returns:
        True if function is secured, False otherwise
    """
    return hasattr(func, '_security_enabled') and func._security_enabled


def get_tool_permission(func: Callable) -> Optional[str]:
    """Get the required permission for a secured tool.
    
    Args:
        func: Secured tool function
        
    Returns:
        Required permission string or None if not secured
    """
    return getattr(func, '_required_permission', None)


# Security validation function for startup checks
def validate_security_configuration() -> List[str]:
    """Validate security configuration for all MCP tools.
    
    Returns:
        List of configuration issues (empty if all good)
    """
    issues = []
    
    try:
        # Check if MCP auth middleware is initialized
        get_mcp_auth_middleware()
    except RuntimeError:
        issues.append("MCP authentication middleware not initialized")
    
    # Add more validation checks as needed
    return issues


# Export for security integration
__all__ = [
    'SecurityContext',
    'secure_mcp_tool',
    'require_mcp_permission',
    'get_security_metrics',
    'is_tool_secured',
    'get_tool_permission',
    'validate_security_configuration',
    'security_metrics',
    'security_audit_logger'
]