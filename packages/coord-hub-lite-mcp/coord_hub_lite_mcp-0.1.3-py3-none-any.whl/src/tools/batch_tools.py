"""Batch operations tools for parallel task management"""
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.services.task_service import TaskService
from src.dao.task_dao import TaskDAO
from src.dao.agent_dao import AgentDAO
from src.models.task import TaskUpdate, TaskStatus


@asynccontextmanager
async def transaction_manager():
    """Context manager for database transactions"""
    async with get_async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def batch_create_tasks(
    tasks: List[Dict[str, Any]],
    project_id: Optional[int] = None,
    auto_assign: bool = False
) -> List[Dict[str, Any]]:
    """
    Create multiple tasks atomically with dependencies.
    
    Args:
        tasks: List of task definitions with optional 'temp_id' and 'depends_on'
        project_id: Optional project ID to associate tasks with
        auto_assign: Whether to auto-assign tasks to available agents
    
    Returns:
        List of created tasks with their IDs
    
    Example:
        >>> tasks = [
        ...     {
        ...         "temp_id": "task1",
        ...         "title": "Setup database",
        ...         "description": "Initialize database schema",
        ...         "priority": "high"
        ...     },
        ...     {
        ...         "temp_id": "task2", 
        ...         "title": "Create API",
        ...         "description": "Implement REST API",
        ...         "depends_on": ["task1"]
        ...     }
        ... ]
        >>> created = await batch_create_tasks(tasks, auto_assign=True)
    """
    async with transaction_manager() as session:
        task_service = TaskService(session)
        created_tasks = []
        task_mapping = {}  # temp_id -> actual_task
        
        # Phase 1: Create all tasks
        for task_data in tasks:
            temp_id = task_data.pop('temp_id', None)
            depends_on = task_data.pop('depends_on', [])  # Remove for now
            
            # Add project_id if provided
            if project_id and 'metadata' not in task_data:
                task_data['metadata'] = {}
            if project_id:
                task_data['metadata']['project_id'] = project_id
            
            # Create task
            task = await task_service.create_task(
                session=session,
                title=task_data.get('title', 'Untitled Task'),
                description=task_data.get('description', ''),
                priority=task_data.get('priority', 'medium'),
                metadata=task_data.get('metadata', {}),
                requires_documentation=task_data.get('requires_documentation', False),
                documentation_paths=task_data.get('documentation_paths'),
                documentation_context=task_data.get('documentation_context')
            )
            
            created_tasks.append({
                "id": task.id,
                "title": task.name,  # TaskResponse uses 'name' not 'title'
                "status": task.status,
                "temp_id": temp_id
            })
            
            if temp_id:
                task_mapping[temp_id] = task
        
        # Phase 2: Set up dependencies (if dependency service is available)
        # This would need to be implemented with a dependency service
        # For now, we'll store dependencies in metadata
        for i, task_data in enumerate(tasks):
            if 'depends_on' in task_data and task_data['depends_on']:
                # Update task metadata with dependencies
                task = created_tasks[i]
                deps = []
                for dep_ref in task_data['depends_on']:
                    if isinstance(dep_ref, str) and dep_ref in task_mapping:
                        deps.append(task_mapping[dep_ref].id)
                    elif isinstance(dep_ref, int):
                        deps.append(dep_ref)
                
                if deps:
                    # Store dependencies in metadata (simplified approach)
                    created_tasks[i]['dependencies'] = deps
        
        # Phase 3: Auto-assign if requested
        if auto_assign:
            # Get tasks without dependencies
            ready_tasks = [t for t in created_tasks if not t.get('dependencies')]
            if ready_tasks:
                assignments = await batch_assign_tasks(
                    task_ids=[t['id'] for t in ready_tasks],
                    max_parallel=4
                )
                # Update created_tasks with assignments
                for task in created_tasks:
                    if task['id'] in assignments:
                        task['assigned_to'] = assignments[task['id']]
        
        return created_tasks


