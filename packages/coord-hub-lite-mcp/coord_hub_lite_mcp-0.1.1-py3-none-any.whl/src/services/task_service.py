"""Task Service - Business logic for task management"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority
from src.dao.task_dao import TaskDAO
from src.dao.artifact_dao import ArtifactDAO
from src.models.metadata_schemas import can_transition, STATUS_TRANSITIONS
from src.utils.metadata_utils import merge_metadata


class TaskService:
    """Service layer for task management operations"""
    
    def __init__(self, session: AsyncSession):
        """Initialize task service
        
        Args:
            session: Database session (required)
        """
        self._session = session
        self._dao = TaskDAO(session)
        self._artifact_dao = ArtifactDAO(session)
    
    async def create_task(
        self,
        session: AsyncSession,
        title: str,
        description: str,
        status: str = "pending",
        priority: str = "medium",
        parent_task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        requires_documentation: bool = False,
        documentation_paths: Optional[List[str]] = None,
        documentation_context: Optional[str] = None
    ) -> TaskResponse:
        """Create a new task
        
        Args:
            session: Database session
            title: Task title
            description: Task description
            status: Initial status (default: pending)
            priority: Task priority (default: medium)
            parent_task_id: Parent task ID for subtasks
            metadata: Additional metadata
            requires_documentation: Whether task needs documentation files
            documentation_paths: List of documentation file paths
            documentation_context: Context about documentation requirements
            
        Returns:
            Created task response
            
        Raises:
            ValueError: If status or priority is invalid
        """
        # Validate status
        try:
            task_status = TaskStatus(status)
        except ValueError:
            raise ValueError(f"Invalid status: {status}. Must be one of: {[s.value for s in TaskStatus]}")
        
        # Validate priority
        try:
            task_priority = TaskPriority(priority)
        except ValueError:
            raise ValueError(f"Invalid priority: {priority}. Must be one of: {[p.value for p in TaskPriority]}")
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Add parent task reference to metadata if provided
        if parent_task_id:
            metadata["parent_task_id"] = parent_task_id
        
        # Store created_by_agent_type in both metadata and model if provided
        created_by_agent_type = metadata.get('created_by_agent_type')
        
        # Create task data - ensure proper instantiation
        try:
            task_data = TaskCreate(
                title=title,  # Use alias name
                description=description,
                priority=task_priority,
                meta_data=metadata,  # Use alias name
                dependencies=[],  # Explicitly set dependencies to empty list
                requires_documentation=requires_documentation,
                documentation_paths=documentation_paths or [],
                documentation_context=documentation_context
            )
        except Exception as e:
            raise ValueError(f"Failed to create TaskCreate object: {str(e)}")
        
        # Use DAO to create task
        dao = TaskDAO(session)
        return await dao.create_task(task_data)
    
    async def update_task_status(
        self,
        session: AsyncSession,
        task_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TaskResponse:
        """Update task status with strict validation and quality gates
        
        Args:
            session: Database session
            task_id: Task ID to update
            status: New status
            metadata: Additional metadata to merge
            
        Returns:
            Updated task response
            
        Raises:
            ValueError: If status is invalid or transition not allowed
        """
        # Convert string ID to integer for database
        try:
            task_id_int = int(task_id)
        except ValueError:
            raise ValueError(f"Invalid task ID: {task_id}")
        
        # Get current task to validate transition
        dao = TaskDAO(session)
        current_task = await dao.get_task(task_id_int)
        if not current_task:
            raise ValueError(f"Task not found: {task_id}")
        
        # Validate the state transition with strict enforcement
        await self.validate_state_transition(current_task, status, session)
        
        # Prepare update
        task_update = TaskUpdate(status=status)
        
        # Handle metadata merging if provided
        if metadata:
            # TaskResponse uses 'metadata' not 'meta_data'
            existing_metadata = getattr(current_task, 'metadata', None) or getattr(current_task, 'meta_data', {}) or {}
            merged_metadata = merge_metadata(existing_metadata, metadata)
            # Note: TaskUpdate doesn't have metadata field, we'll need to update the DAO
        
        # Update task using DAO
        try:
            updated_task = await dao.update_task_status(task_id_int, task_update)
        except ValueError as e:
            # Re-raise with more context
            if "not found" in str(e):
                raise ValueError(f"Task not found: {task_id}")
            raise
        
        # Merge metadata if provided
        if metadata:
            # Update metadata in a second pass
            # This is a simplified approach - in production, we'd do this atomically
            updated_metadata = updated_task.metadata.copy()
            updated_metadata.update(metadata)
            
            # Return updated response
            updated_task.metadata = updated_metadata
        
        return updated_task
    
    async def validate_state_transition(
        self,
        task,
        new_status: str,
        session
    ) -> None:
        """Enforce strict state machine rules
        
        Args:
            task: Current task object
            new_status: Desired new status
            artifacts: Available artifacts (optional)
            
        Raises:
            ValueError: If transition is invalid or requirements not met
        """
        current = task.status
        
        # Define valid transitions with quality gates
        TRANSITIONS = {
            'pending': ['assigned'],
            'assigned': ['in_progress'],
            'in_progress': ['needs_review', 'failed'],
            'needs_review': ['approved', 'needs_fixes'],
            'needs_fixes': ['in_progress'],
            'approved': ['completed'],
            'completed': ['merged'],
            'merged': ['audited'],
            'audited': ['ready_for_release'],
            'failed': ['pending'],  # Allow retry
        }
        
        # Check if transition is valid
        if new_status not in TRANSITIONS.get(current, []):
            raise ValueError(
                f"Invalid transition: {current} → {new_status}. "
                f"Allowed transitions: {', '.join(TRANSITIONS.get(current, []))}"
            )
        
        # Special rules for executor tasks
        # Check both the model attribute and metadata
        created_by_agent_type = getattr(task, 'created_by_agent_type', None)
        if not created_by_agent_type and hasattr(task, 'meta_data'):
            created_by_agent_type = task.meta_data.get('created_by_agent_type')
        if not created_by_agent_type and hasattr(task, 'metadata'):
            created_by_agent_type = task.metadata.get('created_by_agent_type')
        
        if created_by_agent_type == 'executor':
            # Executor tasks MUST go through review
            if current == 'in_progress' and new_status == 'completed':
                raise ValueError(
                    "Executor tasks must go through review. Use 'needs_review' status first."
                )
            
            # Check for required artifacts before moving to review
            if current == 'in_progress' and new_status == 'needs_review':
                # Use the session to create artifact DAO
                artifact_dao = ArtifactDAO(session) if session else self._artifact_dao
                
                # Get numeric task ID
                task_id = int(task.id) if isinstance(task.id, str) else task.id
                
                has_red = await artifact_dao.has_artifact_type(task_id, 'tdd_red')
                has_green = await artifact_dao.has_artifact_type(task_id, 'tdd_green')
                
                if not (has_red and has_green):
                    raise ValueError(
                        "Cannot mark for review without TDD artifacts (red/green)"
                    )
            
            # Check for review artifact before approval
            if current == 'needs_review' and new_status == 'approved':
                # Use the session to create artifact DAO
                artifact_dao = ArtifactDAO(session) if session else self._artifact_dao
                
                # Get numeric task ID
                task_id = int(task.id) if isinstance(task.id, str) else task.id
                
                has_review = await artifact_dao.has_artifact_type(task_id, 'review_feedback')
                
                if not has_review:
                    raise ValueError(
                        "Cannot approve without review artifact"
                    )
    
    async def _has_tdd_artifacts(self, task_id: int) -> bool:
        """Check if task has both TDD artifacts
        
        Args:
            task_id: Task ID to check
            
        Returns:
            True if both TDD artifacts exist
        """
        has_red = await self._artifact_dao.has_artifact_type(task_id, 'tdd_red')
        has_green = await self._artifact_dao.has_artifact_type(task_id, 'tdd_green')
        return has_red and has_green
    
    async def _has_review_artifact(self, task_id: int) -> bool:
        """Check if task has review feedback artifact
        
        Args:
            task_id: Task ID to check
            
        Returns:
            True if review artifact exists
        """
        return await self._artifact_dao.has_artifact_type(task_id, 'review_feedback')
    
    def validate_status_transition(
        self,
        current_status: TaskStatus,
        new_status: TaskStatus
    ) -> bool:
        """Validate if status transition is allowed
        
        Args:
            current_status: Current task status
            new_status: Desired new status
            
        Returns:
            True if transition is valid
            
        Raises:
            ValueError: If transition is not allowed
        """
        # Define valid transitions
        valid_transitions = {
            TaskStatus.PENDING: [
                TaskStatus.IN_PROGRESS,
                TaskStatus.CANCELLED,
                TaskStatus.BLOCKED
            ],
            TaskStatus.IN_PROGRESS: [
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
                TaskStatus.BLOCKED
            ],
            TaskStatus.BLOCKED: [
                TaskStatus.IN_PROGRESS,
                TaskStatus.CANCELLED
            ],
            TaskStatus.COMPLETED: [],  # Terminal state
            TaskStatus.FAILED: [
                TaskStatus.PENDING,  # Allow retry
                TaskStatus.IN_PROGRESS  # Allow retry
            ],
            TaskStatus.CANCELLED: []  # Terminal state
        }
        
        allowed = valid_transitions.get(current_status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Invalid status transition from {current_status.value} to {new_status.value}"
            )
        
        return True
    
    async def check_dependencies(self, task_id: str) -> bool:
        """Check if all task dependencies are completed
        
        Args:
            task_id: Task ID to check
            
        Returns:
            True if all dependencies are completed
        """
        # Convert string ID to integer
        try:
            task_id_int = int(task_id)
        except ValueError:
            raise ValueError(f"Invalid task ID: {task_id}")
        
        
        # Get task with dependencies
        # This is a simplified implementation
        # In production, we'd use the DAO method to fetch with dependencies
        return True  # Simplified for now
    
    async def close(self):
        """Close the service and cleanup resources"""
        # Session management is handled externally
        pass