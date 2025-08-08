"""
MCP Authentication Middleware

Integrates existing authentication frameworks (API keys, JWT, sessions)
with MCP tools to eliminate the security bypass identified in Phase 7.

This middleware provides authentication context for all MCP tool operations
and ensures proper integration with the existing security infrastructure.
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timezone

from fastmcp import Context

from src.auth.api_keys import APIKeyManager
from src.auth.permissions import PermissionManager, PermissionDeniedError
from src.middleware.auth import AuthMiddleware


@dataclass
class SecurityContext:
    """Security context for MCP operations."""
    
    authenticated: bool
    auth_method: Optional[str] = None
    agent_id: Optional[str] = None
    role: Optional[str] = None
    permissions: List[str] = None
    capabilities: List[str] = None
    key_id: Optional[str] = None
    session_id: Optional[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.permissions is None:
            self.permissions = []
        if self.capabilities is None:
            self.capabilities = []
    
    def has_permission(self, permission: str) -> bool:
        """Check if context has a specific permission."""
        if not self.authenticated:
            return False
        
        # Check for exact match
        if permission in self.permissions:
            return True
        
        # Check for wildcard permissions
        if "*" in self.permissions:
            return True
        
        # Check for partial wildcards (e.g., task.* matches task.create)
        perm_parts = permission.split(".")
        for i in range(len(perm_parts)):
            wildcard_perm = ".".join(perm_parts[:i+1]) + ".*"
            if wildcard_perm in self.permissions:
                return True
        
        return False
    
    def has_capability(self, capability: str) -> bool:
        """Check if context has a specific capability."""
        if not self.authenticated:
            return False
        
        # If no capabilities are defined, rely on permissions only
        if not self.capabilities:
            return True
        
        return capability in self.capabilities


class MCPAuthMiddleware:
    """Authentication middleware for MCP tools."""
    
    def __init__(self, auth_middleware: AuthMiddleware):
        """Initialize MCP authentication middleware.
        
        Args:
            auth_middleware: Existing authentication middleware to integrate with
        """
        self.auth_middleware = auth_middleware
        self.api_key_manager = auth_middleware.api_key_manager
        self.permission_manager = auth_middleware.permission_manager
        
        # Security configuration
        self.max_request_size = 1024 * 1024  # 1MB max request size
        self.max_string_length = 10000       # 10K max string length
        
    async def authenticate_mcp_context(
        self, 
        request: Any = None,
        context: Optional[Context] = None,
        auth_header: Optional[str] = None
    ) -> SecurityContext:
        """Authenticate MCP request and create security context.
        
        Args:
            request: Optional HTTP request object (for HTTP-based MCP)
            context: Optional MCP context for logging
            auth_header: Optional direct auth header (for direct tool calls)
            
        Returns:
            SecurityContext with authentication results
        """
        try:
            if context:
                await context.debug("Authenticating MCP request")
            
            # Extract authentication header
            if auth_header:
                # Direct auth header provided
                auth_value = auth_header
            elif request and hasattr(request, 'headers'):
                # Extract from HTTP request
                auth_value = request.headers.get("Authorization", "")
            else:
                # No authentication provided
                if context:
                    await context.warning("No authentication provided for MCP request")
                return SecurityContext(
                    authenticated=False,
                    error="No authentication provided"
                )
            
            if not auth_value:
                return SecurityContext(
                    authenticated=False,
                    error="Missing Authorization header"
                )
            
            # Parse authentication header
            parts = auth_value.split(" ", 1)
            if len(parts) != 2:
                return SecurityContext(
                    authenticated=False,
                    error="Invalid authorization header format"
                )
            
            auth_type, credential = parts
            
            # Handle different authentication methods
            if auth_type == "Bearer":
                return await self._authenticate_api_key(credential, context)
            elif auth_type == "JWT":
                return await self._authenticate_jwt(credential, context)
            elif auth_type == "Session":
                return await self._authenticate_session(credential, context)
            else:
                return SecurityContext(
                    authenticated=False,
                    error=f"Unsupported authentication type: {auth_type}"
                )
            
        except Exception as e:
            if context:
                await context.error(f"Authentication error: {str(e)}")
            return SecurityContext(
                authenticated=False,
                error=f"Authentication failed: {str(e)}"
            )
    
    async def _authenticate_api_key(self, api_key: str, context: Optional[Context]) -> SecurityContext:
        """Authenticate using API key."""
        try:
            # Validate API key
            validation_result = await self.api_key_manager.validate_api_key(api_key)
            
            if not validation_result["valid"]:
                if context:
                    await context.warning(f"Invalid API key: {validation_result.get('error')}")
                return SecurityContext(
                    authenticated=False,
                    error=validation_result.get("error", "Invalid API key")
                )
            
            # Check rate limiting
            key_id = validation_result["key_id"]
            rate_limit_result = await self.api_key_manager.check_rate_limit(key_id)
            
            if not rate_limit_result["allowed"]:
                if context:
                    await context.warning(f"Rate limit exceeded for key {key_id}")
                return SecurityContext(
                    authenticated=False,
                    error=f"Rate limit exceeded. Retry after {rate_limit_result.get('retry_after', 60)} seconds"
                )
            
            # Get role permissions
            role = validation_result["role"]
            permissions = self.permission_manager.get_role_permissions(role)
            
            # Get agent capabilities if defined
            agent_id = validation_result["agent_id"]
            capabilities = self.permission_manager.get_agent_capabilities(agent_id)
            
            if context:
                await context.info(f"API key authentication successful for agent {agent_id}")
            
            return SecurityContext(
                authenticated=True,
                auth_method="api_key",
                agent_id=agent_id,
                role=role,
                permissions=permissions,
                capabilities=capabilities,
                key_id=key_id
            )
            
        except Exception as e:
            return SecurityContext(
                authenticated=False,
                error=f"API key authentication error: {str(e)}"
            )
    
    async def _authenticate_jwt(self, token: str, context: Optional[Context]) -> SecurityContext:
        """Authenticate using JWT token."""
        try:
            # Verify JWT token
            payload = self.auth_middleware.token_manager.verify_token(token)
            
            agent_id = payload["agent_id"]
            role = payload["role"]
            
            # Get role permissions
            permissions = self.permission_manager.get_role_permissions(role)
            
            # Get capabilities from token or agent
            capabilities = payload.get("capabilities", [])
            if not capabilities:
                capabilities = self.permission_manager.get_agent_capabilities(agent_id)
            
            if context:
                await context.info(f"JWT authentication successful for agent {agent_id}")
            
            return SecurityContext(
                authenticated=True,
                auth_method="jwt",
                agent_id=agent_id,
                role=role,
                permissions=permissions,
                capabilities=capabilities
            )
            
        except Exception as e:
            return SecurityContext(
                authenticated=False,
                error=f"JWT authentication error: {str(e)}"
            )
    
    async def _authenticate_session(self, session_id: str, context: Optional[Context]) -> SecurityContext:
        """Authenticate using session ID."""
        try:
            # Validate session
            session_result = await self.auth_middleware.validate_session(session_id)
            
            if not session_result["valid"]:
                return SecurityContext(
                    authenticated=False,
                    error=session_result.get("error", "Invalid session")
                )
            
            agent_id = session_result["agent_id"]
            role = session_result["role"]
            
            # Get role permissions
            permissions = self.permission_manager.get_role_permissions(role)
            
            # Get agent capabilities
            capabilities = self.permission_manager.get_agent_capabilities(agent_id)
            
            if context:
                await context.info(f"Session authentication successful for agent {agent_id}")
            
            return SecurityContext(
                authenticated=True,
                auth_method="session",
                agent_id=agent_id,
                role=role,
                permissions=permissions,
                capabilities=capabilities,
                session_id=session_id
            )
            
        except Exception as e:
            return SecurityContext(
                authenticated=False,
                error=f"Session authentication error: {str(e)}"
            )
    
    async def validate_input_size(self, input_data: Any, context: Optional[Context] = None) -> bool:
        """Validate input data size for DOS protection.
        
        Args:
            input_data: Input data to validate
            context: Optional MCP context for logging
            
        Returns:
            True if input size is acceptable, False otherwise
        """
        try:
            # Check string lengths
            if isinstance(input_data, str):
                if len(input_data) > self.max_string_length:
                    if context:
                        await context.warning(f"String too long: {len(input_data)} > {self.max_string_length}")
                    return False
            
            # Check dictionary/object sizes
            elif isinstance(input_data, dict):
                total_size = 0
                for key, value in input_data.items():
                    if isinstance(key, str):
                        total_size += len(key)
                    if isinstance(value, str):
                        total_size += len(value)
                    elif isinstance(value, (dict, list)):
                        # Recursive check for nested structures
                        if not self.validate_input_size(value, context):
                            return False
                
                if total_size > self.max_request_size:
                    if context:
                        await context.warning(f"Request too large: {total_size} > {self.max_request_size}")
                    return False
            
            # Check list sizes
            elif isinstance(input_data, list):
                for item in input_data:
                    if not self.validate_input_size(item, context):
                        return False
            
            return True
            
        except Exception as e:
            if context:
                await context.error(f"Input validation error: {str(e)}")
            return False
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize input data to prevent injection attacks.
        
        Args:
            input_data: Input string to sanitize
            
        Returns:
            Sanitized input string
        """
        if not isinstance(input_data, str):
            return input_data
        
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            # SQL injection patterns
            "';", "'; ", "--", "/*", "*/", "xp_", "sp_",
            # XSS patterns
            "<script", "</script>", "javascript:", "onclick=", "onerror=",
            # Path traversal
            "../", "..\\", "/etc/", "\\windows\\",
            # Command injection
            "|", "&", ";", "$", "`", "$(", "${",
            # LDAP injection
            "${jndi:", "ldap://", "rmi://",
        ]
        
        sanitized = input_data
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, "")
        
        # Limit length
        if len(sanitized) > self.max_string_length:
            sanitized = sanitized[:self.max_string_length]
        
        return sanitized
    
    async def create_security_context_from_mcp(
        self,
        context: Optional[Context] = None,
        auth_header: Optional[str] = None
    ) -> SecurityContext:
        """Create security context for MCP tool calls.
        
        This is the main entry point for MCP tools to get authentication context.
        
        Args:
            context: MCP context for logging
            auth_header: Optional authentication header
            
        Returns:
            SecurityContext for the request
        """
        if context:
            await context.debug("Creating security context for MCP tool call")
        
        # For MCP tools, we might not have a traditional HTTP request
        # The auth header could come from the MCP client or be embedded in context
        if not auth_header and context:
            # Try to extract auth from MCP context metadata
            auth_header = getattr(context, 'auth_header', None)
        
        return await self.authenticate_mcp_context(
            request=None,
            context=context,
            auth_header=auth_header
        )


