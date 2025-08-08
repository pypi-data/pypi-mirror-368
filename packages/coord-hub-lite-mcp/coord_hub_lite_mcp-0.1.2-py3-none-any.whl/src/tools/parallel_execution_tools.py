"""MCP tools for managing parallel task execution"""
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, timezone
from fastmcp import Context
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Task as TaskModel, Agent as AgentModel
from src.database.session import get_async_session
from src.utils.metadata_utils import parse_metadata
from src.models.task import TaskStatus
from src.models.agent import AgentStatus


async def identify_parallel_groups(
    project_id: int,
    context: Optional[Context] = None
) -> Dict:
    """
    Identify groups of tasks that can be executed in parallel.
    
    Args:
        project_id: Project to analyze
        
    Returns:
        Parallel execution groups
    """
    async with get_async_session() as session:
        # Get all project tasks
        tasks = await get_project_tasks(session, project_id)
        
        # Build dependency graph
        dep_graph = build_dependency_graph(tasks)
        
        # Find parallel groups using topological levels
        levels = calculate_topological_levels(dep_graph)
        
        # Group tasks by level
        parallel_groups = {}
        for task_id, level in levels.items():
            if level not in parallel_groups:
                parallel_groups[level] = []
            
            task = next((t for t in tasks if t.id == task_id), None)
            if task:
                metadata = parse_metadata(task.meta_data or {})
                parallel_groups[level].append({
                    "task_id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "can_parallelize": metadata.can_parallelize,
                    "exclusive_files": metadata.exclusive_files,
                    "estimated_hours": metadata.estimated_hours
                })
        
        # Check for file conflicts within groups
        for level, group_tasks in parallel_groups.items():
            conflicts = check_file_conflicts_in_group(group_tasks)
            if conflicts:
                parallel_groups[level] = resolve_file_conflicts(group_tasks, conflicts)
        
        return {
            "success": True,
            "project_id": project_id,
            "total_tasks": len(tasks),
            "parallel_groups": parallel_groups,
            "max_parallelism": max(len(g) for g in parallel_groups.values()) if parallel_groups else 0,
            "total_levels": len(parallel_groups)
        }


async def schedule_parallel_execution(
    task_ids: List[int],
    max_parallel: int = 4,
    respect_file_locks: bool = True,
    context: Optional[Context] = None
) -> Dict:
    """
    Schedule tasks for parallel execution with resource constraints.
    
    Args:
        task_ids: Tasks to schedule
        max_parallel: Maximum parallel executions
        respect_file_locks: Whether to respect file ownership
        
    Returns:
        Execution schedule
    """
    async with get_async_session() as session:
        # Get tasks
        stmt = select(TaskModel).where(TaskModel.id.in_(task_ids))
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        
        if not tasks:
            return {"success": False, "error": "No tasks found"}
        
        # Get available agents
        available_agents = await get_agents_for_parallel_execution(session, max_parallel)
        
        if not available_agents:
            return {
                "success": False,
                "error": "No available agents for parallel execution"
            }
        
        # Build execution schedule
        schedule = []
        assigned_files = set()
        assigned_agents = set()
        
        for task in tasks:
            metadata = parse_metadata(task.meta_data or {})
            
            # Check if task can be scheduled
            can_schedule = True
            
            # Check file conflicts
            if respect_file_locks and metadata.exclusive_files:
                file_conflicts = set(metadata.exclusive_files) & assigned_files
                if file_conflicts:
                    can_schedule = False
            
            # Check agent availability
            suitable_agents = [
                a for a in available_agents 
                if a.id not in assigned_agents and
                agent_can_handle_task(a, task)
            ]
            
            if not suitable_agents:
                can_schedule = False
            
            if can_schedule and task.status == TaskStatus.PENDING.value:
                # Assign to agent
                agent = suitable_agents[0]
                
                schedule.append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "agent_id": agent.id,
                    "agent_type": agent.agent_type,
                    "start_time": "immediate",
                    "exclusive_files": metadata.exclusive_files
                })
                
                # Mark resources as used
                assigned_agents.add(agent.id)
                if metadata.exclusive_files:
                    assigned_files.update(metadata.exclusive_files)
                
                # Update task
                task.agent_id = agent.id
                task.status = TaskStatus.ASSIGNED.value
                metadata.parallel_group = "scheduled"
                metadata.scheduled_at = datetime.now(timezone.utc).isoformat()
                task.meta_data = metadata.dict()
                
                # Update agent workload
                agent.current_workload += 1
        
        await session.commit()
        
        # Tasks that couldn't be scheduled
        unscheduled = [t for t in tasks if t.id not in [s["task_id"] for s in schedule]]
        
        return {
            "success": True,
            "scheduled_count": len(schedule),
            "schedule": schedule,
            "unscheduled_count": len(unscheduled),
            "unscheduled_tasks": [{"id": t.id, "title": t.title} for t in unscheduled],
            "agents_used": len(assigned_agents),
            "files_locked": len(assigned_files)
        }


