"""MCP tools for review workflow management"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from fastmcp import Context
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Task as TaskModel
from src.database.session import get_async_session
from src.utils.metadata_utils import parse_metadata, merge_metadata
from src.models.task import TaskStatus, TaskPriority
from src.models.metadata_schemas import TaskMetadata, ReviewDecision


async def submit_task_for_review(
    task_id: int,
    reviewer_agent_id: Optional[str] = None,
    review_type: str = "code_review",
    artifacts: Optional[List[str]] = None,
    context: Optional[Context] = None
) -> Dict:
    """
    Submit a task for review when executor completes.
    
    Args:
        task_id: Task to submit for review
        reviewer_agent_id: Specific reviewer to assign (optional)
        review_type: Type of review needed (code_review, architecture_review, etc.)
        artifacts: List of artifact paths to review
        
    Returns:
        Result with review task details
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Validate task is in a state that can be reviewed
        if task.status not in [TaskStatus.IN_PROGRESS.value, TaskStatus.COMPLETED.value]:
            return {
                "success": False, 
                "error": f"Task must be in progress or completed to submit for review. Current status: {task.status}"
            }
        
        # Update task status to needs_review
        task.status = TaskStatus.NEEDS_REVIEW.value
        
        # Update metadata with review information
        metadata = parse_metadata(task.meta_data or {})
        metadata.review_required = True
        metadata.review_type = review_type
        metadata.review_requested_at = datetime.now(timezone.utc).isoformat()
        metadata.review_requested_by = task.agent_id
        
        if reviewer_agent_id:
            metadata.assigned_reviewer = reviewer_agent_id
        
        if artifacts:
            metadata.review_artifacts = artifacts
        
        task.meta_data = metadata.dict()
        
        # Create review task if needed (for complex workflows)
        review_task = None
        if metadata.create_review_subtask:
            review_task_data = {
                "title": f"Review: {task.title}",
                "description": f"Review {review_type} for task #{task_id}: {task.title}",
                "priority": task.priority,
                "meta_data": {
                    "parent_task_id": task_id,
                    "is_review_task": True,
                    "review_type": review_type,
                    "original_task_id": task_id,
                    "preferred_agent_type": "reviewer",
                    "required_capabilities": [review_type, "review"],
                    "review_artifacts": artifacts or []
                }
            }
            
            review_model = TaskModel(**review_task_data)
            session.add(review_model)
            await session.flush()
            review_task = review_model
        
        await session.commit()
        
        response = {
            "success": True,
            "task_id": task_id,
            "status": TaskStatus.NEEDS_REVIEW.value,
            "review_type": review_type
        }
        
        if review_task:
            response["review_task_id"] = review_task.id
            response["review_task_title"] = review_task.title
        
        return response


async def submit_review_decision(
    task_id: int,
    decision: str,  # approved, needs_fixes, rejected
    reviewer_agent_id: str,
    feedback: str,
    required_fixes: Optional[List[str]] = None,
    blocking_issues: Optional[List[str]] = None,
    context: Optional[Context] = None
) -> Dict:
    """
    Submit review decision for a task.
    
    Args:
        task_id: Task being reviewed
        decision: Review decision (approved/needs_fixes/rejected)
        reviewer_agent_id: ID of reviewing agent
        feedback: Review feedback text
        required_fixes: List of required fixes (for needs_fixes)
        blocking_issues: List of blocking issues (for rejected)
        
    Returns:
        Result with updated task status
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Validate task is in review
        if task.status != TaskStatus.NEEDS_REVIEW.value:
            return {
                "success": False,
                "error": f"Task is not in review. Current status: {task.status}"
            }
        
        # Parse decision
        try:
            review_decision = ReviewDecision(decision)
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid decision: {decision}. Must be one of: approved, needs_fixes, rejected"
            }
        
        # Update metadata with review results
        metadata = parse_metadata(task.meta_data or {})
        
        # Add to review history
        review_entry = {
            "reviewer": reviewer_agent_id,
            "decision": decision,
            "feedback": feedback,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "required_fixes": required_fixes or [],
            "blocking_issues": blocking_issues or []
        }
        
        if not hasattr(metadata, 'review_history') or metadata.review_history is None:
            metadata.review_history = []
        metadata.review_history.append(review_entry)
        
        # Update task based on decision
        if review_decision == ReviewDecision.APPROVED:
            task.status = TaskStatus.COMPLETED.value
            metadata.review_status = "approved"
            metadata.approved_by = reviewer_agent_id
            metadata.approved_at = datetime.now(timezone.utc).isoformat()
            
        elif review_decision == ReviewDecision.NEEDS_FIXES:
            task.status = TaskStatus.FIXES_REQUESTED.value
            metadata.review_status = "needs_fixes"
            metadata.fixes_requested_by = reviewer_agent_id
            metadata.fixes_requested_at = datetime.now(timezone.utc).isoformat()
            metadata.required_fixes = required_fixes or []
            
        else:  # REJECTED
            task.status = TaskStatus.BLOCKED.value
            metadata.review_status = "rejected"
            metadata.rejected_by = reviewer_agent_id
            metadata.rejected_at = datetime.now(timezone.utc).isoformat()
            metadata.blocker_reason = f"Rejected in review: {', '.join(blocking_issues or ['See feedback'])}"
            metadata.blocking_issues = blocking_issues or []
        
        task.meta_data = metadata.dict()
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "new_status": task.status,
            "decision": decision,
            "review_entry": review_entry
        }


async def get_tasks_pending_review(
    reviewer_agent_id: Optional[str] = None,
    review_type: Optional[str] = None,
    project_id: Optional[int] = None,
    context: Optional[Context] = None
) -> List[Dict]:
    """
    Get all tasks waiting for review.
    
    Args:
        reviewer_agent_id: Filter by assigned reviewer
        review_type: Filter by review type
        project_id: Filter by project
        
    Returns:
        List of tasks pending review
    """
    async with get_async_session() as session:
        # Query tasks in needs_review status
        stmt = select(TaskModel).where(
            TaskModel.status == TaskStatus.NEEDS_REVIEW.value
        )
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        
        pending_reviews = []
        
        for task in tasks:
            metadata = parse_metadata(task.meta_data or {})
            
            # Apply filters
            if reviewer_agent_id and metadata.assigned_reviewer != reviewer_agent_id:
                continue
                
            if review_type and metadata.review_type != review_type:
                continue
                
            if project_id and metadata.parent_task_id != project_id:
                continue
            
            pending_reviews.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "review_type": metadata.review_type,
                "assigned_reviewer": metadata.assigned_reviewer,
                "review_requested_at": metadata.review_requested_at,
                "review_requested_by": metadata.review_requested_by,
                "artifacts": metadata.review_artifacts or [],
                "executor_agent": task.agent_id
            })
        
        # Sort by priority and request time
        pending_reviews.sort(
            key=lambda t: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(t["priority"], 2),
                t["review_requested_at"] or ""
            ),
            reverse=True
        )
        
        return pending_reviews


async def get_review_history(
    task_id: int,
    context: Optional[Context] = None
) -> Dict:
    """
    Get complete review history for a task.
    
    Args:
        task_id: Task to get history for
        
    Returns:
        Review history with all decisions and feedback
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        metadata = parse_metadata(task.meta_data or {})
        
        return {
            "success": True,
            "task_id": task_id,
            "task_title": task.title,
            "current_status": task.status,
            "review_required": metadata.review_required,
            "review_type": metadata.review_type,
            "review_status": metadata.review_status,
            "review_history": metadata.review_history or [],
            "total_reviews": len(metadata.review_history or [])
        }


