"""MCP tools for dependency management"""
from typing import List, Dict, Optional, Set
from fastmcp import Context
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Task as TaskModel
from src.database.session import get_async_session
from src.utils.metadata_utils import parse_metadata, validate_dependencies, find_circular_dependencies
from src.models.task import TaskStatus
from src.models.metadata_schemas import get_active_states


async def set_task_dependencies(
    task_id: int,
    depends_on: List[int],
    blocks: Optional[List[int]] = None,
    context: Optional[Context] = None
) -> Dict:
    """
    Set task dependencies in metadata.
    
    Args:
        task_id: The task to update
        depends_on: List of task IDs this task depends on
        blocks: List of task IDs blocked by this task
        
    Returns:
        Updated task with dependencies
    """
    async with get_async_session() as session:
        # Validate dependencies
        errors = validate_dependencies(task_id, depends_on)
        if errors:
            return {"success": False, "errors": errors}
        
        # Get current task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Parse existing metadata
        metadata = parse_metadata(task.meta_data or {})
        metadata.depends_on = depends_on
        metadata.blocks = blocks or []
        
        # Build dependency graph to check for cycles
        # First, get all tasks to build the graph
        all_tasks_stmt = select(TaskModel)
        all_tasks_result = await session.execute(all_tasks_stmt)
        all_tasks = all_tasks_result.scalars().all()
        
        task_graph = {}
        for t in all_tasks:
            t_metadata = parse_metadata(t.meta_data or {})
            task_graph[t.id] = t_metadata.depends_on
        
        # Update with new dependencies
        task_graph[task_id] = depends_on
        
        # Check for circular dependencies
        cycle = await find_circular_dependencies(task_graph, task_id)
        if cycle:
            return {
                "success": False, 
                "error": "Circular dependency detected",
                "cycle": cycle
            }
        
        # Update task metadata
        task.meta_data = metadata.dict()
        
        # Also update the blocks relationship on the dependent tasks
        if blocks:
            for blocked_task_id in blocks:
                blocked_stmt = select(TaskModel).where(TaskModel.id == blocked_task_id)
                blocked_result = await session.execute(blocked_stmt)
                blocked_task = blocked_result.scalar_one_or_none()
                if blocked_task:
                    blocked_metadata = parse_metadata(blocked_task.meta_data or {})
                    if task_id not in blocked_metadata.blocks:
                        blocked_metadata.blocks.append(task_id)
                        blocked_task.meta_data = blocked_metadata.dict()
        
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "dependencies_set": len(depends_on),
            "blocks_set": len(blocks or [])
        }


async def get_ready_tasks(
    project_id: Optional[int] = None,
    agent_type: Optional[str] = None,
    context: Optional[Context] = None
) -> List[Dict]:
    """
    Find tasks ready to execute (all dependencies satisfied).
    
    Args:
        project_id: Filter by project (root task)
        agent_type: Filter by preferred agent type
        
    Returns:
        List of ready tasks with details
    """
    async with get_async_session() as session:
        # Get all pending/assigned tasks
        stmt = select(TaskModel).where(
            TaskModel.status.in_([TaskStatus.PENDING.value, TaskStatus.ASSIGNED.value])
        )
        result = await session.execute(stmt)
        candidate_tasks = result.scalars().all()
        
        ready_tasks = []
        
        for task in candidate_tasks:
            metadata = parse_metadata(task.meta_data or {})
            
            # Check project filter
            if project_id and metadata.parent_task_id != project_id:
                continue
            
            # Check agent type filter
            if agent_type and metadata.preferred_agent_type != agent_type:
                continue
            
            # Check if all dependencies are satisfied
            if await are_dependencies_satisfied(session, metadata.depends_on):
                ready_tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "priority": task.priority,
                    "depends_on": metadata.depends_on,
                    "parallel_group": metadata.parallel_group,
                    "can_parallelize": metadata.can_parallelize,
                    "required_capabilities": metadata.required_capabilities,
                    "exclusive_files": metadata.exclusive_files,
                    "estimated_hours": metadata.estimated_hours
                })
        
        # Sort by priority score
        ready_tasks.sort(
            key=lambda t: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(t["priority"], 2),
            reverse=True
        )
        
        return ready_tasks