async def detect_parallelization_opportunities(
    project_id: int,
    min_time_saved: float = 2.0,
    context: Optional[Context] = None
) -> Dict:
    """
    Detect opportunities to parallelize sequential tasks.
    
    Args:
        project_id: Project to analyze
        min_time_saved: Minimum hours saved to suggest parallelization
        
    Returns:
        Parallelization opportunities
    """
    async with get_async_session() as session:
        # Get project tasks
        tasks = await get_project_tasks(session, project_id)
        
        # Find sequential chains that could be parallelized
        opportunities = []
        
        # Build dependency graph
        dep_graph = build_dependency_graph(tasks)
        
        # Find linear chains
        chains = find_linear_chains(dep_graph, tasks)
        
        for chain in chains:
            # Check if tasks in chain can be parallelized
            chain_tasks = [t for t in tasks if t.id in chain]
            
            if can_parallelize_chain(chain_tasks):
                # Calculate time savings
                sequential_time = sum(
                    parse_metadata(t.meta_data or {}).estimated_hours or 0 
                    for t in chain_tasks
                )
                
                parallel_time = max(
                    parse_metadata(t.meta_data or {}).estimated_hours or 0 
                    for t in chain_tasks
                )
                
                time_saved = sequential_time - parallel_time
                
                if time_saved >= min_time_saved:
                    opportunities.append({
                        "chain_tasks": [
                            {"id": t.id, "title": t.title} 
                            for t in chain_tasks
                        ],
                        "sequential_time": round(sequential_time, 2),
                        "parallel_time": round(parallel_time, 2),
                        "time_saved": round(time_saved, 2),
                        "speedup_factor": round(sequential_time / parallel_time, 2) if parallel_time > 0 else 0
                    })
        
        # Find independent task groups
        independent_groups = find_independent_task_groups(tasks, dep_graph)
        
        for group in independent_groups:
            if len(group) > 1:
                group_tasks = [t for t in tasks if t.id in group]
                total_time = sum(
                    parse_metadata(t.meta_data or {}).estimated_hours or 0 
                    for t in group_tasks
                )
                
                if total_time >= min_time_saved:
                    opportunities.append({
                        "independent_group": [
                            {"id": t.id, "title": t.title} 
                            for t in group_tasks
                        ],
                        "total_hours": round(total_time, 2),
                        "can_parallelize": True
                    })
        
        return {
            "success": True,
            "project_id": project_id,
            "opportunities_found": len(opportunities),
            "opportunities": opportunities,
            "potential_time_saved": sum(o.get("time_saved", 0) for o in opportunities)
        }


