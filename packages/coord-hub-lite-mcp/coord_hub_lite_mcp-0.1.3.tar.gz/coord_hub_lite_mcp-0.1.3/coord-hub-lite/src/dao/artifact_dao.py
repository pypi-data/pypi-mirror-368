"""Data Access Object for TaskArtifact operations"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from src.database.models import TaskArtifact, Task
from src.models.artifact import (
    ArtifactCreate, 
    ArtifactResponse,
    validate_artifact_type
)


class ArtifactDAO:
    """Data Access Object for artifact operations"""
    
    def __init__(self, session: AsyncSession):
        """Initialize ArtifactDAO
        
        Args:
            session: AsyncSession instance
        """
        self.session = session
    
    async def create_artifact(
        self,
        artifact_data: ArtifactCreate
    ) -> ArtifactResponse:
        """Create a new artifact
        
        Args:
            artifact_data: Artifact creation data
            
        Returns:
            Created artifact response
            
        Raises:
            ValueError: If artifact type is invalid or task not found
        """
        # Validate artifact type
        validate_artifact_type(artifact_data.artifact_type)
        
        # Verify task exists
        task = await self.session.get(Task, artifact_data.task_id)
        if not task:
            raise ValueError(f"Task not found: {artifact_data.task_id}")
        
        # Create artifact
        artifact = TaskArtifact(
            task_id=artifact_data.task_id,
            artifact_type=artifact_data.artifact_type,
            content=artifact_data.content,
            created_by=artifact_data.created_by
        )
        
        self.session.add(artifact)
        await self.session.commit()
        await self.session.refresh(artifact)
        
        return ArtifactResponse.model_validate(artifact)
    
    async def get_artifact(self, artifact_id: int) -> Optional[ArtifactResponse]:
        """Get an artifact by ID
        
        Args:
            artifact_id: Artifact ID
            
        Returns:
            Artifact if found, None otherwise
        """
        artifact = await self.session.get(TaskArtifact, artifact_id)
        if artifact:
            return ArtifactResponse.model_validate(artifact)
        return None
    
    async def get_task_artifacts(
        self,
        task_id: int,
        artifact_type: Optional[str] = None
    ) -> List[ArtifactResponse]:
        """Get all artifacts for a task
        
        Args:
            task_id: Task ID
            artifact_type: Optional filter by type
            
        Returns:
            List of artifacts
        """
        query = select(TaskArtifact).where(TaskArtifact.task_id == task_id)
        
        if artifact_type:
            validate_artifact_type(artifact_type)
            query = query.where(TaskArtifact.artifact_type == artifact_type)
        
        query = query.order_by(TaskArtifact.created_at)
        
        result = await self.session.execute(query)
        artifacts = result.scalars().all()
        
        return [ArtifactResponse.model_validate(a) for a in artifacts]
    
    async def has_artifact_type(
        self,
        task_id: int,
        artifact_type: str
    ) -> bool:
        """Check if a task has a specific artifact type
        
        Args:
            task_id: Task ID
            artifact_type: Artifact type to check
            
        Returns:
            True if artifact exists
        """
        validate_artifact_type(artifact_type)
        
        query = select(TaskArtifact.id).where(
            and_(
                TaskArtifact.task_id == task_id,
                TaskArtifact.artifact_type == artifact_type
            )
        ).limit(1)
        
        result = await self.session.execute(query)
        return result.scalar() is not None
    
    async def delete_artifact(self, artifact_id: int) -> bool:
        """Delete an artifact
        
        Args:
            artifact_id: Artifact ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        artifact = await self.session.get(TaskArtifact, artifact_id)
        if artifact:
            await self.session.delete(artifact)
            await self.session.commit()
            return True
        return False
    
    async def get_artifacts_by_type(
        self,
        artifact_type: str,
        limit: int = 100
    ) -> List[ArtifactResponse]:
        """Get artifacts by type across all tasks
        
        Args:
            artifact_type: Type of artifacts to fetch
            limit: Maximum number of results
            
        Returns:
            List of artifacts
        """
        validate_artifact_type(artifact_type)
        
        query = (
            select(TaskArtifact)
            .where(TaskArtifact.artifact_type == artifact_type)
            .order_by(TaskArtifact.created_at.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        artifacts = result.scalars().all()
        
        return [ArtifactResponse.model_validate(a) for a in artifacts]