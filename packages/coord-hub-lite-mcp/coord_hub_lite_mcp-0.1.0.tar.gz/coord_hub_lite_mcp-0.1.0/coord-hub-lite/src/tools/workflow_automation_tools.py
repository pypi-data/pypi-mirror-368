"""MCP tools for workflow automation and orchestration"""
from typing import List, Dict, Optional, Any, Set
from datetime import datetime, timezone
from fastmcp import Context
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Task as TaskModel, Agent as AgentModel
from src.database.session import get_async_session
from src.utils.metadata_utils import parse_metadata, extract_keywords, calculate_task_priority_score
from src.models.task import TaskStatus, TaskPriority
from src.models.agent import AgentStatus


async def auto_assign_ready_tasks(
    project_id: Optional[int] = None,
    max_assignments: int = 10,
    context: Optional[Context] = None
) -> Dict:
    """
    Automatically assign ready tasks to available agents based on capabilities.
    
    Args:
        project_id: Limit to specific project
        max_assignments: Maximum tasks to assign in one run
        
    Returns:
        Assignment results
    """
    async with get_async_session() as session:
        # Get ready tasks
        ready_tasks = await get_ready_tasks_for_assignment(session, project_id)
        
        if not ready_tasks:
            return {
                "success": True,
                "message": "No ready tasks to assign",
                "assignments": []
            }
        
        # Get available agents
        available_agents = await get_available_agents(session)
        
        if not available_agents:
            return {
                "success": True,
                "message": "No available agents",
                "assignments": [],
                "pending_tasks": len(ready_tasks)
            }
        
        # Perform assignments
        assignments = []
        assigned_count = 0
        
        for task in ready_tasks:
            if assigned_count >= max_assignments:
                break
                
            # Find best matching agent
            best_agent = await find_best_agent_for_task(task, available_agents)
            
            if best_agent:
                # Assign task
                task.agent_id = best_agent.id
                task.status = TaskStatus.ASSIGNED.value
                
                # Update task metadata
                metadata = parse_metadata(task.meta_data or {})
                metadata.assigned_at = datetime.now(timezone.utc).isoformat()
                metadata.assignment_method = "auto"
                task.meta_data = metadata.dict()
                
                # Update agent workload
                best_agent.current_workload += 1
                
                assignments.append({
                    "task_id": task.id,
                    "task_title": task.title,
                    "agent_id": best_agent.id,
                    "agent_type": best_agent.agent_type,
                    "match_score": calculate_agent_task_match_score(task, best_agent)
                })
                
                assigned_count += 1
                
                # Remove agent from available list if at capacity
                if best_agent.current_workload >= best_agent.max_workload:
                    available_agents.remove(best_agent)
        
        await session.commit()
        
        return {
            "success": True,
            "assignments": assignments,
            "assigned_count": assigned_count,
            "remaining_tasks": len(ready_tasks) - assigned_count,
            "available_agents_remaining": len(available_agents)
        }


