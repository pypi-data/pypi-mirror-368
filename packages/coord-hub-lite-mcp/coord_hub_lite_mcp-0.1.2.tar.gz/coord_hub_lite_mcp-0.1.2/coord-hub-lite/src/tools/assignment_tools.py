"""
Assignment tools for MCP - task assignment and tree visualization with security integration.
Provides tools for assigning tasks to agents and viewing task hierarchies.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastmcp import Context

from src.services.assignment_service import AssignmentService
from src.utils.tree_builder import TreeBuilder
from src.database.session import get_async_session
# NO AUTHENTICATION - Local MCP server

# Import Task conditionally to avoid test issues
try:
    from src.database.models import Task
except ImportError:
    # For testing, use a mock
    Task = None


# NO AUTH REQUIRED
async def assign_task_tool(
    task_id: int,
    agent_id: str,
    check_capabilities: bool = True,
    context: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Assign a task to an agent with validation.
    
    This tool validates agent availability, capability matching (if enabled),
    and workload before making the assignment. It updates the task status
    to 'assigned' and creates an audit trail.
    
    Args:
        task_id: ID of the task to assign
        agent_id: ID of the agent to assign to
        check_capabilities: Whether to validate agent capabilities match task requirements
        context: Optional MCP context for structured logging
        
    Returns:
        Dict containing:
        - success: bool indicating if assignment succeeded
        - task_id: ID of the assigned task
        - agent_id: ID of the assigned agent
        - message: Success message or error details
        
    Example:
        >>> result = await assign_task_tool(
        ...     task_id=1,
        ...     agent_id="executor-001",
        ...     check_capabilities=True
        ... )
        >>> print(result)
        {
            'success': True,
            'task_id': 1,
            'agent_id': 'executor-001',
            'message': 'Task 1 assigned to executor-001'
        }
    """
    try:
        # Log the assignment attempt
        if context:
            await context.info(f"Attempting to assign task {task_id} to agent {agent_id}")
        
        async with get_async_session() as session:
            service = AssignmentService()
            result = await service.assign_task(
                session=session,
                task_id=task_id,
                agent_id=agent_id,
                check_capabilities=check_capabilities
            )
            
            # Standardize success response format
            if result.get('success'):
                if context:
                    await context.info(f"Successfully assigned task {task_id} to agent {agent_id}")
                return {
                    'success': True,
                    'data': result,
                    'task_id': task_id,
                    'agent_id': agent_id
                }
            else:
                # Handle service-level errors
                error_msg = result.get('error', 'Assignment service returned failure')
                if context:
                    await context.error(f"Assignment failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'task_id': task_id,
                    'agent_id': agent_id
                }
            
    except Exception as e:
        error_msg = f'Assignment failed: {str(e)}'
        if context:
            await context.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'task_id': task_id,
            'agent_id': agent_id
        }