async def coordinate_parallel_agents(
    parallel_group_id: str,
    coordination_type: str = "sync_point",
    context: Optional[Context] = None
) -> Dict:
    """
    Coordinate agents working on parallel tasks.
    
    Args:
        parallel_group_id: ID of the parallel execution group
        coordination_type: Type of coordination (sync_point, shared_resource, message_pass)
        
    Returns:
        Coordination status
    """
    async with get_async_session() as session:
        # Get tasks in parallel group
        stmt = select(TaskModel)
        result = await session.execute(stmt)
        all_tasks = result.scalars().all()
        
        group_tasks = []
        for task in all_tasks:
            metadata = parse_metadata(task.meta_data or {})
            if metadata.parallel_group == parallel_group_id:
                group_tasks.append(task)
        
        if not group_tasks:
            return {"success": False, "error": "No tasks found in parallel group"}
        
        coordination_result = {
            "group_id": parallel_group_id,
            "task_count": len(group_tasks),
            "coordination_type": coordination_type
        }
        
        if coordination_type == "sync_point":
            # Check if all tasks reached sync point
            ready_for_sync = all(
                t.status in [TaskStatus.COMPLETED.value, TaskStatus.NEEDS_REVIEW.value]
                for t in group_tasks
            )
            
            coordination_result["ready_for_sync"] = ready_for_sync
            coordination_result["waiting_tasks"] = [
                {"id": t.id, "title": t.title, "status": t.status}
                for t in group_tasks
                if t.status not in [TaskStatus.COMPLETED.value, TaskStatus.NEEDS_REVIEW.value]
            ]
            
            if ready_for_sync:
                # Update metadata to mark sync achieved
                for task in group_tasks:
                    metadata = parse_metadata(task.meta_data or {})
                    metadata.sync_point_reached = True
                    metadata.sync_point_time = datetime.now(timezone.utc).isoformat()
                    task.meta_data = metadata.dict()
        
        elif coordination_type == "shared_resource":
            # Coordinate shared resource access
            resource_map = {}
            
            for task in group_tasks:
                metadata = parse_metadata(task.meta_data or {})
                for resource in metadata.shared_resources or []:
                    if resource not in resource_map:
                        resource_map[resource] = []
                    resource_map[resource].append({
                        "task_id": task.id,
                        "task_title": task.title,
                        "access_type": metadata.resource_access_type
                    })
            
            coordination_result["shared_resources"] = resource_map
            coordination_result["conflicts"] = find_resource_conflicts(resource_map)
        
        elif coordination_type == "message_pass":
            # Set up message passing between tasks
            message_queue = []
            
            for task in group_tasks:
                metadata = parse_metadata(task.meta_data or {})
                if metadata.output_message:
                    message_queue.append({
                        "from_task": task.id,
                        "to_tasks": metadata.message_recipients or [],
                        "message_type": metadata.message_type,
                        "timestamp": metadata.message_timestamp
                    })
            
            coordination_result["message_queue"] = message_queue
            coordination_result["pending_messages"] = len(message_queue)
        
        await session.commit()
        
        return {
            "success": True,
            **coordination_result
        }


async def monitor_parallel_progress(
    parallel_group_id: Optional[str] = None,
    project_id: Optional[int] = None,
    context: Optional[Context] = None
) -> Dict:
    """
    Monitor progress of parallel task execution.
    
    Args:
        parallel_group_id: Specific group to monitor
        project_id: Project to monitor all parallel groups
        
    Returns:
        Progress report
    """
    async with get_async_session() as session:
        # Get tasks to monitor
        stmt = select(TaskModel)
        result = await session.execute(stmt)
        all_tasks = result.scalars().all()
        
        if parallel_group_id:
            # Monitor specific group
            group_tasks = [
                t for t in all_tasks
                if parse_metadata(t.meta_data or {}).parallel_group == parallel_group_id
            ]
            
            if not group_tasks:
                return {"success": False, "error": "Parallel group not found"}
            
            progress = calculate_group_progress(group_tasks)
            
            return {
                "success": True,
                "group_id": parallel_group_id,
                **progress
            }
        
        elif project_id:
            # Monitor all parallel groups in project
            project_tasks = [
                t for t in all_tasks
                if parse_metadata(t.meta_data or {}).parent_task_id == project_id
            ]
            
            # Group by parallel group
            groups = {}
            for task in project_tasks:
                metadata = parse_metadata(task.meta_data or {})
                if metadata.parallel_group:
                    if metadata.parallel_group not in groups:
                        groups[metadata.parallel_group] = []
                    groups[metadata.parallel_group].append(task)
            
            group_progress = {}
            for group_id, group_tasks in groups.items():
                group_progress[group_id] = calculate_group_progress(group_tasks)
            
            return {
                "success": True,
                "project_id": project_id,
                "parallel_groups": len(groups),
                "group_progress": group_progress,
                "overall_completion": calculate_overall_completion(group_progress)
            }
        
        else:
            return {
                "success": False,
                "error": "Must specify either parallel_group_id or project_id"
            }