async def process_completion_workflow(
    task_id: int,
    context: Optional[Context] = None
) -> Dict:
    """
    Process the full completion workflow for a task including reviews and follow-ups.
    
    Args:
        task_id: Task that completed
        
    Returns:
        Workflow execution results
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        metadata = parse_metadata(task.meta_data or {})
        workflow_actions = []
        
        # 1. Release file ownership
        if metadata.exclusive_files:
            workflow_actions.append({
                "action": "release_files",
                "status": "completed",
                "files_released": len(metadata.exclusive_files)
            })
            metadata.exclusive_files = []
        
        # 2. Check if review required
        if metadata.review_required and task.status != TaskStatus.NEEDS_REVIEW.value:
            # Create review task
            review_task = await create_review_task(session, task)
            workflow_actions.append({
                "action": "create_review_task",
                "status": "completed",
                "review_task_id": review_task.id
            })
            
            # Update original task status
            task.status = TaskStatus.NEEDS_REVIEW.value
        
        # 3. Unblock dependent tasks
        dependent_tasks = await get_dependent_tasks(session, task_id)
        unblocked_count = 0
        
        for dep_task in dependent_tasks:
            if await check_task_ready(session, dep_task):
                dep_task.status = TaskStatus.PENDING.value
                unblocked_count += 1
        
        if unblocked_count > 0:
            workflow_actions.append({
                "action": "unblock_dependencies",
                "status": "completed",
                "unblocked_count": unblocked_count
            })
        
        # 4. Check phase completion
        if metadata.phase:
            phase_complete = await is_phase_complete(session, metadata.phase, metadata.parent_task_id)
            if phase_complete:
                workflow_actions.append({
                    "action": "phase_completed",
                    "status": "triggered",
                    "phase": metadata.phase
                })
        
        # 5. Update agent workload
        if task.agent_id:
            agent_stmt = select(AgentModel).where(AgentModel.id == task.agent_id)
            agent_result = await session.execute(agent_stmt)
            agent = agent_result.scalar_one_or_none()
            if agent and agent.current_workload > 0:
                agent.current_workload -= 1
        
        task.meta_data = metadata.dict()
        await session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "workflow_actions": workflow_actions,
            "total_actions": len(workflow_actions)
        }


async def create_task_batch(
    tasks: List[Dict[str, Any]],
    project_id: int,
    phase: Optional[str] = None,
    auto_assign: bool = True,
    context: Optional[Context] = None
) -> Dict:
    """
    Create multiple related tasks as a batch with dependencies.
    
    Args:
        tasks: List of task definitions with dependencies
        project_id: Parent project ID
        phase: Optional phase name
        auto_assign: Whether to auto-assign after creation
        
    Returns:
        Batch creation results
    """
    async with get_async_session() as session:
        created_tasks = []
        task_id_map = {}  # Map from temp IDs to real IDs
        
        # First pass: Create all tasks
        for idx, task_def in enumerate(tasks):
            # Extract task data
            temp_id = task_def.get("temp_id", f"temp_{idx}")
            
            task_metadata = {
                "parent_task_id": project_id,
                "phase": phase,
                "batch_created": True,
                "created_in_batch": datetime.now(timezone.utc).isoformat(),
                **task_def.get("metadata", {})
            }
            
            # Create task
            task = TaskModel(
                title=task_def["title"],
                description=task_def["description"],
                priority=task_def.get("priority", "medium"),
                status=TaskStatus.PENDING.value,
                meta_data=task_metadata
            )
            
            session.add(task)
            await session.flush()  # Get the ID
            
            created_tasks.append(task)
            task_id_map[temp_id] = task.id
        
        # Second pass: Set dependencies using real IDs
        for idx, task_def in enumerate(tasks):
            if "depends_on" in task_def:
                task = created_tasks[idx]
                metadata = parse_metadata(task.meta_data)
                
                # Convert temp IDs to real IDs
                real_deps = []
                for dep in task_def["depends_on"]:
                    if dep in task_id_map:
                        real_deps.append(task_id_map[dep])
                    elif isinstance(dep, int):
                        real_deps.append(dep)  # Already a real ID
                
                metadata.depends_on = real_deps
                task.meta_data = metadata.dict()
        
        await session.commit()
        
        # Auto-assign if requested
        assignments = []
        if auto_assign:
            for task in created_tasks:
                metadata = parse_metadata(task.meta_data)
                if not metadata.depends_on:  # Only assign tasks with no dependencies
                    agent = await find_available_agent_for_task(session, task)
                    if agent:
                        task.agent_id = agent.id
                        task.status = TaskStatus.ASSIGNED.value
                        agent.current_workload += 1
                        
                        assignments.append({
                            "task_id": task.id,
                            "agent_id": agent.id
                        })
            
            await session.commit()
        
        return {
            "success": True,
            "created_count": len(created_tasks),
            "task_ids": [t.id for t in created_tasks],
            "task_id_map": task_id_map,
            "auto_assigned": len(assignments),
            "assignments": assignments
        }


async def cascade_task_cancellation(
    task_id: int,
    reason: str,
    cancel_dependents: bool = True,
    context: Optional[Context] = None
) -> Dict:
    """
    Cancel a task and optionally cascade to dependent tasks.
    
    Args:
        task_id: Task to cancel
        reason: Cancellation reason
        cancel_dependents: Whether to cancel dependent tasks
        
    Returns:
        Cancellation results
    """
    async with get_async_session() as session:
        # Get the task
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        cancelled_tasks = []
        
        # Cancel the main task
        if task.status not in [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]:
            task.status = TaskStatus.CANCELLED.value
            
            metadata = parse_metadata(task.meta_data or {})
            metadata.cancellation_reason = reason
            metadata.cancelled_at = datetime.now(timezone.utc).isoformat()
            task.meta_data = metadata.dict()
            
            # Release resources
            if metadata.exclusive_files:
                metadata.exclusive_files = []
            
            # Update agent workload
            if task.agent_id:
                agent_stmt = select(AgentModel).where(AgentModel.id == task.agent_id)
                agent_result = await session.execute(agent_stmt)
                agent = agent_result.scalar_one_or_none()
                if agent and agent.current_workload > 0:
                    agent.current_workload -= 1
            
            cancelled_tasks.append({
                "task_id": task.id,
                "task_title": task.title,
                "previous_status": task.status
            })
        
        # Cancel dependent tasks if requested
        if cancel_dependents:
            dependent_tasks = await get_all_dependent_tasks(session, task_id)
            
            for dep_task in dependent_tasks:
                if dep_task.status not in [TaskStatus.COMPLETED.value, TaskStatus.CANCELLED.value]:
                    dep_task.status = TaskStatus.CANCELLED.value
                    
                    dep_metadata = parse_metadata(dep_task.meta_data or {})
                    dep_metadata.cancellation_reason = f"Parent task #{task_id} cancelled: {reason}"
                    dep_metadata.cancelled_at = datetime.now(timezone.utc).isoformat()
                    dep_metadata.cascade_cancelled = True
                    dep_task.meta_data = dep_metadata.dict()
                    
                    cancelled_tasks.append({
                        "task_id": dep_task.id,
                        "task_title": dep_task.title,
                        "previous_status": dep_task.status
                    })
        
        await session.commit()
        
        return {
            "success": True,
            "primary_task_id": task_id,
            "cancelled_count": len(cancelled_tasks),
            "cancelled_tasks": cancelled_tasks,
            "cascade_applied": cancel_dependents
        }


async def rebalance_agent_workload(
    context: Optional[Context] = None
) -> Dict:
    """
    Rebalance task assignments across available agents.
    
    Returns:
        Rebalancing results
    """
    async with get_async_session() as session:
        # Get all agents and their workloads
        agent_stmt = select(AgentModel).where(
            AgentModel.status == AgentStatus.AVAILABLE.value
        )
        agent_result = await session.execute(agent_stmt)
        agents = agent_result.scalars().all()
        
        if not agents:
            return {
                "success": True,
                "message": "No available agents",
                "reassignments": []
            }
        
        # Calculate average workload
        total_workload = sum(agent.current_workload for agent in agents)
        avg_workload = total_workload / len(agents)
        
        reassignments = []
        
        # Find overloaded and underloaded agents
        overloaded = [a for a in agents if a.current_workload > avg_workload + 1]
        underloaded = [a for a in agents if a.current_workload < avg_workload - 1]
        
        # Reassign tasks from overloaded to underloaded agents
        for over_agent in overloaded:
            if not underloaded:
                break
                
            # Get assigned tasks for overloaded agent
            task_stmt = select(TaskModel).where(
                and_(
                    TaskModel.agent_id == over_agent.id,
                    TaskModel.status == TaskStatus.ASSIGNED.value
                )
            )
            task_result = await session.execute(task_stmt)
            tasks = task_result.scalars().all()
            
            # Reassign tasks to underloaded agents
            for task in tasks:
                if not underloaded:
                    break
                    
                # Find best underloaded agent for task
                best_under = find_best_match(task, underloaded)
                
                if best_under:
                    # Reassign
                    task.agent_id = best_under.id
                    over_agent.current_workload -= 1
                    best_under.current_workload += 1
                    
                    reassignments.append({
                        "task_id": task.id,
                        "task_title": task.title,
                        "from_agent": over_agent.id,
                        "to_agent": best_under.id
                    })
                    
                    # Update underloaded list
                    if best_under.current_workload >= avg_workload:
                        underloaded.remove(best_under)
                    
                    # Stop if agent is balanced
                    if over_agent.current_workload <= avg_workload:
                        break
        
        await session.commit()
        
        return {
            "success": True,
            "total_agents": len(agents),
            "average_workload": round(avg_workload, 2),
            "reassignments": reassignments,
            "reassignment_count": len(reassignments)
        }


# Helper functions

async def get_ready_tasks_for_assignment(session: AsyncSession, project_id: Optional[int]) -> List[TaskModel]:
    """Get tasks ready for assignment"""
    stmt = select(TaskModel).where(
        and_(
            TaskModel.status == TaskStatus.PENDING.value,
            TaskModel.agent_id == None
        )
    )
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    
    # Filter by project if specified
    if project_id:
        tasks = [t for t in tasks if parse_metadata(t.meta_data or {}).parent_task_id == project_id]
    
    # Filter by dependency readiness
    ready_tasks = []
    for task in tasks:
        metadata = parse_metadata(task.meta_data or {})
        if await are_dependencies_complete(session, metadata.depends_on):
            ready_tasks.append(task)
    
    return ready_tasks


async def get_available_agents(session: AsyncSession) -> List[AgentModel]:
    """Get agents available for assignment"""
    stmt = select(AgentModel).where(
        and_(
            AgentModel.status == AgentStatus.AVAILABLE.value,
            AgentModel.current_workload < AgentModel.max_workload
        )
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def find_best_agent_for_task(task: TaskModel, agents: List[AgentModel]) -> Optional[AgentModel]:
    """Find the best matching agent for a task"""
    metadata = parse_metadata(task.meta_data or {})
    
    # Extract required capabilities
    required_caps = set(metadata.required_capabilities)
    if metadata.preferred_agent_type:
        required_caps.add(metadata.preferred_agent_type)
    
    # Add capabilities from task description
    keywords = extract_keywords(f"{task.title} {task.description}")
    required_caps.update(keywords)
    
    best_agent = None
    best_score = 0
    
    for agent in agents:
        score = calculate_agent_task_match_score(task, agent)
        if score > best_score:
            best_score = score
            best_agent = agent
    
    return best_agent if best_score > 0.5 else None


def calculate_agent_task_match_score(task: TaskModel, agent: AgentModel) -> float:
    """Calculate match score between task and agent"""
    metadata = parse_metadata(task.meta_data or {})
    
    score = 0.0
    
    # Check agent type match
    if metadata.preferred_agent_type == agent.agent_type:
        score += 0.5
    
    # Check capability matches
    required_caps = set(metadata.required_capabilities)
    agent_caps = set(agent.capabilities)
    
    if required_caps:
        capability_match = len(required_caps & agent_caps) / len(required_caps)
        score += capability_match * 0.3
    
    # Check workload
    workload_ratio = agent.current_workload / agent.max_workload
    score += (1 - workload_ratio) * 0.2
    
    return score


async def are_dependencies_complete(session: AsyncSession, dependency_ids: List[int]) -> bool:
    """Check if all dependencies are complete"""
    if not dependency_ids:
        return True
    
    stmt = select(TaskModel).where(TaskModel.id.in_(dependency_ids))
    result = await session.execute(stmt)
    deps = result.scalars().all()
    
    return all(d.status == TaskStatus.COMPLETED.value for d in deps)


async def get_dependent_tasks(session: AsyncSession, task_id: int) -> List[TaskModel]:
    """Get tasks that directly depend on this task"""
    stmt = select(TaskModel)
    result = await session.execute(stmt)
    all_tasks = result.scalars().all()
    
    dependent = []
    for task in all_tasks:
        metadata = parse_metadata(task.meta_data or {})
        if task_id in metadata.depends_on:
            dependent.append(task)
    
    return dependent


async def get_all_dependent_tasks(session: AsyncSession, task_id: int) -> List[TaskModel]:
    """Get all tasks in the dependency tree"""
    all_dependent = set()
    to_check = [task_id]
    
    while to_check:
        current_id = to_check.pop(0)
        direct_deps = await get_dependent_tasks(session, current_id)
        
        for dep in direct_deps:
            if dep.id not in all_dependent:
                all_dependent.add(dep.id)
                to_check.append(dep.id)
    
    # Fetch all dependent tasks
    if all_dependent:
        stmt = select(TaskModel).where(TaskModel.id.in_(all_dependent))
        result = await session.execute(stmt)
        return result.scalars().all()
    
    return []


async def check_task_ready(session: AsyncSession, task: TaskModel) -> bool:
    """Check if a task is ready to run"""
    metadata = parse_metadata(task.meta_data or {})
    return await are_dependencies_complete(session, metadata.depends_on)


async def is_phase_complete(session: AsyncSession, phase: str, project_id: int) -> bool:
    """Check if all tasks in a phase are complete"""
    stmt = select(TaskModel)
    result = await session.execute(stmt)
    all_tasks = result.scalars().all()
    
    phase_tasks = [
        t for t in all_tasks
        if parse_metadata(t.meta_data or {}).phase == phase
        and parse_metadata(t.meta_data or {}).parent_task_id == project_id
    ]
    
    return all(t.status == TaskStatus.COMPLETED.value for t in phase_tasks)


async def create_review_task(session: AsyncSession, original_task: TaskModel) -> TaskModel:
    """Create a review task for the original task"""
    metadata = parse_metadata(original_task.meta_data or {})
    
    review_task = TaskModel(
        title=f"Review: {original_task.title}",
        description=f"Review {metadata.review_type or 'code'} for task #{original_task.id}",
        priority=original_task.priority,
        status=TaskStatus.PENDING.value,
        meta_data={
            "parent_task_id": metadata.parent_task_id,
            "original_task_id": original_task.id,
            "is_review_task": True,
            "review_type": metadata.review_type or "code_review",
            "preferred_agent_type": "reviewer",
            "required_capabilities": ["review", metadata.review_type or "code_review"]
        }
    )
    
    session.add(review_task)
    await session.flush()
    return review_task


async def find_available_agent_for_task(session: AsyncSession, task: TaskModel) -> Optional[AgentModel]:
    """Find an available agent for a specific task"""
    agents = await get_available_agents(session)
    return await find_best_agent_for_task(task, agents)


def find_best_match(task: TaskModel, agents: List[AgentModel]) -> Optional[AgentModel]:
    """Find best matching agent from a list"""
    best_agent = None
    best_score = 0
    
    for agent in agents:
        score = calculate_agent_task_match_score(task, agent)
        if score > best_score:
            best_score = score
            best_agent = agent
    
    return best_agent