async def check_circular_dependencies(
    task_id: int,
    new_dependencies: List[int],
    context: Optional[Context] = None
) -> Dict:
    """
    Check if adding dependencies would create a circular dependency.
    
    Args:
        task_id: Task that would have dependencies
        new_dependencies: Proposed dependencies
        
    Returns:
        Check result with cycle details if found
    """
    async with get_async_session() as session:
        # Build current dependency graph
        stmt = select(TaskModel)
        result = await session.execute(stmt)
        all_tasks = result.scalars().all()
        
        task_graph = {}
        for task in all_tasks:
            metadata = parse_metadata(task.meta_data or {})
            task_graph[task.id] = metadata.depends_on
        
        # Add proposed dependencies
        task_graph[task_id] = new_dependencies
        
        # Check for cycles
        cycle = await find_circular_dependencies(task_graph, task_id)
        
        if cycle:
            return {
                "has_cycle": True,
                "cycle": cycle,
                "cycle_description": " → ".join(f"Task {id}" for id in cycle)
            }
        else:
            return {
                "has_cycle": False,
                "message": "No circular dependencies found"
            }


async def get_dependency_graph(
    project_id: int,
    format: str = "tree",  # tree, mermaid, graphviz
    context: Optional[Context] = None
) -> Dict:
    """
    Get visual representation of task dependencies.
    
    Args:
        project_id: Root project task ID
        format: Output format (tree, mermaid, graphviz)
        
    Returns:
        Dependency graph in requested format
    """
    async with get_async_session() as session:
        # Get all tasks
        stmt = select(TaskModel)
        result = await session.execute(stmt)
        all_tasks = result.scalars().all()
        
        # Filter to project tasks
        project_tasks = []
        task_map = {t.id: t for t in all_tasks}
        
        # Find all tasks in this project hierarchy
        def collect_project_tasks(task_id):
            if task_id in task_map:
                task = task_map[task_id]
                project_tasks.append(task)
                
                # Find children
                for t in all_tasks:
                    metadata = parse_metadata(t.meta_data or {})
                    if metadata.parent_task_id == task_id:
                        collect_project_tasks(t.id)
        
        collect_project_tasks(project_id)
        
        if format == "mermaid":
            return {
                "format": "mermaid",
                "content": render_mermaid_graph(project_tasks),
                "task_count": len(project_tasks)
            }
        elif format == "tree":
            return {
                "format": "tree",
                "content": render_tree_graph(project_tasks, project_id),
                "task_count": len(project_tasks)
            }
        else:
            return {
                "format": "text",
                "content": f"Found {len(project_tasks)} tasks in project",
                "task_count": len(project_tasks)
            }


