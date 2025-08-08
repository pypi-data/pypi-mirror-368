"""Artifact models for task artifacts management"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ArtifactBase(BaseModel):
    """Base model for artifacts"""
    task_id: int = Field(..., description="Task ID this artifact belongs to")
    artifact_type: str = Field(..., description="Type of artifact (tdd_red, tdd_green, etc.)")
    content: str = Field(..., description="Artifact content (can be JSON string)")
    created_by: Optional[str] = Field(None, description="Agent that created this artifact")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "task_id": 1,
                "artifact_type": "tdd_red",
                "content": "FAILED test_feature.py::test_behavior - AssertionError",
                "created_by": "executor-001"
            }
        }
    )


class ArtifactCreate(ArtifactBase):
    """Model for creating a new artifact"""
    pass


class ArtifactResponse(ArtifactBase):
    """Response model for artifacts"""
    id: int = Field(..., description="Artifact ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "task_id": 1,
                "artifact_type": "tdd_green",
                "content": "PASSED test_feature.py::test_behavior",
                "created_by": "executor-001",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }
    )


class ComplianceValidation(BaseModel):
    """Model for compliance validation results"""
    compliant: bool = Field(..., description="Whether task is compliant with requirements")
    missing: list[str] = Field(default_factory=list, description="Missing required artifacts")
    present: list[str] = Field(default_factory=list, description="Present artifacts")
    task_id: int = Field(..., description="Task ID that was validated")
    task_status: str = Field(..., description="Current task status")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "compliant": False,
                "missing": ["tdd_red", "tdd_green"],
                "present": ["review_feedback"],
                "task_id": 1,
                "task_status": "needs_review"
            }
        }
    )


# Valid artifact types
ARTIFACT_TYPES = [
    'tdd_red',           # TDD failing test output
    'tdd_green',         # TDD passing test output
    'review_feedback',   # Code review feedback (JSON)
    'test_results',      # Test execution results
    'console_logs',      # Browser console logs from integration tests
    'completion_report', # Agent completion report
    'integration_test'   # Integration test results
]


def validate_artifact_type(artifact_type: str) -> bool:
    """Validate if artifact type is valid
    
    Args:
        artifact_type: Type to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If type is invalid
    """
    if artifact_type not in ARTIFACT_TYPES:
        raise ValueError(
            f"Invalid artifact type: {artifact_type}. "
            f"Must be one of: {', '.join(ARTIFACT_TYPES)}"
        )
    return True