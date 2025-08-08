"""Metadata schemas for enhanced task tracking"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class ReviewDecision(str, Enum):
    """Review decision options"""
    APPROVED = "approved"
    NEEDS_FIXES = "needs_fixes"
    STOP_WORK = "stop_work"


class TaskMetadata(BaseModel):
    """Complete metadata schema for tasks"""
    
    # Hierarchy
    parent_task_id: Optional[int] = Field(None, description="Parent task for subtasks")
    phase: Optional[str] = Field(None, description="Project phase this task belongs to")
    
    # Dependencies (temporary until native support)
    depends_on: List[int] = Field(default_factory=list, description="Task IDs this depends on")
    blocks: List[int] = Field(default_factory=list, description="Task IDs blocked by this")
    
    # File ownership
    exclusive_files: List[str] = Field(default_factory=list, description="Files exclusively owned")
    shared_files: List[str] = Field(default_factory=list, description="Files that can be shared")
    
    # Parallelization
    parallel_group: Optional[str] = Field(None, description="Group name for parallel execution")
    can_parallelize: bool = Field(True, description="Whether task can run in parallel")
    max_parallel: int = Field(4, description="Max parallel tasks of this type")
    exclusive_resources: List[str] = Field(default_factory=list, description="Resources that block parallelization")
    
    # Review workflow
    workflow_type: str = Field("executor", description="Type: executor, reviewer, tester")
    review_required: bool = Field(False, description="Whether review is required")
    reviewer_assigned: Optional[str] = Field(None, description="Assigned reviewer agent ID")
    review_task_id: Optional[int] = Field(None, description="Associated review task ID")
    
    # Completion tracking
    completion_file: Optional[str] = Field(None, description="Path to job_done file")
    completion_readers: List[str] = Field(default_factory=list, description="Agents who read the file")
    required_readers: List[str] = Field(default_factory=list, description="Agents who must read")
    completion_time: Optional[datetime] = Field(None, description="When task was completed")
    
    # Time tracking
    estimated_hours: Optional[float] = Field(None, description="Estimated hours to complete")
    actual_hours: Optional[float] = Field(None, description="Actual hours spent")
    
    # Blocking and issues
    blocker_reason: Optional[str] = Field(None, description="Why task is blocked")
    blocked_since: Optional[datetime] = Field(None, description="When task was blocked")
    challenge_id: Optional[int] = Field(None, description="Associated challenge document")
    
    # Agent matching
    required_capabilities: List[str] = Field(default_factory=list, description="Required agent capabilities")
    preferred_agent_type: Optional[str] = Field(None, description="Preferred agent type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "parent_task_id": 1,
                "phase": "implementation",
                "depends_on": [2, 3],
                "exclusive_files": ["src/main.py", "tests/test_main.py"],
                "parallel_group": "backend",
                "review_required": True,
                "estimated_hours": 4.0
            }
        }


# Status transition rules
STATUS_TRANSITIONS = {
    "pending": ["assigned", "cancelled"],
    "assigned": ["in_progress", "cancelled"],
    "in_progress": ["needs_review", "blocked", "failed", "cancelled", "completed"],
    "needs_review": ["fixes_requested", "completed", "failed"],
    "fixes_requested": ["in_progress", "cancelled"],
    "blocked": ["in_progress", "cancelled"],
    "completed": [],  # Terminal state
    "failed": ["in_progress"],  # Can retry
    "cancelled": []  # Terminal state
}


def can_transition(from_status: str, to_status: str) -> bool:
    """Check if a status transition is valid"""
    allowed = STATUS_TRANSITIONS.get(from_status, [])
    return to_status in allowed


def get_terminal_states() -> List[str]:
    """Get list of terminal states"""
    return [status for status, transitions in STATUS_TRANSITIONS.items() if not transitions]


def get_active_states() -> List[str]:
    """Get list of active (non-terminal) states"""
    return ["assigned", "in_progress", "needs_review", "fixes_requested", "blocked"]