"""Authentication middleware for request handling."""

import time
from typing import Dict, Any, Optional
import secrets
from datetime import datetime, timedelta

from src.auth.api_keys import APIKeyManager, JWTTokenManager
from src.auth.permissions import PermissionManager


class AuthMiddleware:
    """Middleware for handling authentication and authorization."""
    
    def __init__(
        self,
        api_key_manager: APIKeyManager,
        token_manager: JWTTokenManager,
        permission_manager: PermissionManager
    ):
        """Initialize authentication middleware.
        
        Args:
            api_key_manager: Manager for API keys
            token_manager: Manager for JWT tokens
            permission_manager: Manager for permissions
        """
        self.api_key_manager = api_key_manager
        self.token_manager = token_manager
        self.permission_manager = permission_manager
        self._sessions: Dict[str, Dict[str, Any]] = {}
        
    async def authenticate(self, request: Any) -> Dict[str, Any]:
        """Authenticate a request.
        
        Args:
            request: The incoming request object
            
        Returns:
            Authentication context with user info
        """
        # Check for Authorization header
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header:
            return {
                "authenticated": False,
                "error": "No authorization header"
            }
            
        # Parse auth header
        parts = auth_header.split(" ", 1)
        if len(parts) != 2:
            return {
                "authenticated": False,
                "error": "Invalid authorization header format"
            }
            
        auth_type, credential = parts
        
        # Handle API key authentication
        if auth_type == "Bearer":
            result = await self.api_key_manager.validate_api_key(credential)
            if result["valid"]:
                return {
                    "authenticated": True,
                    "auth_method": "api_key",
                    "key_id": result["key_id"],
                    "agent_id": result["agent_id"],
                    "role": result["role"],
                    "capabilities": result.get("capabilities", [])
                }
            else:
                return {
                    "authenticated": False,
                    "error": result.get("error", "Invalid API key")
                }
                
        # Handle JWT authentication
        elif auth_type == "JWT":
            try:
                payload = self.token_manager.verify_token(credential)
                return {
                    "authenticated": True,
                    "auth_method": "jwt",
                    "agent_id": payload["agent_id"],
                    "role": payload["role"],
                    "capabilities": payload.get("capabilities", []),
                    "token_payload": payload
                }
            except Exception as e:
                return {
                    "authenticated": False,
                    "error": f"Invalid JWT: {str(e)}"
                }
                
        else:
            return {
                "authenticated": False,
                "error": f"Unsupported auth type: {auth_type}"
            }
            
    async def create_session(
        self,
        agent_id: str,
        role: str,
        timeout_minutes: int = 30
    ) -> str:
        """Create a new session.
        
        Args:
            agent_id: ID of the agent
            role: Role of the agent
            timeout_minutes: Session timeout in minutes
            
        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)
        
        self._sessions[session_id] = {
            "agent_id": agent_id,
            "role": role,
            "created_at": time.time(),
            "timeout_minutes": timeout_minutes,
            "last_activity": time.time()
        }
        
        return session_id
        
    async def validate_session(self, session_id: str) -> Dict[str, Any]:
        """Validate a session.
        
        Args:
            session_id: The session ID to validate
            
        Returns:
            Session validation result
        """
        if session_id not in self._sessions:
            return {"valid": False, "error": "Session not found"}
            
        session = self._sessions[session_id]
        current_time = time.time()
        
        # Check timeout
        timeout_seconds = session["timeout_minutes"] * 60
        if current_time - session["last_activity"] > timeout_seconds:
            # Session expired
            del self._sessions[session_id]
            return {"valid": False, "error": "Session expired"}
            
        # Update last activity
        session["last_activity"] = current_time
        
        return {
            "valid": True,
            "agent_id": session["agent_id"],
            "role": session["role"]
        }
        
    async def check_rate_limit(self, request: Any) -> Dict[str, Any]:
        """Check rate limiting for a request.
        
        Args:
            request: The incoming request
            
        Returns:
            Rate limit check result
        """
        # First authenticate to get the key_id
        auth_context = await self.authenticate(request)
        
        if not auth_context["authenticated"]:
            return {"allowed": True}  # No rate limit for unauthenticated
            
        if auth_context["auth_method"] != "api_key":
            return {"allowed": True}  # Only rate limit API keys
            
        key_id = auth_context.get("key_id")
        if not key_id:
            return {"allowed": True}
            
        return await self.api_key_manager.check_rate_limit(key_id)
        
    async def authorize(
        self,
        auth_context: Dict[str, Any],
        permission: str
    ) -> bool:
        """Check if authenticated user has permission.
        
        Args:
            auth_context: Authentication context from authenticate()
            permission: Permission to check
            
        Returns:
            True if authorized, False otherwise
        """
        if not auth_context.get("authenticated"):
            return False
            
        role = auth_context.get("role")
        if not role:
            return False
            
        # Check role-based permission
        has_permission = self.permission_manager.check_permission(role, permission)
        
        # If role has permission, also check agent capabilities if present
        if has_permission:
            agent_id = auth_context.get("agent_id")
            if agent_id and self.permission_manager.get_agent_capabilities(agent_id):
                # If agent has specific capabilities, must have the capability too
                return self.permission_manager.agent_has_capability(
                    agent_id, permission
                )
                
        return has_permission