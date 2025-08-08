"""Task models for validation and serialization"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class TaskStatus(str, Enum):
    """Task execution status - enforces quality gate workflow"""
    PENDING = "pending"                 # Task created, awaiting assignment
    ASSIGNED = "assigned"                # Assigned to agent, not started
    IN_PROGRESS = "in_progress"         # Agent actively working
    NEEDS_REVIEW = "needs_review"       # Work complete, awaiting review
    APPROVED = "approved"                # Review passed, ready for next stage
    NEEDS_FIXES = "needs_fixes"         # Review failed, requires changes
    COMPLETED = "completed"             # All reviews passed, work finalized
    FAILED = "failed"                   # Task failed during execution
    CANCELLED = "cancelled"              # Task cancelled
    MERGED = "merged"                   # Code integrated into target branch
    AUDITED = "audited"                 # Compliance verified by release-gate-auditor
    READY_FOR_RELEASE = "ready_for_release"  # All gates passed, deployable


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCreate(BaseModel):
    """Model for creating a new task"""
    name: str = Field(..., min_length=1, max_length=255, description="Task name", alias="title")
    description: str = Field(..., min_length=1, description="Task description")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this task depends on")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata", alias="meta_data")
    assigned_to: Optional[str] = Field(None, description="Agent ID assigned to this task", alias="agent_id")
    requires_documentation: bool = Field(False, description="Whether this task requires documentation")
    documentation_paths: List[str] = Field(default_factory=list, description="Paths to required documentation files")
    documentation_context: Optional[str] = Field(None, description="Context about documentation requirements")
    
    @field_validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Task name cannot be empty")
        if len(v) > 255:
            raise ValueError("Task name cannot exceed 255 characters")
        return v.strip()
    
    @field_validator("priority", mode="before")
    def validate_priority(cls, v):
        if isinstance(v, str) and v not in [p.value for p in TaskPriority]:
            raise ValueError(f"Invalid priority: {v}")
        return v
    
    model_config = ConfigDict(
        populate_by_name=True,  # Allow both field names and aliases
        json_schema_extra={
            "example": {
                "name": "Process Data",
                "description": "Process incoming data from API",
                "priority": "high",
                "dependencies": ["task-123", "task-456"],
                "metadata": {"source": "api", "batch_size": 1000}
            }
        }
    )


class TaskUpdate(BaseModel):
    """Model for updating task status and progress"""
    status: Optional[TaskStatus] = Field(None, description="New task status")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Task progress percentage")
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution result")
    error: Optional[str] = Field(None, description="Error message if task failed")
    assigned_to: Optional[str] = Field(None, description="Reassign task to different agent")
    
    @field_validator("progress")
    def validate_progress(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Progress must be between 0 and 100")
        return v
    
    @model_validator(mode="after")
    def validate_status_progress(self):
        # If marking as completed, progress should be 100
        if self.status == TaskStatus.COMPLETED and self.progress is not None and self.progress != 100:
            self.progress = 100
            
        # If marking as failed/cancelled, result should be None
        if self.status in [TaskStatus.FAILED, TaskStatus.CANCELLED]:
            self.result = None
            
        return self
    
    model_config = ConfigDict(
        populate_by_name=True,  # Allow both field names and aliases
        json_schema_extra={
            "example": {
                "status": "in_progress",
                "progress": 50,
                "result": {"processed": 500, "total": 1000}
            }
        }
    )


class TaskResponse(BaseModel):
    """Model for task responses"""
    id: str = Field(..., description="Task unique identifier")
    name: str = Field(..., description="Task name", alias="title")
    description: str = Field(..., description="Task description")
    status: TaskStatus = Field(..., description="Current task status")
    priority: TaskPriority = Field(..., description="Task priority")
    progress: int = Field(0, description="Task progress percentage")
    
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    dependents: List[str] = Field(default_factory=list, description="Tasks that depend on this one")
    
    assigned_to: Optional[str] = Field(None, description="Assigned agent ID", alias="agent_id")
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution result")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Task metadata", alias="meta_data")
    requires_documentation: bool = Field(False, description="Whether this task requires documentation")
    documentation_paths: List[str] = Field(default_factory=list, description="Paths to required documentation files")
    documentation_context: Optional[str] = Field(None, description="Context about documentation requirements")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Allow both field names and aliases
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Process Data",
                "description": "Process incoming data from API",
                "status": "completed",
                "priority": "high",
                "progress": 100,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T01:00:00Z",
                "started_at": "2024-01-01T00:15:00Z",
                "completed_at": "2024-01-01T01:00:00Z",
                "dependencies": ["task-123"],
                "assigned_to": "agent-001",
                "result": {"processed": 1000, "duration_seconds": 2700}
            }
        }
    )