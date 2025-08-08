"""MCP tools for handling task completion and triggering follow-up actions"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from fastmcp import Context
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Task as TaskModel
from src.database.session import get_async_session
from src.utils.metadata_utils import parse_metadata
from src.models.task import TaskStatus, TaskPriority
from src.services.task_service import TaskService


async def handle_task_completion(
    task_id: int,
    completion_summary: str,
    deliverables: Optional[List[str]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    context: Optional[Context] = None
) -> Dict:
    """
    Handle task completion and trigger follow-up actions.
    
    Args:
        task_id: Completed task
        completion_summary: Summary of what was accomplished
        deliverables: List of deliverable files/artifacts
        metrics: Performance metrics (lines added, tests passed, etc.)
        
    Returns:
        Result with follow-up actions triggered
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Update completion metadata
        metadata = parse_metadata(task.meta_data or {})
        metadata.completion_summary = completion_summary
        metadata.deliverables = deliverables or []
        metadata.completion_metrics = metrics or {}
        metadata.completed_at = datetime.now(timezone.utc).isoformat()
        
        # Calculate actual duration if started_at exists
        if task.started_at:
            duration = datetime.now(timezone.utc) - task.started_at
            metadata.actual_hours = duration.total_seconds() / 3600
        
        task.meta_data = metadata.dict()
        
        # Determine follow-up actions
        follow_up_actions = []
        
        # 1. Check if review is required
        if metadata.review_required and task.status != TaskStatus.COMPLETED.value:
            follow_up_actions.append({
                "action": "submit_for_review",
                "reason": "Task requires review before completion",
                "params": {
                    "task_id": task_id,
                    "review_type": metadata.review_type or "code_review",
                    "artifacts": deliverables
                }
            })
        
        # 2. Check for dependent tasks
        dependent_tasks = await get_tasks_blocked_by(session, task_id)
        if dependent_tasks:
            follow_up_actions.append({
                "action": "unblock_dependent_tasks",
                "reason": f"Task completion unblocks {len(dependent_tasks)} dependent tasks",
                "dependent_task_ids": [t.id for t in dependent_tasks]
            })
        
        # 3. Check if this completes a phase
        if metadata.phase:
            phase_complete = await check_phase_completion(session, metadata.phase, metadata.parent_task_id)
            if phase_complete:
                follow_up_actions.append({
                    "action": "phase_completed",
                    "phase": metadata.phase,
                    "project_id": metadata.parent_task_id
                })
        
        # 4. Release file ownership
        if metadata.exclusive_files:
            follow_up_actions.append({
                "action": "release_file_ownership",
                "files": metadata.exclusive_files,
                "task_id": task_id
            })
        
        # 5. Check for completion triggers
        if metadata.on_completion_trigger:
            follow_up_actions.append({
                "action": "execute_trigger",
                "trigger": metadata.on_completion_trigger,
                "params": metadata.trigger_params or {}
            })
        
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "completion_recorded": True,
            "follow_up_actions": follow_up_actions,
            "deliverables_count": len(deliverables or [])
        }


