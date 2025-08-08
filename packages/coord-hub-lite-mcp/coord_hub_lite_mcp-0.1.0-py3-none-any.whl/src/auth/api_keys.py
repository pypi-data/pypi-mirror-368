"""API key and JWT token management for authentication."""

import hashlib
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
import jwt


class APIKeyManager:
    """Manages API keys for agent authentication."""
    
    def __init__(self):
        """Initialize API key manager."""
        self._keys: Dict[str, Dict[str, Any]] = {}
        self._key_by_hash: Dict[str, str] = {}
        self._rate_limits: Dict[str, Dict[str, Any]] = {}
        
    def generate_api_key(self) -> str:
        """Generate a new API key.
        
        Returns:
            32-character hex string API key
        """
        return secrets.token_hex(16)
        
    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for secure storage.
        
        Args:
            api_key: The API key to hash
            
        Returns:
            SHA256 hash of the API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
        
    async def create_api_key(
        self,
        agent_id: str,
        role: str,
        capabilities: Optional[List[str]] = None,
        rate_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new API key for an agent.
        
        Args:
            agent_id: ID of the agent
            role: Role of the agent (agent, admin, etc.)
            capabilities: List of capabilities for the agent
            rate_limit: Max requests per minute (None for unlimited)
            
        Returns:
            Dictionary containing api_key, key_id, and metadata
        """
        api_key = self.generate_api_key()
        key_id = f"key_{secrets.token_hex(8)}"
        hashed_key = self.hash_api_key(api_key)
        
        key_data = {
            "key_id": key_id,
            "agent_id": agent_id,
            "role": role,
            "capabilities": capabilities or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "revoked": False,
            "rate_limit": rate_limit
        }
        
        self._keys[key_id] = key_data
        self._key_by_hash[hashed_key] = key_id
        
        if rate_limit:
            self._rate_limits[key_id] = {
                "limit": rate_limit,
                "window_start": time.time(),
                "requests": 0
            }
        
        return {
            "api_key": api_key,
            "key_id": key_id,
            "agent_id": agent_id,
            "role": role,
            "capabilities": capabilities or []
        }
        
    async def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Validate an API key.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Dictionary with validation result and metadata
        """
        hashed_key = self.hash_api_key(api_key)
        
        if hashed_key not in self._key_by_hash:
            return {"valid": False, "error": "Invalid API key"}
            
        key_id = self._key_by_hash[hashed_key]
        key_data = self._keys[key_id]
        
        if key_data["revoked"]:
            return {"valid": False, "error": "API key has been revoked"}
            
        return {
            "valid": True,
            "key_id": key_id,
            "agent_id": key_data["agent_id"],
            "role": key_data["role"],
            "capabilities": key_data["capabilities"]
        }
        
    async def revoke_api_key(self, key_id: str) -> None:
        """Revoke an API key.
        
        Args:
            key_id: ID of the key to revoke
        """
        if key_id in self._keys:
            self._keys[key_id]["revoked"] = True
            
    async def check_rate_limit(self, key_id: str) -> Dict[str, Any]:
        """Check if a key has exceeded its rate limit.
        
        Args:
            key_id: ID of the key to check
            
        Returns:
            Dictionary with allowed status and retry_after if limited
        """
        if key_id not in self._rate_limits:
            return {"allowed": True}
            
        rate_data = self._rate_limits[key_id]
        current_time = time.time()
        window_duration = 60  # 1 minute window
        
        # Reset window if needed
        if current_time - rate_data["window_start"] >= window_duration:
            rate_data["window_start"] = current_time
            rate_data["requests"] = 0
            
        # Check if under limit
        if rate_data["requests"] < rate_data["limit"]:
            rate_data["requests"] += 1
            return {"allowed": True}
            
        # Calculate retry after
        retry_after = window_duration - (current_time - rate_data["window_start"])
        return {
            "allowed": False,
            "retry_after": int(retry_after)
        }


class JWTTokenManager:
    """Manages JWT tokens for authentication."""
    
    def __init__(self, secret_key: str):
        """Initialize JWT token manager.
        
        Args:
            secret_key: Secret key for signing tokens
        """
        self.secret_key = secret_key
        self.algorithm = "HS256"
        
    def generate_token(
        self,
        payload: Dict[str, Any],
        expiration_minutes: int = 30
    ) -> str:
        """Generate a JWT token.
        
        Args:
            payload: Data to encode in the token
            expiration_minutes: Token expiration time in minutes
            
        Returns:
            Encoded JWT token
        """
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=expiration_minutes)
        
        token_payload = {
            **payload,
            "iat": now,
            "exp": exp
        }
        
        return jwt.encode(
            token_payload,
            self.secret_key,
            algorithm=self.algorithm
        )
        
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token payload
            
        Raises:
            jwt.ExpiredSignatureError: If token is expired
            jwt.InvalidTokenError: If token is invalid
        """
        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm]
        )