"""Agent models for validation and serialization"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID
import re

from pydantic import BaseModel, Field, field_validator, ConfigDict


class AgentStatus(str, Enum):
    """Agent availability status"""
    ACTIVE = "active"  # Maps to available in API logic
    INACTIVE = "inactive"  # Maps to offline in API logic  
    BUSY = "busy"
    ERROR = "error"


class AgentCapability(str, Enum):
    """Agent capabilities/roles"""
    EXECUTOR = "executor"
    REVIEWER = "reviewer" 
    TESTER = "tester"
    ARCHITECT = "architect"
    DATA_REVIEWER = "data_reviewer"


class AgentRegister(BaseModel):
    """Model for registering a new agent"""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional agent metadata", alias="meta_data")
    
    @field_validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Agent name cannot be empty")
        # Name must match pattern: lowercase letters, numbers, hyphens
        pattern = r'^[a-z0-9\-]+$'
        if not re.match(pattern, v):
            raise ValueError(f"Agent name must match pattern {pattern}")
        return v.strip()
    
    @field_validator("capabilities")
    def validate_capabilities(cls, v):
        if not v:
            raise ValueError("Agent must have at least one capability")
        # Remove duplicates
        return list(set(v))
    
    def to_db_capabilities(self) -> Dict[str, Any]:
        """Convert capabilities list to database format"""
        return {"roles": [cap.value for cap in self.capabilities]}
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "executor-001",
                "capabilities": ["executor"],
                "metadata": {"version": "1.0", "host": "worker-1"}
            }
        }
    )


class AgentUpdate(BaseModel):
    """Model for updating agent status"""
    status: Optional[AgentStatus] = Field(None, description="New agent status")
    current_task: Optional[str] = Field(None, description="Current task ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    
    @field_validator("current_task")
    def validate_task_assignment(cls, v, info):
        status = info.data.get("status") if info.data else None
        # If setting to busy, must have a task
        if status == AgentStatus.BUSY and not v:
            raise ValueError("Cannot set status to BUSY without a current task")
        # If setting to active, should not have a task
        if status == AgentStatus.ACTIVE and v:
            raise ValueError("Cannot have a current task when status is ACTIVE")
        return v
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "status": "busy",
                "current_task": "task-123",
                "metadata": {"load": 0.8}
            }
        }
    )


class AgentResponse(BaseModel):
    """Model for agent responses"""
    id: str = Field(..., description="Agent unique identifier")
    name: str = Field(..., description="Agent name")
    type: str = Field(..., description="Agent type")
    status: AgentStatus = Field(..., description="Current agent status")
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")
    
    created_at: datetime = Field(..., description="Agent registration timestamp")
    last_heartbeat: datetime = Field(..., description="Last heartbeat timestamp")
    
    current_task: Optional[str] = Field(None, description="Current task ID if busy")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    failed_tasks: int = Field(0, description="Number of failed tasks")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Agent metadata", alias="meta_data")
    
    @property
    def success_rate(self) -> float:
        """Calculate agent success rate"""
        total = self.completed_tasks + self.failed_tasks
        if total == 0:
            return 100.0
        return (self.completed_tasks / total) * 100.0
    
    @property
    def is_available(self) -> bool:
        """Check if agent is available for work"""
        return self.status == AgentStatus.ACTIVE
    
    @classmethod
    def from_db_capabilities(cls, db_capabilities: Dict[str, Any]) -> List[AgentCapability]:
        """Convert database capabilities format to Pydantic format"""
        roles = db_capabilities.get("roles", [])
        return [AgentCapability(role) for role in roles if role in [cap.value for cap in AgentCapability]]
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "executor-001",
                "type": "executor",
                "status": "active",
                "capabilities": ["executor"],
                "created_at": "2024-01-01T00:00:00Z",
                "last_heartbeat": "2024-01-01T12:00:00Z",
                "current_task": None,
                "completed_tasks": 42,
                "failed_tasks": 3,
                "metadata": {"version": "1.0", "host": "worker-1"}
            }
        }
    )