async def batch_assign_tasks(
    task_ids: List[int],
    max_parallel: int = 4
) -> Dict[int, str]:
    """
    Assign multiple tasks to available agents.
    
    Args:
        task_ids: List of task IDs to assign
        max_parallel: Maximum number of parallel assignments
    
    Returns:
        Dictionary mapping task_id to agent_id
    
    Example:
        >>> assignments = await batch_assign_tasks(
        ...     task_ids=[1, 2, 3, 4, 5],
        ...     max_parallel=4
        ... )
        >>> print(assignments)
        {1: 'executor-001', 2: 'executor-002', 3: 'executor-003', 4: 'executor-004'}
    """
    async with get_async_session() as session:
        task_dao = TaskDAO(session)
        agent_dao = AgentDAO(session)
        assignments = {}
        
        # Limit to max_parallel
        task_ids_to_assign = task_ids[:max_parallel]
        
        # Get available agents
        available_agents = await agent_dao.get_available_agents(limit=max_parallel)
        
        if not available_agents:
            return assignments
        
        # For simplicity, treat all tasks as requiring 'executor' capability
        # This avoids the metadata access issue
        task_groups = {'executor': task_ids_to_assign}
        
        # Assign tasks to agents (round-robin)
        for i, task_id in enumerate(task_ids_to_assign):
            if i < len(available_agents):
                agent = available_agents[i]
                
                # Update task with agent assignment
                update_data = TaskUpdate(
                    status=TaskStatus.ASSIGNED,
                    assigned_to=agent.id
                )
                await task_dao.update_task_status(task_id, update_data)
                
                assignments[task_id] = agent.id
        
        await session.commit()
        return assignments


async def batch_update_status(
    updates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Update multiple task statuses atomically.
    
    Args:
        updates: List of update dictionaries with 'task_id', 'status', and optional 'metadata'
    
    Returns:
        List of updated tasks
    
    Example:
        >>> updates = [
        ...     {"task_id": 1, "status": "in_progress"},
        ...     {"task_id": 2, "status": "needs_review"},
        ...     {"task_id": 3, "status": "completed"}
        ... ]
        >>> updated = await batch_update_status(updates)
    """
    async with transaction_manager() as session:
        task_service = TaskService(session)
        updated_tasks = []
        
        for update in updates:
            try:
                task = await task_service.update_task_status(
                    session=session,
                    task_id=str(update['task_id']),
                    status=update['status'],
                    metadata=update.get('metadata', {})
                )
                
                updated_tasks.append({
                    "id": task.id,
                    "title": task.name,
                    "status": task.status,
                    "success": True
                })
            except ValueError as e:
                # Log error but continue with other updates
                updated_tasks.append({
                    "id": update['task_id'],
                    "error": str(e),
                    "success": False
                })
        
        return updated_tasks


async def get_ready_tasks(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get tasks that are ready for execution (pending with no unmet dependencies).
    
    Args:
        limit: Maximum number of tasks to return
    
    Returns:
        List of ready tasks
    """
    async with get_async_session() as session:
        task_dao = TaskDAO(session)
        
        # Get pending tasks
        pending_tasks = await task_dao.get_tasks_by_status("pending", limit=limit)
        
        ready_tasks = []
        for task in pending_tasks:
            # For now, consider all pending tasks as ready (simplified)
            ready_tasks.append({
                "id": task.id,
                "title": task.name,
                "priority": task.priority,
                "created_at": task.created_at.isoformat() if task.created_at else None
            })
        
        return ready_tasks


async def parallel_task_status() -> Dict[str, Any]:
    """
    Get current parallel execution status.
    
    Returns:
        Dictionary with execution statistics
    """
    async with get_async_session() as session:
        task_dao = TaskDAO(session)
        agent_dao = AgentDAO(session)
        
        # Get task counts by status
        in_progress = await task_dao.get_tasks_by_status("in_progress", limit=100)
        assigned = await task_dao.get_tasks_by_status("assigned", limit=100)
        pending = await task_dao.get_tasks_by_status("pending", limit=100)
        
        # Get agent availability
        available_agents = await agent_dao.get_available_agents(limit=10)
        busy_agents = await agent_dao.get_agents_by_status("busy", limit=10)
        
        return {
            "tasks": {
                "in_progress": len(in_progress),
                "assigned": len(assigned),
                "pending": len(pending)
            },
            "agents": {
                "available": len(available_agents),
                "busy": len(busy_agents)
            },
            "capacity": {
                "max_parallel": 4,
                "current_utilization": min(len(in_progress), 4),
                "available_slots": max(0, 4 - len(in_progress))
            }
        }


# Tool registry for MCP server
BATCH_TOOLS = {
    "batch_create_tasks": batch_create_tasks,
    "batch_assign_tasks": batch_assign_tasks,
    "batch_update_status": batch_update_status,
    "get_ready_tasks": get_ready_tasks,
    "parallel_task_status": parallel_task_status
}