async def handle_task_failure(
    task_id: int,
    failure_reason: str,
    error_details: Optional[str] = None,
    can_retry: bool = True,
    context: Optional[Context] = None
) -> Dict:
    """
    Handle task failure and determine recovery actions.
    
    Args:
        task_id: Failed task
        failure_reason: Why the task failed
        error_details: Detailed error information
        can_retry: Whether task can be retried
        
    Returns:
        Result with recovery actions
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Update task status
        task.status = TaskStatus.FAILED.value
        
        # Update failure metadata
        metadata = parse_metadata(task.meta_data or {})
        metadata.failure_reason = failure_reason
        metadata.error_details = error_details
        metadata.failed_at = datetime.now(timezone.utc).isoformat()
        metadata.can_retry = can_retry
        
        # Increment failure count
        metadata.failure_count = getattr(metadata, 'failure_count', 0) + 1
        
        task.meta_data = metadata.dict()
        
        # Determine recovery actions
        recovery_actions = []
        
        # 1. Check if task can be retried
        if can_retry and metadata.failure_count < 3:
            recovery_actions.append({
                "action": "retry_task",
                "reason": f"Task can be retried (attempt {metadata.failure_count + 1}/3)",
                "wait_time": 60 * metadata.failure_count  # Exponential backoff
            })
        
        # 2. Check if escalation needed
        if metadata.failure_count >= 2 or not can_retry:
            recovery_actions.append({
                "action": "escalate_to_architect",
                "reason": "Multiple failures or non-retryable error",
                "failure_count": metadata.failure_count
            })
        
        # 3. Block dependent tasks
        dependent_tasks = await get_tasks_blocked_by(session, task_id)
        if dependent_tasks:
            recovery_actions.append({
                "action": "notify_blocked_tasks",
                "reason": f"Task failure blocks {len(dependent_tasks)} dependent tasks",
                "blocked_task_ids": [t.id for t in dependent_tasks]
            })
        
        # 4. Release partial file ownership
        if metadata.exclusive_files:
            recovery_actions.append({
                "action": "release_file_ownership",
                "files": metadata.exclusive_files,
                "reason": "Releasing files due to task failure"
            })
        
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "status": TaskStatus.FAILED.value,
            "failure_count": metadata.failure_count,
            "recovery_actions": recovery_actions
        }


async def check_project_completion(
    project_id: int,
    context: Optional[Context] = None
) -> Dict:
    """
    Check if all tasks in a project are complete.
    
    Args:
        project_id: Root project task ID
        
    Returns:
        Project completion status and summary
    """
    async with get_async_session() as session:
        # Get all tasks in project
        all_tasks = await get_project_tasks(session, project_id)
        
        if not all_tasks:
            return {"success": False, "error": "Project not found or has no tasks"}
        
        # Count task statuses
        status_counts = {}
        for task in all_tasks:
            status = task.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Check completion
        total_tasks = len(all_tasks)
        completed_tasks = status_counts.get(TaskStatus.COMPLETED.value, 0)
        failed_tasks = status_counts.get(TaskStatus.FAILED.value, 0)
        blocked_tasks = status_counts.get(TaskStatus.BLOCKED.value, 0)
        
        is_complete = (
            completed_tasks + failed_tasks == total_tasks or
            completed_tasks + failed_tasks + blocked_tasks == total_tasks
        )
        
        # Calculate metrics
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Get project task
        project_task = next((t for t in all_tasks if t.id == project_id), None)
        
        summary = {
            "project_id": project_id,
            "project_title": project_task.title if project_task else "Unknown",
            "is_complete": is_complete,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "blocked_tasks": blocked_tasks,
            "in_progress_tasks": status_counts.get(TaskStatus.IN_PROGRESS.value, 0),
            "pending_tasks": status_counts.get(TaskStatus.PENDING.value, 0),
            "completion_percentage": round(completion_percentage, 2),
            "status_breakdown": status_counts
        }
        
        # If complete, prepare completion report
        if is_complete:
            summary["completion_report"] = await generate_completion_report(all_tasks)
        
        return {
            "success": True,
            **summary
        }


async def trigger_phase_transition(
    project_id: int,
    from_phase: str,
    to_phase: str,
    context: Optional[Context] = None
) -> Dict:
    """
    Trigger transition from one project phase to another.
    
    Args:
        project_id: Project ID
        from_phase: Current phase name
        to_phase: Next phase name
        
    Returns:
        Transition result with new tasks created
    """
    async with get_async_session() as session:
        service = TaskService(session)
        
        # Verify current phase is complete
        phase_status = await check_phase_completion(session, from_phase, project_id)
        if not phase_status:
            return {
                "success": False,
                "error": f"Phase '{from_phase}' is not complete"
            }
        
        # Get phase definition from project metadata
        project_stmt = select(TaskModel).where(TaskModel.id == project_id)
        project_result = await session.execute(project_stmt)
        project_task = project_result.scalar_one_or_none()
        
        if not project_task:
            return {"success": False, "error": "Project not found"}
        
        project_metadata = parse_metadata(project_task.meta_data or {})
        
        # Create tasks for next phase
        new_tasks = []
        phase_tasks = project_metadata.phase_definitions.get(to_phase, [])
        
        for task_def in phase_tasks:
            task_metadata = {
                "parent_task_id": project_id,
                "phase": to_phase,
                **task_def.get("metadata", {})
            }
            
            # Create task using service
            new_task = await service.create_task(
                session=session,
                title=task_def["title"],
                description=task_def["description"],
                priority=task_def.get("priority", "medium"),
                metadata=task_metadata
            )
            new_tasks.append(new_task)
        
        # Update project phase
        project_metadata.current_phase = to_phase
        project_metadata.phase_history.append({
            "from": from_phase,
            "to": to_phase,
            "transitioned_at": datetime.now(timezone.utc).isoformat(),
            "tasks_created": len(new_tasks)
        })
        
        project_task.meta_data = project_metadata.dict()
        await session.commit()
        
        return {
            "success": True,
            "project_id": project_id,
            "from_phase": from_phase,
            "to_phase": to_phase,
            "new_tasks_created": len(new_tasks),
            "new_task_ids": [t.id for t in new_tasks]
        }


async def retry_failed_task(
    task_id: int,
    retry_reason: str,
    modifications: Optional[Dict[str, Any]] = None,
    context: Optional[Context] = None
) -> Dict:
    """
    Retry a failed task with optional modifications.
    
    Args:
        task_id: Failed task to retry
        retry_reason: Why we're retrying
        modifications: Optional changes to task parameters
        
    Returns:
        Result with retry status
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Verify task is in failed state
        if task.status != TaskStatus.FAILED.value:
            return {
                "success": False,
                "error": f"Task is not in failed state. Current status: {task.status}"
            }
        
        # Update metadata
        metadata = parse_metadata(task.meta_data or {})
        
        # Apply modifications if provided
        if modifications:
            for key, value in modifications.items():
                if hasattr(metadata, key):
                    setattr(metadata, key, value)
        
        # Record retry attempt
        retry_entry = {
            "attempt": metadata.failure_count + 1,
            "reason": retry_reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modifications": modifications or {}
        }
        
        if not hasattr(metadata, 'retry_history') or metadata.retry_history is None:
            metadata.retry_history = []
        metadata.retry_history.append(retry_entry)
        
        # Reset task for retry
        task.status = TaskStatus.PENDING.value
        task.started_at = None
        task.completed_at = None
        task.meta_data = metadata.dict()
        
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "new_status": TaskStatus.PENDING.value,
            "retry_attempt": metadata.failure_count + 1,
            "modifications_applied": bool(modifications)
        }


