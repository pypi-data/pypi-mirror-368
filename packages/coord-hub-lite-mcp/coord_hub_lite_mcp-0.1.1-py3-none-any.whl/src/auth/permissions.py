"""Role-based access control and permission management."""

from functools import wraps
from typing import Dict, List, Set, Optional, Callable, Any
import asyncio


class PermissionDeniedError(Exception):
    """Raised when permission is denied."""
    pass


class PermissionManager:
    """Manages roles, permissions, and agent capabilities."""
    
    def __init__(self):
        """Initialize permission manager."""
        self._roles: Dict[str, Set[str]] = {}
        self._agent_capabilities: Dict[str, Set[str]] = {}
        self._task_ownership: Dict[str, str] = {}
        
    def define_role(self, role: str, permissions: List[str]) -> None:
        """Define a role with its permissions.
        
        Args:
            role: Name of the role
            permissions: List of permission strings
        """
        self._roles[role] = set(permissions)
        
    def get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a role.
        
        Args:
            role: Name of the role
            
        Returns:
            List of permissions for the role
        """
        return list(self._roles.get(role, set()))
        
    def check_permission(self, role: str, permission: str) -> bool:
        """Check if a role has a specific permission.
        
        Args:
            role: Name of the role
            permission: Permission to check
            
        Returns:
            True if role has permission, False otherwise
        """
        if role not in self._roles:
            return False
            
        role_perms = self._roles[role]
        
        # Check for exact match
        if permission in role_perms:
            return True
            
        # Check for wildcard match
        if "*" in role_perms:
            return True
            
        # Check for partial wildcard (e.g., task.* matches task.read)
        perm_parts = permission.split(".")
        for i in range(len(perm_parts)):
            wildcard_perm = ".".join(perm_parts[:i+1]) + ".*"
            if wildcard_perm in role_perms:
                return True
                
        return False
        
    def set_agent_capabilities(
        self,
        agent_id: str,
        capabilities: List[str]
    ) -> None:
        """Set capabilities for a specific agent.
        
        Args:
            agent_id: ID of the agent
            capabilities: List of capability strings
        """
        self._agent_capabilities[agent_id] = set(capabilities)
        
    def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """Get capabilities for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of capabilities
        """
        return list(self._agent_capabilities.get(agent_id, set()))
        
    def agent_has_capability(
        self,
        agent_id: str,
        capability: str
    ) -> bool:
        """Check if an agent has a specific capability.
        
        Args:
            agent_id: ID of the agent
            capability: Capability to check
            
        Returns:
            True if agent has capability, False otherwise
        """
        return capability in self._agent_capabilities.get(agent_id, set())
        
    def assign_task_ownership(
        self,
        task_id: str,
        agent_id: str
    ) -> None:
        """Assign task ownership to an agent.
        
        Args:
            task_id: ID of the task
            agent_id: ID of the agent
        """
        self._task_ownership[task_id] = agent_id
        
    def validate_task_ownership(
        self,
        task_id: str,
        agent_id: str
    ) -> bool:
        """Validate if an agent owns a task.
        
        Args:
            task_id: ID of the task
            agent_id: ID of the agent
            
        Returns:
            True if agent owns the task, False otherwise
        """
        return self._task_ownership.get(task_id) == agent_id


def require_permission(permission: str) -> Callable:
    """Decorator to require a permission for a function.
    
    Args:
        permission: Required permission string
        
    Returns:
        Decorated function that checks permission
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(agent_context: Dict[str, Any], *args, **kwargs):
            """Check permission before executing function."""
            # Check if agent has the required permission
            permissions = agent_context.get("permissions", [])
            
            if permission not in permissions:
                # Also check for wildcard permissions
                has_permission = False
                for perm in permissions:
                    if perm == "*" or perm == permission:
                        has_permission = True
                        break
                    # Check partial wildcards
                    if perm.endswith(".*"):
                        perm_prefix = perm[:-2]
                        if permission.startswith(perm_prefix + "."):
                            has_permission = True
                            break
                            
                if not has_permission:
                    raise PermissionDeniedError(
                        f"Permission '{permission}' required"
                    )
                    
            # Call the original function
            if asyncio.iscoroutinefunction(func):
                return await func(agent_context, *args, **kwargs)
            else:
                return func(agent_context, *args, **kwargs)
                
        return wrapper
    return decorator