class MCPSecurityError(Exception):
    """Base exception for MCP security errors."""
    pass


class MCPAuthenticationError(MCPSecurityError):
    """Raised when MCP authentication fails."""
    pass


class MCPAuthorizationError(MCPSecurityError):
    """Raised when MCP authorization fails."""
    pass


class MCPRateLimitError(MCPSecurityError):
    """Raised when MCP rate limit is exceeded."""
    pass


class MCPInputValidationError(MCPSecurityError):
    """Raised when MCP input validation fails."""
    pass


# Utility functions for MCP security integration
async def require_authentication(security_context: SecurityContext, context: Optional[Context] = None) -> None:
    """Require authentication for MCP operation.
    
    Args:
        security_context: Security context to validate
        context: Optional MCP context for logging
        
    Raises:
        MCPAuthenticationError: If authentication is required but not provided
    """
    if not security_context.authenticated:
        error_msg = security_context.error or "Authentication required"
        if context:
            await context.error(f"Authentication required: {error_msg}")
        raise MCPAuthenticationError(error_msg)


async def require_permission(
    security_context: SecurityContext,
    permission: str,
    context: Optional[Context] = None
) -> None:
    """Require specific permission for MCP operation.
    
    Args:
        security_context: Security context to validate
        permission: Required permission
        context: Optional MCP context for logging
        
    Raises:
        MCPAuthorizationError: If permission is not granted
    """
    if not security_context.has_permission(permission):
        error_msg = f"Permission '{permission}' required"
        if context:
            await context.error(error_msg)
        raise MCPAuthorizationError(error_msg)


