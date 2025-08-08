"""Artifact Service - Business logic for artifact management and compliance validation"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.dao.artifact_dao import ArtifactDAO
from src.dao.task_dao import TaskDAO
from src.models.artifact import (
    ArtifactCreate,
    ArtifactResponse,
    ComplianceValidation,
    ARTIFACT_TYPES
)


class ArtifactService:
    """Service layer for artifact management and compliance"""
    
    def __init__(self, session: AsyncSession):
        """Initialize artifact service
        
        Args:
            session: Database session
        """
        self.session = session
        self.dao = ArtifactDAO(session)
        self.task_dao = TaskDAO(session)
    
    async def upload_artifact(
        self,
        task_id: int,
        artifact_type: str,
        content: str,
        created_by: str
    ) -> ArtifactResponse:
        """Store artifact for a task
        
        Args:
            task_id: Task ID this artifact belongs to
            artifact_type: Type of artifact (tdd_red, tdd_green, etc.)
            content: Artifact content
            created_by: Agent that created this artifact
            
        Returns:
            Created artifact response
            
        Raises:
            ValueError: If artifact type is invalid or task not found
        """
        # Validate artifact type
        if artifact_type not in ARTIFACT_TYPES:
            raise ValueError(
                f"Invalid artifact type: {artifact_type}. "
                f"Valid types: {', '.join(ARTIFACT_TYPES)}"
            )
        
        # Create artifact
        artifact_data = ArtifactCreate(
            task_id=task_id,
            artifact_type=artifact_type,
            content=content,
            created_by=created_by
        )
        
        artifact = await self.dao.create_artifact(artifact_data)
        
        # Trigger compliance check if needed
        if artifact_type in ['tdd_green', 'review_feedback']:
            await self._check_compliance(task_id)
        
        return artifact
    
    async def get_artifacts(
        self,
        task_id: int,
        artifact_type: Optional[str] = None
    ) -> List[ArtifactResponse]:
        """Get artifacts for a task
        
        Args:
            task_id: Task ID
            artifact_type: Optional filter by type
            
        Returns:
            List of artifacts
        """
        return await self.dao.get_task_artifacts(task_id, artifact_type)
    
    async def validate_compliance(self, task_id: int) -> ComplianceValidation:
        """Check if task has all required artifacts
        
        Args:
            task_id: Task ID to validate
            
        Returns:
            Compliance validation result
        """
        # Get task to check status and type
        task = await self.task_dao.get_task(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        # Get all artifacts for the task
        artifacts = await self.dao.get_task_artifacts(task_id)
        artifact_types = [a.artifact_type for a in artifacts]
        
        # Determine requirements based on task status and creator type
        requirements = self._get_requirements_for_status(
            task.status,
            getattr(task, 'created_by_agent_type', None)
        )
        
        # Check compliance
        missing = []
        present = []
        
        for req in requirements:
            if req in artifact_types:
                present.append(req)
            else:
                missing.append(req)
        
        return ComplianceValidation(
            compliant=len(missing) == 0,
            missing=missing,
            present=present,
            task_id=task_id,
            task_status=task.status
        )
    
    def _get_requirements_for_status(
        self,
        status: str,
        created_by_agent_type: Optional[str] = None
    ) -> List[str]:
        """Get required artifacts for a task status
        
        Args:
            status: Task status
            created_by_agent_type: Type of agent that created the task
            
        Returns:
            List of required artifact types
        """
        requirements = []
        
        # Executor tasks moving to review need TDD artifacts
        if status == 'needs_review' and created_by_agent_type == 'executor':
            requirements.extend(['tdd_red', 'tdd_green'])
        
        # Tasks being approved need review feedback
        elif status == 'approved':
            requirements.append('review_feedback')
        
        # Completed tasks should have test results
        elif status == 'completed':
            requirements.append('test_results')
            if created_by_agent_type == 'executor':
                requirements.extend(['tdd_red', 'tdd_green'])
        
        # Tasks ready for release need all artifacts
        elif status == 'ready_for_release':
            requirements.extend([
                'tdd_red',
                'tdd_green',
                'review_feedback',
                'test_results',
                'completion_report'
            ])
        
        return requirements
    
    async def _check_compliance(self, task_id: int) -> None:
        """Internal method to check and log compliance
        
        Args:
            task_id: Task ID to check
        """
        try:
            validation = await self.validate_compliance(task_id)
            if not validation.compliant:
                # Log missing artifacts (in production, this would be logged properly)
                print(f"Task {task_id} missing artifacts: {validation.missing}")
        except Exception as e:
            # Log error (in production, use proper logging)
            print(f"Compliance check failed for task {task_id}: {e}")
    
    async def has_tdd_artifacts(self, task_id: int) -> bool:
        """Check if task has both TDD artifacts
        
        Args:
            task_id: Task ID to check
            
        Returns:
            True if both TDD artifacts exist
        """
        has_red = await self.dao.has_artifact_type(task_id, 'tdd_red')
        has_green = await self.dao.has_artifact_type(task_id, 'tdd_green')
        return has_red and has_green
    
    async def has_review_artifact(self, task_id: int) -> bool:
        """Check if task has review feedback artifact
        
        Args:
            task_id: Task ID to check
            
        Returns:
            True if review artifact exists
        """
        return await self.dao.has_artifact_type(task_id, 'review_feedback')
    
    async def get_latest_artifact(
        self,
        task_id: int,
        artifact_type: str
    ) -> Optional[ArtifactResponse]:
        """Get the latest artifact of a specific type for a task
        
        Args:
            task_id: Task ID
            artifact_type: Type of artifact
            
        Returns:
            Latest artifact if found
        """
        artifacts = await self.dao.get_task_artifacts(task_id, artifact_type)
        if artifacts:
            return artifacts[-1]  # Already sorted by created_at
        return None