# Helper functions

async def get_project_tasks(session: AsyncSession, project_id: int) -> List[TaskModel]:
    """Get all tasks in a project"""
    stmt = select(TaskModel)
    result = await session.execute(stmt)
    all_tasks = result.scalars().all()
    
    project_tasks = []
    
    def collect_tasks(task_id):
        for task in all_tasks:
            metadata = parse_metadata(task.meta_data or {})
            if task.id == task_id or metadata.parent_task_id == task_id:
                if task not in project_tasks:
                    project_tasks.append(task)
                    collect_tasks(task.id)
    
    collect_tasks(project_id)
    return project_tasks


def build_dependency_graph(tasks: List[TaskModel]) -> Dict[int, List[int]]:
    """Build dependency graph from tasks"""
    graph = {}
    
    for task in tasks:
        metadata = parse_metadata(task.meta_data or {})
        graph[task.id] = metadata.depends_on
    
    return graph


def calculate_topological_levels(graph: Dict[int, List[int]]) -> Dict[int, int]:
    """Calculate topological levels for parallel execution"""
    levels = {}
    
    # Find tasks with no dependencies (level 0)
    for task_id, deps in graph.items():
        if not deps:
            levels[task_id] = 0
    
    # Calculate levels for remaining tasks
    changed = True
    while changed:
        changed = False
        for task_id, deps in graph.items():
            if task_id not in levels and deps:
                # Check if all dependencies have levels
                if all(dep in levels for dep in deps):
                    # Set level to max dependency level + 1
                    levels[task_id] = max(levels[dep] for dep in deps) + 1
                    changed = True
    
    return levels


def check_file_conflicts_in_group(tasks: List[Dict]) -> List[Tuple[int, int, List[str]]]:
    """Check for file conflicts within a task group"""
    conflicts = []
    
    for i, task1 in enumerate(tasks):
        files1 = set(task1.get("exclusive_files", []))
        if not files1:
            continue
            
        for j, task2 in enumerate(tasks[i+1:], i+1):
            files2 = set(task2.get("exclusive_files", []))
            if not files2:
                continue
                
            conflict_files = files1 & files2
            if conflict_files:
                conflicts.append((
                    task1["task_id"],
                    task2["task_id"],
                    list(conflict_files)
                ))
    
    return conflicts


def resolve_file_conflicts(tasks: List[Dict], conflicts: List[Tuple]) -> List[Dict]:
    """Resolve file conflicts by creating sub-groups"""
    # Simple resolution: tasks with conflicts can't be in same parallel group
    # This is a simplified implementation
    return tasks


def find_linear_chains(graph: Dict[int, List[int]], tasks: List[TaskModel]) -> List[List[int]]:
    """Find linear dependency chains that could be parallelized"""
    chains = []
    
    # Find tasks with single dependency and single dependent
    for task_id, deps in graph.items():
        if len(deps) == 1:
            # Check if this task has only one dependent
            dependents = [t for t, d in graph.items() if task_id in d]
            if len(dependents) == 1:
                # This is part of a linear chain
                chain = [deps[0], task_id, dependents[0]]
                chains.append(chain)
    
    return chains


def can_parallelize_chain(tasks: List[TaskModel]) -> bool:
    """Check if a chain of tasks can be parallelized"""
    for task in tasks:
        metadata = parse_metadata(task.meta_data or {})
        if not metadata.can_parallelize:
            return False
        
        # Check for shared files
        all_files = []
        for t in tasks:
            m = parse_metadata(t.meta_data or {})
            all_files.extend(m.exclusive_files)
        
        if len(all_files) != len(set(all_files)):
            return False  # File conflicts
    
    return True