async def require_capability(
    security_context: SecurityContext,
    capability: str,
    context: Optional[Context] = None
) -> None:
    """Require specific capability for MCP operation.
    
    Args:
        security_context: Security context to validate
        capability: Required capability
        context: Optional MCP context for logging
        
    Raises:
        MCPAuthorizationError: If capability is not available
    """
    if not security_context.has_capability(capability):
        error_msg = f"Capability '{capability}' required"
        if context:
            await context.error(error_msg)
        raise MCPAuthorizationError(error_msg)


# Global instance (will be initialized by server)
mcp_auth_middleware: Optional[MCPAuthMiddleware] = None


def get_mcp_auth_middleware() -> MCPAuthMiddleware:
    """Get the global MCP authentication middleware instance.
    
    Returns:
        Global MCP authentication middleware
        
    Raises:
        RuntimeError: If middleware is not initialized
    """
    if mcp_auth_middleware is None:
        raise RuntimeError("MCP authentication middleware not initialized")
    return mcp_auth_middleware


def initialize_mcp_auth_middleware(auth_middleware: AuthMiddleware) -> None:
    """Initialize the global MCP authentication middleware.
    
    Args:
        auth_middleware: Existing authentication middleware
    """
    global mcp_auth_middleware
    mcp_auth_middleware = MCPAuthMiddleware(auth_middleware)