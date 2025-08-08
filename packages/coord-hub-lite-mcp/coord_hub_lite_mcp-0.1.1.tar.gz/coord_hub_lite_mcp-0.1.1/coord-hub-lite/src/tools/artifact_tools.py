"""MCP Tools for artifact management and compliance validation"""
from typing import Optional, Dict, Any, List
from src.database.session import get_async_session
from src.services.artifact_service import ArtifactService
from src.models.artifact import ArtifactCreate


async def upload_artifact(
    task_id: int,
    artifact_type: str,
    content: str,
    created_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload an artifact for a task (replaces markdown file outputs).
    This tool should be called by sub-agents to store their outputs.
    
    Args:
        task_id: The task this artifact belongs to
        artifact_type: Type of artifact ('tdd_red', 'tdd_green', 'review_feedback', etc.)
        content: The artifact content (can be plain text or JSON string)
        created_by: Optional identifier of the creating agent
    
    Returns:
        Confirmation of artifact storage with artifact details
    
    Example:
        >>> result = await upload_artifact(
        ...     task_id=123,
        ...     artifact_type="tdd_red",
        ...     content="FAILED test_feature.py::test_behavior - AssertionError",
        ...     created_by="executor-001"
        ... )
        >>> print(result)
        {'success': True, 'artifact_id': 1, 'message': 'Artifact uploaded'}
    """
    async with get_async_session() as session:
        service = ArtifactService(session)
        
        try:
            artifact = await service.upload_artifact(
                task_id=task_id,
                artifact_type=artifact_type,
                content=content,
                created_by=created_by or "unknown"
            )
            
            return {
                "success": True,
                "artifact_id": artifact.id,
                "task_id": artifact.task_id,
                "artifact_type": artifact.artifact_type,
                "message": f"Artifact '{artifact_type}' uploaded for task {task_id}"
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to upload artifact: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Unexpected error uploading artifact: {str(e)}"
            }


async def get_task_artifacts(
    task_id: int,
    artifact_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve artifacts for a task.
    
    Args:
        task_id: The task to get artifacts for
        artifact_type: Optional filter by type
    
    Returns:
        List of artifacts with their details
    
    Example:
        >>> artifacts = await get_task_artifacts(task_id=123)
        >>> for artifact in artifacts:
        ...     print(f"{artifact['type']}: {artifact['created_at']}")
    """
    async with get_async_session() as session:
        service = ArtifactService(session)
        
        try:
            artifacts = await service.get_artifacts(
                task_id=task_id,
                artifact_type=artifact_type
            )
            
            return [
                {
                    "id": a.id,
                    "type": a.artifact_type,
                    "content": a.content,
                    "created_by": a.created_by,
                    "created_at": a.created_at.isoformat() if a.created_at else None
                }
                for a in artifacts
            ]
        except Exception as e:
            return []


async def validate_compliance(task_id: int) -> Dict[str, Any]:
    """
    Check if a task has all required artifacts for its current status.
    
    Args:
        task_id: The task to validate
    
    Returns:
        Compliance status with details about missing/present artifacts
    
    Example:
        >>> result = await validate_compliance(task_id=123)
        >>> if not result['compliant']:
        ...     print(f"Missing artifacts: {result['missing']}")
    """
    async with get_async_session() as session:
        service = ArtifactService(session)
        
        try:
            result = await service.validate_compliance(task_id)
            
            return {
                "compliant": result.compliant,
                "missing": result.missing,
                "present": result.present,
                "task_id": result.task_id,
                "task_status": result.task_status,
                "message": "Task is compliant" if result.compliant else f"Missing artifacts: {', '.join(result.missing)}"
            }
        except ValueError as e:
            return {
                "compliant": False,
                "error": str(e),
                "message": f"Validation failed: {str(e)}"
            }
        except Exception as e:
            return {
                "compliant": False,
                "error": str(e),
                "message": f"Unexpected error during validation: {str(e)}"
            }


async def get_latest_artifact(
    task_id: int,
    artifact_type: str
) -> Optional[Dict[str, Any]]:
    """
    Get the latest artifact of a specific type for a task.
    
    Args:
        task_id: Task ID
        artifact_type: Type of artifact to retrieve
    
    Returns:
        Latest artifact if found, None otherwise
    
    Example:
        >>> latest_review = await get_latest_artifact(
        ...     task_id=123,
        ...     artifact_type="review_feedback"
        ... )
        >>> if latest_review:
        ...     print(latest_review['content'])
    """
    async with get_async_session() as session:
        service = ArtifactService(session)
        
        try:
            artifact = await service.get_latest_artifact(task_id, artifact_type)
            
            if artifact:
                return {
                    "id": artifact.id,
                    "type": artifact.artifact_type,
                    "content": artifact.content,
                    "created_by": artifact.created_by,
                    "created_at": artifact.created_at.isoformat() if artifact.created_at else None
                }
            return None
        except Exception:
            return None


# Tool registry for MCP server
ARTIFACT_TOOLS = {
    "upload_artifact": upload_artifact,
    "get_task_artifacts": get_task_artifacts,
    "validate_compliance": validate_compliance,
    "get_latest_artifact": get_latest_artifact
}