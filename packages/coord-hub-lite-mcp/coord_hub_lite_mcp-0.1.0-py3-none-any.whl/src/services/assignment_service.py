"""
Assignment service for task-agent assignment logic.
Handles capability matching, workload checking, and atomic assignment.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.database.models import Task, Agent, TaskEvent


class AssignmentService:
    """Service for managing task assignments to agents."""
    
    async def assign_task(
        self,
        session: AsyncSession,
        task_id: int,
        agent_id: str,
        check_capabilities: bool = True
    ) -> Dict[str, Any]:
        """
        Assign a task to an agent with validation.
        
        Args:
            session: Database session
            task_id: ID of task to assign
            agent_id: ID of agent to assign to
            check_capabilities: Whether to validate agent capabilities
            
        Returns:
            Result dict with success status and details
        """
        try:
            # Get task and agent
            task = await session.get(Task, task_id)
            if not task:
                return {
                    'success': False,
                    'error': f'Task {task_id} not found'
                }
            
            agent = await session.get(Agent, agent_id)
            if not agent:
                return {
                    'success': False,
                    'error': f'Agent {agent_id} not found'
                }
            
            # Check if task is already assigned
            if task.agent_id:
                return {
                    'success': False,
                    'error': f'Task already assigned to {task.agent_id}'
                }
            
            # Check if task is in assignable state
            if task.status not in ['pending', 'failed']:
                return {
                    'success': False,
                    'error': f'Task is not in assignable state (current: {task.status})'
                }
            
            # Check agent availability
            if agent.status not in ['active', 'inactive']:
                return {
                    'success': False,
                    'error': f'Agent is not available (status: {agent.status})'
                }
            
            # Check capabilities if requested
            if check_capabilities:
                capability_result = self._check_capabilities(task, agent)
                if not capability_result['match']:
                    return {
                        'success': False,
                        'error': capability_result['reason']
                    }
            
            # Check workload
            is_overloaded = await self.is_agent_overloaded(
                session, 
                agent_id,
                max_tasks=agent.capabilities.get('max_concurrent_tasks', 5)
            )
            if is_overloaded:
                return {
                    'success': False,
                    'error': 'Agent is at maximum workload capacity'
                }
            
            # Perform assignment
            task.agent_id = agent_id
            task.status = 'assigned'
            task.updated_at = datetime.now(timezone.utc)
            
            # Create audit event
            event = TaskEvent(
                task_id=task_id,
                event_type='assignment',
                old_value=None,
                new_value=agent_id,
                actor='system',
                meta_data={
                    'capabilities_checked': check_capabilities,
                    'agent_status': agent.status
                }
            )
            session.add(event)
            
            # Update agent status if needed
            if agent.status == 'inactive':
                agent.status = 'active'
            
            # Commit changes
            await session.commit()
            
            return {
                'success': True,
                'task_id': task_id,
                'agent_id': agent_id,
                'message': f'Task {task_id} assigned to {agent_id}'
            }
            
        except Exception as e:
            await session.rollback()
            return {
                'success': False,
                'error': f'Assignment failed: {str(e)}'
            }
    
    def _check_capabilities(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """
        Check if agent has required capabilities for task.
        
        Args:
            task: Task with potential required_skills in metadata
            agent: Agent with capabilities
            
        Returns:
            Dict with 'match' bool and 'reason' if no match
        """
        # Get required skills from task metadata
        required_skills = task.meta_data.get('required_skills', [])
        if not required_skills:
            return {'match': True}
        
        # Get agent skills
        agent_skills = agent.capabilities.get('skills', [])
        
        # Check if all required skills are present
        missing_skills = [skill for skill in required_skills if skill not in agent_skills]
        
        if missing_skills:
            return {
                'match': False,
                'reason': f'Missing required skills: {", ".join(missing_skills)}'
            }
        
        return {'match': True}
    
    async def is_agent_overloaded(
        self,
        session: AsyncSession,
        agent_id: str,
        max_tasks: int = 5
    ) -> bool:
        """
        Check if agent has too many active tasks.
        
        Args:
            session: Database session
            agent_id: Agent to check
            max_tasks: Maximum concurrent tasks allowed
            
        Returns:
            True if agent is at or over capacity
        """
        # Count active tasks for agent
        stmt = select(Task).where(
            and_(
                Task.agent_id == agent_id,
                Task.status.in_(['assigned', 'in_progress'])
            )
        )
        result = await session.execute(stmt)
        active_tasks = result.scalars().all()
        
        return len(active_tasks) >= max_tasks
    
    async def get_agent_workload(
        self,
        session: AsyncSession,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed workload information for an agent.
        
        Args:
            session: Database session
            agent_id: Agent to check
            
        Returns:
            Workload details including task counts by status
        """
        # Get all tasks for agent
        stmt = select(Task).where(Task.agent_id == agent_id)
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        
        # Count by status
        status_counts = {}
        for task in tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
        
        return {
            'agent_id': agent_id,
            'total_tasks': len(tasks),
            'active_tasks': status_counts.get('assigned', 0) + status_counts.get('in_progress', 0),
            'completed_tasks': status_counts.get('completed', 0),
            'failed_tasks': status_counts.get('failed', 0),
            'status_breakdown': status_counts
        }