# NO AUTH REQUIRED
async def get_task_tree_tool(
    root_task_id: Optional[int] = None,
    include_status: bool = True,
    status_filter: Optional[List[str]] = None,
    context: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Get hierarchical task tree visualization.
    
    Builds a tree structure showing task dependencies and relationships.
    Can return a single tree from a root task or a forest of all task trees.
    
    Args:
        root_task_id: Optional root task ID. If None, returns all task trees
        include_status: Whether to include task status in the tree
        status_filter: Optional list of statuses to include (e.g., ['pending', 'in_progress'])
        context: Optional MCP context for structured logging
        
    Returns:
        Dict containing:
        - tree: Single tree structure (if root_task_id provided)
        - forest: List of tree structures (if no root_task_id)
        - task_count: Total number of tasks in the result
        - stats: Statistics about the tasks
        
    Example:
        >>> # Get tree for specific task
        >>> result = await get_task_tree_tool(root_task_id=1)
        >>> print(result['tree'])
        {
            'id': 1,
            'title': 'Main Task',
            'status': 'in_progress',
            'agent_id': 'executor-001',
            'children': [
                {
                    'id': 2,
                    'title': 'Subtask 1',
                    'status': 'completed',
                    'agent_id': 'executor-002',
                    'children': []
                }
            ]
        }
        
        >>> # Get all task trees
        >>> result = await get_task_tree_tool()
        >>> print(f"Found {len(result['forest'])} task trees")
    """
    try:
        # Log the tree building attempt
        if context:
            if root_task_id:
                await context.info(f"Building task tree for root task {root_task_id}")
            else:
                await context.info("Building complete task forest")
        
        async with get_async_session() as session:
            builder = TreeBuilder()
            
            if root_task_id is not None:
                # Get specific task tree
                stmt = select(Task).options(
                    selectinload(Task.dependencies),
                    selectinload(Task.dependents)
                ).where(Task.id >= root_task_id)  # Get task and its descendants
                
                result = await session.execute(stmt)
                tasks = result.scalars().all()
                
                if context:
                    await context.debug(f"Found {len(tasks)} tasks for tree building")
                
                # Build tree
                tree = builder.build_tree(
                    tasks,
                    root_id=root_task_id,
                    status_filter=status_filter,
                    include_metadata=include_status
                )
                
                if not tree:
                    error_msg = f'Task {root_task_id} not found'
                    if context:
                        await context.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'task_count': 0
                    }
                
                # Get statistics
                stats = builder.get_task_stats(tree)
                
                if context:
                    await context.info(f"Successfully built task tree with {stats['total_tasks']} tasks")
                
                return {
                    'success': True,
                    'data': {
                        'tree': tree,
                        'task_count': stats['total_tasks'],
                        'stats': stats
                    }
                }
            else:
                # Get all tasks and build forest
                stmt = select(Task).options(
                    selectinload(Task.dependencies),
                    selectinload(Task.dependents)
                )
                
                result = await session.execute(stmt)
                tasks = result.scalars().all()
                
                if context:
                    await context.debug(f"Found {len(tasks)} total tasks for forest building")
                
                # Check for circular dependencies
                if builder.has_circular_dependencies(tasks):
                    error_msg = 'Circular dependencies detected in task graph'
                    if context:
                        await context.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'task_count': len(tasks)
                    }
                
                # Build forest
                forest = builder.build_forest(
                    tasks,
                    status_filter=status_filter,
                    include_metadata=include_status
                )
                
                # Calculate total stats
                total_tasks = 0
                combined_stats = {
                    'by_status': {},
                    'by_agent': {},
                    'unassigned': 0
                }
                
                for tree in forest:
                    stats = builder.get_task_stats(tree)
                    total_tasks += stats['total_tasks']
                    
                    # Merge status counts
                    for status, count in stats['by_status'].items():
                        combined_stats['by_status'][status] = \
                            combined_stats['by_status'].get(status, 0) + count
                    
                    # Merge agent counts
                    for agent, count in stats['by_agent'].items():
                        combined_stats['by_agent'][agent] = \
                            combined_stats['by_agent'].get(agent, 0) + count
                    
                    combined_stats['unassigned'] += stats['unassigned']
                
                if context:
                    await context.info(f"Successfully built task forest with {len(forest)} trees and {total_tasks} total tasks")
                
                return {
                    'success': True,
                    'data': {
                        'forest': forest,
                        'task_count': total_tasks,
                        'tree_count': len(forest),
                        'stats': combined_stats
                    }
                }
                
    except Exception as e:
        error_msg = f'Failed to build task tree: {str(e)}'
        if context:
            await context.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'task_count': 0
        }


# Tool metadata for MCP registration
TOOL_DEFINITIONS = [
    {
        "name": "assign_task",
        "description": "Assign a task to an agent with validation",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "ID of the task to assign"
                },
                "agent_id": {
                    "type": "string",
                    "description": "ID of the agent to assign to"
                },
                "check_capabilities": {
                    "type": "boolean",
                    "description": "Whether to validate agent capabilities",
                    "default": True
                }
            },
            "required": ["task_id", "agent_id"]
        }
    },
    {
        "name": "get_task_tree",
        "description": "Get hierarchical task tree visualization",
        "input_schema": {
            "type": "object",
            "properties": {
                "root_task_id": {
                    "type": ["integer", "null"],
                    "description": "Root task ID or null for all trees"
                },
                "include_status": {
                    "type": "boolean",
                    "description": "Include task status in tree",
                    "default": True
                },
                "status_filter": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "description": "Filter tasks by status"
                }
            }
        }
    }
]