async def resubmit_after_fixes(
    task_id: int,
    fix_summary: str,
    fixed_items: List[str],
    context: Optional[Context] = None
) -> Dict:
    """
    Resubmit a task for review after fixes.
    
    Args:
        task_id: Task that was fixed
        fix_summary: Summary of fixes made
        fixed_items: List of specific fixes addressed
        
    Returns:
        Result with updated status
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Validate task is in fixes_requested status
        if task.status != TaskStatus.FIXES_REQUESTED.value:
            return {
                "success": False,
                "error": f"Task is not in fixes_requested status. Current status: {task.status}"
            }
        
        # Update metadata
        metadata = parse_metadata(task.meta_data or {})
        
        # Record fix information
        fix_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": fix_summary,
            "fixed_items": fixed_items,
            "agent_id": task.agent_id
        }
        
        if not hasattr(metadata, 'fix_history') or metadata.fix_history is None:
            metadata.fix_history = []
        metadata.fix_history.append(fix_entry)
        
        # Clear required_fixes that were addressed
        if metadata.required_fixes:
            remaining_fixes = [
                fix for fix in metadata.required_fixes 
                if fix not in fixed_items
            ]
            metadata.required_fixes = remaining_fixes
        
        # Update status back to needs_review
        task.status = TaskStatus.NEEDS_REVIEW.value
        metadata.resubmitted_for_review = True
        metadata.resubmitted_at = datetime.now(timezone.utc).isoformat()
        
        task.meta_data = metadata.dict()
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "new_status": TaskStatus.NEEDS_REVIEW.value,
            "fix_summary": fix_summary,
            "fixed_items_count": len(fixed_items),
            "remaining_fixes": metadata.required_fixes or []
        }


async def escalate_review(
    task_id: int,
    escalation_reason: str,
    escalate_to: str,  # architect, senior_reviewer, etc.
    context: Optional[Context] = None
) -> Dict:
    """
    Escalate a review to a higher-level reviewer.
    
    Args:
        task_id: Task to escalate
        escalation_reason: Why escalation is needed
        escalate_to: Type of reviewer to escalate to
        
    Returns:
        Escalation result
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Update metadata
        metadata = parse_metadata(task.meta_data or {})
        
        # Record escalation
        escalation_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": escalation_reason,
            "escalated_to": escalate_to,
            "previous_reviewer": metadata.assigned_reviewer,
            "escalated_by": metadata.assigned_reviewer or "system"
        }
        
        if not hasattr(metadata, 'escalation_history') or metadata.escalation_history is None:
            metadata.escalation_history = []
        metadata.escalation_history.append(escalation_entry)
        
        # Update review requirements
        metadata.review_escalated = True
        metadata.escalated_reviewer_type = escalate_to
        metadata.escalation_reason = escalation_reason
        
        # Clear current reviewer assignment to allow reassignment
        metadata.assigned_reviewer = None
        
        # Update required capabilities for finding new reviewer
        if escalate_to == "architect":
            metadata.required_capabilities = ["architecture_review", "senior_review"]
        elif escalate_to == "senior_reviewer":
            metadata.required_capabilities = ["senior_review", metadata.review_type]
        
        task.meta_data = metadata.dict()
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "escalated_to": escalate_to,
            "escalation_reason": escalation_reason,
            "requires_reassignment": True
        }