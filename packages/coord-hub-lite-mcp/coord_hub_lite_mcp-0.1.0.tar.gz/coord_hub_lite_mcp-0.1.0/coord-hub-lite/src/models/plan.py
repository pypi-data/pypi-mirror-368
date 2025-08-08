"""Plan models for validation and serialization"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID
import json

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class PlanStatus(str, Enum):
    """Plan execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class TaskDefinition(BaseModel):
    """Definition of a task within a plan"""
    id: str = Field(..., description="Task identifier within the plan")
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies by ID")
    priority: Optional[str] = Field("medium", description="Task priority")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Task metadata")


class PlanCreate(BaseModel):
    """Model for creating a new execution plan"""
    name: str = Field(..., min_length=1, max_length=255, description="Plan name")
    description: str = Field(..., min_length=1, description="Plan description")
    tasks: List[Dict[str, Any]] = Field(..., description="List of task definitions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional plan metadata")
    
    @field_validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Plan name cannot be empty")
        return v.strip()
    
    @field_validator("tasks")
    def validate_tasks(cls, v):
        if not v:
            raise ValueError("Plan must contain at least one task")
        
        # Check for duplicate task IDs
        task_ids = [task.get("id") for task in v]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Duplicate task ID found in plan")
        
        # Validate task structure
        for task in v:
            if not task.get("id"):
                raise ValueError("Task must have an ID")
            if not task.get("name"):
                raise ValueError(f"Task {task.get('id')} must have a name")
            if not task.get("description"):
                raise ValueError(f"Task {task.get('id')} must have a description")
            if "dependencies" not in task:
                task["dependencies"] = []
        
        return v
    
    @model_validator(mode="after")
    def validate_dependencies(self):
        task_ids = {task["id"] for task in self.tasks}
        
        # Check that all dependencies exist
        for task in self.tasks:
            for dep in task.get("dependencies", []):
                if dep not in task_ids:
                    raise ValueError(f"Task {task['id']} has dependency on non-existent task {dep}")
        
        return self
    
    def to_db_content(self) -> str:
        """Convert plan data to database content format"""
        content = {
            "description": self.description,
            "tasks": self.tasks,
            "metadata": self.metadata
        }
        return json.dumps(content)
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "Data Processing Pipeline",
                "description": "Process and analyze incoming data",
                "tasks": [
                    {
                        "id": "fetch-data",
                        "name": "Fetch Data",
                        "description": "Retrieve data from external API",
                        "dependencies": []
                    },
                    {
                        "id": "validate-data",
                        "name": "Validate Data",
                        "description": "Validate data format and integrity",
                        "dependencies": ["fetch-data"]
                    },
                    {
                        "id": "process-data",
                        "name": "Process Data",
                        "description": "Transform and enrich data",
                        "dependencies": ["validate-data"]
                    }
                ],
                "metadata": {"author": "system", "version": "1.0"}
            }
        }
    )


class PlanResponse(BaseModel):
    """Model for plan responses"""
    id: str = Field(..., description="Plan unique identifier")
    name: str = Field(..., description="Plan name")
    description: str = Field(..., description="Plan description")
    status: PlanStatus = Field(..., description="Current plan status")
    
    created_at: datetime = Field(..., description="Plan creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    started_at: Optional[datetime] = Field(None, description="Plan execution start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Plan completion timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Soft deletion timestamp")
    
    total_tasks: int = Field(..., description="Total number of tasks in plan")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    failed_tasks: int = Field(0, description="Number of failed tasks")
    
    task_tree: Dict[str, Any] = Field(..., description="Hierarchical task structure")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Plan metadata", alias="meta_data")
    
    @property
    def progress(self) -> float:
        """Calculate plan execution progress"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100.0
    
    @property
    def is_active(self) -> bool:
        """Check if plan is currently active"""
        return self.status == PlanStatus.ACTIVE
    
    @property
    def is_complete(self) -> bool:
        """Check if plan execution is complete"""
        return self.status in [PlanStatus.COMPLETED, PlanStatus.FAILED]
    
    @classmethod
    def from_db_content(cls, content: str) -> Dict[str, Any]:
        """Parse database content format to extract plan data"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"description": content, "tasks": [], "metadata": {}}
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "name": "Data Processing Pipeline",
                "description": "Process and analyze incoming data",
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T02:00:00Z",
                "started_at": "2024-01-01T00:30:00Z",
                "total_tasks": 10,
                "completed_tasks": 6,
                "failed_tasks": 1,
                "task_tree": {
                    "fetch-data": {
                        "name": "Fetch Data",
                        "status": "completed",
                        "children": ["validate-data"]
                    },
                    "validate-data": {
                        "name": "Validate Data",
                        "status": "completed",
                        "children": ["process-data"]
                    },
                    "process-data": {
                        "name": "Process Data",
                        "status": "in_progress",
                        "children": []
                    }
                },
                "metadata": {"author": "system", "version": "1.0"}
            }
        }
    )