# Helper functions

async def get_tasks_blocked_by(session: AsyncSession, task_id: int) -> List[TaskModel]:
    """Get all tasks that depend on the given task"""
    stmt = select(TaskModel)
    result = await session.execute(stmt)
    all_tasks = result.scalars().all()
    
    blocked_tasks = []
    for task in all_tasks:
        metadata = parse_metadata(task.meta_data or {})
        if task_id in metadata.depends_on:
            blocked_tasks.append(task)
    
    return blocked_tasks


async def check_phase_completion(session: AsyncSession, phase: str, project_id: int) -> bool:
    """Check if all tasks in a phase are complete"""
    stmt = select(TaskModel)
    result = await session.execute(stmt)
    all_tasks = result.scalars().all()
    
    phase_tasks = []
    for task in all_tasks:
        metadata = parse_metadata(task.meta_data or {})
        if metadata.phase == phase and metadata.parent_task_id == project_id:
            phase_tasks.append(task)
    
    if not phase_tasks:
        return False
    
    # All tasks must be completed
    for task in phase_tasks:
        if task.status != TaskStatus.COMPLETED.value:
            return False
    
    return True


async def get_project_tasks(session: AsyncSession, project_id: int) -> List[TaskModel]:
    """Get all tasks in a project hierarchy"""
    stmt = select(TaskModel)
    result = await session.execute(stmt)
    all_tasks = result.scalars().all()
    
    project_tasks = []
    task_map = {t.id: t for t in all_tasks}
    
    def collect_tasks(task_id):
        if task_id in task_map:
            task = task_map[task_id]
            project_tasks.append(task)
            
            # Find children
            for t in all_tasks:
                metadata = parse_metadata(t.meta_data or {})
                if metadata.parent_task_id == task_id:
                    collect_tasks(t.id)
    
    collect_tasks(project_id)
    return project_tasks


async def generate_completion_report(tasks: List[TaskModel]) -> Dict:
    """Generate a completion report for a set of tasks"""
    total_estimated_hours = 0
    total_actual_hours = 0
    deliverables = []
    
    for task in tasks:
        metadata = parse_metadata(task.meta_data or {})
        
        if metadata.estimated_hours:
            total_estimated_hours += metadata.estimated_hours
        
        if metadata.actual_hours:
            total_actual_hours += metadata.actual_hours
        
        if metadata.deliverables:
            deliverables.extend(metadata.deliverables)
    
    return {
        "total_tasks": len(tasks),
        "total_estimated_hours": round(total_estimated_hours, 2),
        "total_actual_hours": round(total_actual_hours, 2),
        "efficiency_ratio": round(total_actual_hours / total_estimated_hours, 2) if total_estimated_hours > 0 else None,
        "total_deliverables": len(deliverables),
        "unique_deliverables": len(set(deliverables))
    }