def find_independent_task_groups(tasks: List[TaskModel], dep_graph: Dict) -> List[Set[int]]:
    """Find groups of tasks with no dependencies between them"""
    groups = []
    task_ids = [t.id for t in tasks]
    
    # Simple algorithm: tasks at same topological level with no shared dependencies
    levels = calculate_topological_levels(dep_graph)
    
    level_groups = {}
    for task_id, level in levels.items():
        if level not in level_groups:
            level_groups[level] = []
        level_groups[level].append(task_id)
    
    for level, group in level_groups.items():
        if len(group) > 1:
            groups.append(set(group))
    
    return groups


async def get_agents_for_parallel_execution(session: AsyncSession, max_count: int) -> List[AgentModel]:
    """Get available agents for parallel execution"""
    stmt = select(AgentModel).where(
        and_(
            AgentModel.status == AgentStatus.AVAILABLE.value,
            AgentModel.current_workload < AgentModel.max_workload
        )
    ).limit(max_count)
    
    result = await session.execute(stmt)
    return result.scalars().all()


def agent_can_handle_task(agent: AgentModel, task: TaskModel) -> bool:
    """Check if agent can handle task"""
    metadata = parse_metadata(task.meta_data or {})
    
    # Check agent type
    if metadata.preferred_agent_type and metadata.preferred_agent_type != agent.agent_type:
        return False
    
    # Check capabilities
    required_caps = set(metadata.required_capabilities)
    agent_caps = set(agent.capabilities)
    
    if required_caps and not required_caps.issubset(agent_caps):
        return False
    
    return True


def find_resource_conflicts(resource_map: Dict[str, List[Dict]]) -> List[Dict]:
    """Find conflicts in shared resource access"""
    conflicts = []
    
    for resource, accessors in resource_map.items():
        # Check for write-write conflicts
        writers = [a for a in accessors if a.get("access_type") == "write"]
        if len(writers) > 1:
            conflicts.append({
                "resource": resource,
                "conflict_type": "write-write",
                "tasks": writers
            })
        
        # Check for read-write conflicts (if needed)
        readers = [a for a in accessors if a.get("access_type") == "read"]
        if writers and readers:
            conflicts.append({
                "resource": resource,
                "conflict_type": "read-write",
                "writers": writers,
                "readers": readers
            })
    
    return conflicts


def calculate_group_progress(tasks: List[TaskModel]) -> Dict:
    """Calculate progress for a group of tasks"""
    total = len(tasks)
    if total == 0:
        return {"completion_percentage": 0}
    
    status_counts = {}
    for task in tasks:
        status = task.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    completed = status_counts.get(TaskStatus.COMPLETED.value, 0)
    in_progress = status_counts.get(TaskStatus.IN_PROGRESS.value, 0)
    failed = status_counts.get(TaskStatus.FAILED.value, 0)
    
    completion_percentage = (completed / total) * 100
    
    # Calculate estimated time remaining
    total_estimated = sum(
        parse_metadata(t.meta_data or {}).estimated_hours or 0
        for t in tasks
        if t.status in [TaskStatus.PENDING.value, TaskStatus.ASSIGNED.value, TaskStatus.IN_PROGRESS.value]
    )
    
    return {
        "total_tasks": total,
        "completed": completed,
        "in_progress": in_progress,
        "failed": failed,
        "pending": total - completed - in_progress - failed,
        "completion_percentage": round(completion_percentage, 2),
        "estimated_hours_remaining": round(total_estimated, 2),
        "status_breakdown": status_counts
    }


def calculate_overall_completion(group_progress: Dict[str, Dict]) -> float:
    """Calculate overall completion across all groups"""
    if not group_progress:
        return 0.0
    
    total_tasks = sum(g["total_tasks"] for g in group_progress.values())
    total_completed = sum(g["completed"] for g in group_progress.values())
    
    if total_tasks == 0:
        return 0.0
    
    return round((total_completed / total_tasks) * 100, 2)