"""MCP tools for file ownership management"""
from typing import List, Dict, Optional, Set
from fastmcp import Context
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Task as TaskModel
from src.database.session import get_async_session
from src.utils.metadata_utils import parse_metadata
from src.models.task import TaskStatus
from src.models.metadata_schemas import get_active_states


async def set_file_ownership(
    task_id: int,
    exclusive_files: List[str],
    context: Optional[Context] = None
) -> Dict:
    """
    Set exclusive file ownership for a task.
    
    Args:
        task_id: Task claiming ownership
        exclusive_files: List of file paths to claim exclusive access to
        
    Returns:
        Result with success status and any conflicts
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Check for conflicts with other active tasks
        conflicts = await check_file_conflicts(session, task_id, exclusive_files)
        if conflicts:
            return {
                "success": False,
                "error": "File ownership conflicts detected",
                "conflicts": conflicts
            }
        
        # Update task metadata
        metadata = parse_metadata(task.meta_data or {})
        metadata.exclusive_files = exclusive_files
        task.meta_data = metadata.dict()
        
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "files_claimed": len(exclusive_files)
        }


async def check_file_conflicts(
    session: AsyncSession,
    requesting_task_id: int,
    requested_files: List[str]
) -> List[Dict]:
    """
    Check if any requested files are already owned by other active tasks.
    
    Args:
        session: Database session
        requesting_task_id: Task requesting ownership
        requested_files: Files being requested
        
    Returns:
        List of conflicts with task details
    """
    # Get all active tasks
    active_states = get_active_states()
    stmt = select(TaskModel).where(
        TaskModel.status.in_(active_states),
        TaskModel.id != requesting_task_id
    )
    result = await session.execute(stmt)
    active_tasks = result.scalars().all()
    
    conflicts = []
    requested_set = set(requested_files)
    
    for task in active_tasks:
        metadata = parse_metadata(task.meta_data or {})
        if metadata.exclusive_files:
            owned_set = set(metadata.exclusive_files)
            conflicting_files = requested_set & owned_set
            
            if conflicting_files:
                conflicts.append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "task_status": task.status,
                    "conflicting_files": list(conflicting_files)
                })
    
    return conflicts


async def get_file_ownership_map(
    project_id: Optional[int] = None,
    context: Optional[Context] = None
) -> Dict[str, Dict]:
    """
    Get a map of all files and their current owners.
    
    Args:
        project_id: Filter by project (optional)
        
    Returns:
        Map of file paths to owner details
    """
    async with get_async_session() as session:
        # Get all active tasks
        active_states = get_active_states()
        stmt = select(TaskModel).where(TaskModel.status.in_(active_states))
        result = await session.execute(stmt)
        active_tasks = result.scalars().all()
        
        file_map = {}
        
        for task in active_tasks:
            metadata = parse_metadata(task.meta_data or {})
            
            # Check project filter
            if project_id and metadata.parent_task_id != project_id:
                continue
            
            for file_path in metadata.exclusive_files:
                file_map[file_path] = {
                    "owner_task_id": task.id,
                    "owner_task_title": task.title,
                    "owner_task_status": task.status,
                    "assigned_agent": task.agent_id
                }
        
        return file_map


async def release_file_ownership(
    task_id: int,
    files_to_release: Optional[List[str]] = None,
    context: Optional[Context] = None
) -> Dict:
    """
    Release file ownership for a task.
    
    Args:
        task_id: Task releasing ownership
        files_to_release: Specific files to release (None = release all)
        
    Returns:
        Result with files released
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
        
        if files_to_release is None:
            # Release all files
            released = metadata.exclusive_files
            metadata.exclusive_files = []
        else:
            # Release specific files
            current_files = set(metadata.exclusive_files)
            to_release = set(files_to_release)
            released = list(current_files & to_release)
            metadata.exclusive_files = list(current_files - to_release)
        
        task.meta_data = metadata.dict()
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "files_released": released,
            "files_retained": metadata.exclusive_files
        }


async def get_available_files(
    project_id: int,
    file_patterns: Optional[List[str]] = None,
    context: Optional[Context] = None
) -> List[str]:
    """
    Get list of files not currently owned by any active task.
    
    Args:
        project_id: Project to check within
        file_patterns: Optional glob patterns to filter files
        
    Returns:
        List of available file paths
    """
    # Get ownership map
    ownership_map = await get_file_ownership_map(project_id)
    owned_files = set(ownership_map.keys())
    
    # In a real implementation, we would:
    # 1. Get all project files using glob patterns
    # 2. Filter out owned files
    # 3. Return available files
    
    # For now, return a placeholder response
    return {
        "project_id": project_id,
        "owned_files_count": len(owned_files),
        "patterns": file_patterns,
        "message": "File discovery not yet implemented - would scan project files and exclude owned ones"
    }


async def transfer_file_ownership(
    from_task_id: int,
    to_task_id: int,
    files: List[str],
    context: Optional[Context] = None
) -> Dict:
    """
    Transfer file ownership between tasks.
    
    Args:
        from_task_id: Current owner task
        to_task_id: New owner task
        files: Files to transfer
        
    Returns:
        Transfer result
    """
    async with get_async_session() as session:
        # Get both tasks
        from_stmt = select(TaskModel).where(TaskModel.id == from_task_id)
        from_result = await session.execute(from_stmt)
        from_task = from_result.scalar_one_or_none()
        
        to_stmt = select(TaskModel).where(TaskModel.id == to_task_id)
        to_result = await session.execute(to_stmt)
        to_task = to_result.scalar_one_or_none()
        
        if not from_task:
            return {"success": False, "error": f"Source task {from_task_id} not found"}
        if not to_task:
            return {"success": False, "error": f"Target task {to_task_id} not found"}
        
        # Check if target task is active
        if to_task.status not in get_active_states():
            return {"success": False, "error": f"Target task is not in active state: {to_task.status}"}
        
        # Update source task metadata
        from_metadata = parse_metadata(from_task.meta_data or {})
        current_files = set(from_metadata.exclusive_files)
        to_transfer = set(files)
        
        # Verify source owns all files
        if not to_transfer.issubset(current_files):
            missing = to_transfer - current_files
            return {
                "success": False,
                "error": "Source task does not own all requested files",
                "missing_files": list(missing)
            }
        
        # Remove from source
        from_metadata.exclusive_files = list(current_files - to_transfer)
        from_task.meta_data = from_metadata.dict()
        
        # Add to target
        to_metadata = parse_metadata(to_task.meta_data or {})
        to_metadata.exclusive_files = list(set(to_metadata.exclusive_files) | to_transfer)
        to_task.meta_data = to_metadata.dict()
        
        await session.commit()
        
        return {
            "success": True,
            "transferred_files": files,
            "from_task": {
                "id": from_task_id,
                "title": from_task.title,
                "remaining_files": from_metadata.exclusive_files
            },
            "to_task": {
                "id": to_task_id,
                "title": to_task.title,
                "total_files": len(to_metadata.exclusive_files)
            }
        }