async def get_blocked_tasks(
    by_task_id: Optional[int] = None,
    context: Optional[Context] = None
) -> List[Dict]:
    """
    Get tasks that are blocked by dependencies.
    
    Args:
        by_task_id: If provided, only show tasks blocked by this specific task
        
    Returns:
        List of blocked tasks with blocking reasons
    """
    async with get_async_session() as session:
        stmt = select(TaskModel)
        result = await session.execute(stmt)
        all_tasks = result.scalars().all()
        blocked_tasks = []
        
        for task in all_tasks:
            if task.status == TaskStatus.BLOCKED.value:
                # Explicitly blocked status
                metadata = parse_metadata(task.meta_data or {})
                blocked_tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "status": "blocked",
                    "blocker_reason": metadata.blocker_reason,
                    "blocked_since": metadata.blocked_since
                })
            elif task.status in [TaskStatus.PENDING.value, TaskStatus.ASSIGNED.value]:
                # Check if blocked by dependencies
                metadata = parse_metadata(task.meta_data or {})
                
                if metadata.depends_on:
                    # Check which dependencies are not complete
                    incomplete_deps = []
                    for dep_id in metadata.depends_on:
                        if by_task_id and dep_id != by_task_id:
                            continue
                            
                        dep_task = next((t for t in all_tasks if t.id == dep_id), None)
                        if dep_task and dep_task.status != TaskStatus.COMPLETED.value:
                            incomplete_deps.append({
                                "id": dep_id,
                                "title": dep_task.title,
                                "status": dep_task.status
                            })
                    
                    if incomplete_deps:
                        blocked_tasks.append({
                            "id": task.id,
                            "title": task.title,
                            "status": task.status,
                            "blocked_by": incomplete_deps,
                            "blocker_reason": f"Waiting for {len(incomplete_deps)} dependencies"
                        })
        
        return blocked_tasks


# Helper functions

async def are_dependencies_satisfied(
    session: AsyncSession,
    dependency_ids: List[int]
) -> bool:
    """Check if all dependencies are completed"""
    if not dependency_ids:
        return True
    
    stmt = select(TaskModel).where(TaskModel.id.in_(dependency_ids))
    result = await session.execute(stmt)
    dep_tasks = result.scalars().all()
    
    # Check if all dependencies exist and are completed
    if len(dep_tasks) != len(dependency_ids):
        return False
    
    for dep_task in dep_tasks:
        if dep_task.status != TaskStatus.COMPLETED.value:
            return False
    
    return True


def render_mermaid_graph(tasks: List[TaskModel]) -> str:
    """Render dependency graph as Mermaid diagram"""
    lines = ["graph TD"]
    
    # Define nodes with status
    for task in tasks:
        status_emoji = {
            TaskStatus.COMPLETED.value: "✅",
            TaskStatus.IN_PROGRESS.value: "🔄",
            TaskStatus.BLOCKED.value: "🚫",
            TaskStatus.PENDING.value: "⏳",
            TaskStatus.NEEDS_REVIEW.value: "👀",
            TaskStatus.FIXES_REQUESTED.value: "🔧"
        }.get(task.status, "")
        
        lines.append(f"    {task.id}[\"{status_emoji} {task.title}\"]")
    
    # Add dependency edges
    for task in tasks:
        metadata = parse_metadata(task.meta_data or {})
        for dep_id in metadata.depends_on:
            lines.append(f"    {dep_id} --> {task.id}")
    
    return "\n".join(lines)


def render_tree_graph(tasks: List[TaskModel], root_id: int) -> str:
    """Render tasks as tree structure"""
    task_map = {t.id: t for t in tasks}
    
    def render_task(task_id, indent=0):
        if task_id not in task_map:
            return ""
        
        task = task_map[task_id]
        metadata = parse_metadata(task.meta_data or {})
        
        status_emoji = {
            TaskStatus.COMPLETED.value: "✅",
            TaskStatus.IN_PROGRESS.value: "🔄",
            TaskStatus.BLOCKED.value: "🚫",
            TaskStatus.PENDING.value: "⏳",
            TaskStatus.NEEDS_REVIEW.value: "👀",
            TaskStatus.FIXES_REQUESTED.value: "🔧"
        }.get(task.status, "")
        
        lines = [f"{'  ' * indent}{status_emoji} {task.title} (#{task.id})"]
        
        if metadata.depends_on:
            lines.append(f"{'  ' * (indent + 1)}└─ Depends on: {', '.join(f'#{id}' for id in metadata.depends_on)}")
        
        # Find children
        children = [t for t in tasks if parse_metadata(t.meta_data or {}).parent_task_id == task_id]
        for child in children:
            lines.append(render_task(child.id, indent + 1))
        
        return "\n".join(lines)
    
    return render_task(root_id)