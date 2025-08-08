"""Agent Data Access Object"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.dao.base import BaseDAO
from src.database.models import Agent as AgentModel
from src.models.agent import AgentRegister, AgentUpdate, AgentResponse, AgentStatus, AgentCapability
from src.models.task import TaskStatus


class AgentDAO(BaseDAO[AgentModel]):
    """Data Access Object for Agent operations"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AgentModel)
    
    async def register_agent(self, agent_data: AgentRegister, agent_type: str = 'executor') -> AgentResponse:
        """Register a new agent"""
        try:
            # Convert capabilities to the database format
            capabilities_dict = agent_data.to_db_capabilities()
            
            # Create agent model - using agent name as ID
            agent = AgentModel(
                id=agent_data.name,  # Use agent name as ID per database design
                name=agent_data.name,
                type=agent_type,  # Use passed agent type
                status='active',  # Use string status matching database constraints
                capabilities=capabilities_dict,
                meta_data=agent_data.metadata,
                last_heartbeat=datetime.now(timezone.utc)
            )
            
            await self.add(agent)
            await self.flush()
            
            return await self._to_response(agent)
            
        except IntegrityError as e:
            await self.rollback()
            if "unique" in str(e).lower():
                raise ValueError(f"Agent with name {agent_data.name} already exists")
            raise
        except Exception as e:
            await self.rollback()
            self.handle_error(e, "register_agent")
    
    async def update_heartbeat(self, agent_id: str) -> AgentResponse:
        """Update agent heartbeat timestamp"""
        try:
            # Fetch agent first
            stmt = select(AgentModel).where(AgentModel.id == agent_id)
            result = await self.session.execute(stmt)
            agent = result.scalar_one_or_none()
            
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Update heartbeat
            agent.last_heartbeat = datetime.now(timezone.utc)
            
            await self.flush()
            
            return await self._to_response(agent)
            
        except Exception as e:
            await self.rollback()
            self.handle_error(e, "update_heartbeat")
    
    async def update_agent(self, agent_id: str, update_data: AgentUpdate) -> AgentResponse:
        """Update agent status and metadata"""
        try:
            # Fetch agent
            stmt = select(AgentModel).where(AgentModel.id == agent_id)
            result = await self.session.execute(stmt)
            agent = result.scalar_one_or_none()
            
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Check if agent can be assigned (for concurrent access)
            if update_data.status == AgentStatus.BUSY:
                if agent.status != AgentStatus.AVAILABLE:
                    raise ValueError(f"Agent {agent_id} is not available")
                if not update_data.current_task:
                    raise ValueError("Cannot set agent to BUSY without a task")
            
            # Update fields
            if update_data.status is not None:
                agent.status = update_data.status
            
            if update_data.current_task is not None:
                agent.current_task = update_data.current_task
            elif update_data.status == AgentStatus.AVAILABLE:
                agent.current_task = None
            
            if update_data.metadata is not None:
                agent.meta_data = {**agent.meta_data, **update_data.metadata}
            
            await self.flush()
            return await self._to_response(agent)
            
        except Exception as e:
            await self.rollback()
            self.handle_error(e, "update_agent")
    
    async def find_available_agents(self, capability: AgentCapability, limit: Optional[int] = None) -> List[AgentResponse]:
        """Find available agents with specific capability"""
        try:
            # Query agents that have the capability in their JSON capabilities field
            # For SQLite, we need to handle JSON differently
            stmt = (
                select(AgentModel)
                .where(
                    AgentModel.status == 'active'  # Use string status matching database constraint
                )
                .order_by(AgentModel.last_heartbeat.desc())
            )
            
            if limit:
                stmt = stmt.limit(limit)
            
            result = await self.session.execute(stmt)
            agents = result.scalars().all()
            
            # Filter agents that have the requested capability
            filtered_agents = []
            for agent in agents:
                agent_capabilities = agent.capabilities.get('list', []) if agent.capabilities else []
                if capability.value in agent_capabilities:
                    filtered_agents.append(agent)
            
            return [await self._to_response(agent) for agent in filtered_agents]
            
        except Exception as e:
            self.handle_error(e, "find_available_agents")
    
    async def get_agent_workload(self, agent_id: str) -> Dict[str, Any]:
        """Get agent workload statistics"""
        try:
            # Fetch agent
            stmt = select(AgentModel).where(AgentModel.id == agent_id)
            result = await self.session.execute(stmt)
            agent = result.scalar_one_or_none()
            
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Count tasks by status
            from src.database.models import Task as TaskModel
            
            task_counts_stmt = (
                select(
                    TaskModel.status,
                    func.count(TaskModel.id)
                )
                .where(TaskModel.agent_id == agent_id)
                .group_by(TaskModel.status)
            )
            
            task_counts_result = await self.session.execute(task_counts_stmt)
            task_counts = dict(task_counts_result.all())
            
            # Calculate statistics
            total_tasks = sum(task_counts.values())
            completed_tasks = task_counts.get('completed', 0)  # Use string status values
            failed_tasks = task_counts.get('failed', 0)
            active_tasks = task_counts.get('in_progress', 0) + task_counts.get('pending', 0)
            
            # Calculate success rate
            finished_tasks = completed_tasks + failed_tasks
            success_rate = (completed_tasks / finished_tasks * 100.0) if finished_tasks > 0 else 100.0
            
            return {
                "agent_id": agent_id,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "active_tasks": active_tasks,
                "success_rate": success_rate,
                "task_breakdown": {
                    status.value: count 
                    for status, count in task_counts.items()
                }
            }
            
        except Exception as e:
            self.handle_error(e, "get_agent_workload")
    
    async def _to_response(self, agent: AgentModel) -> AgentResponse:
        """Convert AgentModel to AgentResponse"""
        # Capabilities are stored as JSON in the agent model with 'roles' key
        capabilities = agent.capabilities.get('roles', []) if agent.capabilities else []
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            status=AgentStatus(agent.status) if agent.status in [s.value for s in AgentStatus] else AgentStatus.ACTIVE,
            capabilities=[AgentCapability(cap) for cap in capabilities if cap in [c.value for c in AgentCapability]],
            created_at=agent.created_at,
            last_heartbeat=agent.last_heartbeat,
            current_task=None,  # These fields don't exist in the database model
            completed_tasks=0,   # Would need to be calculated from task history
            failed_tasks=0,      # Would need to be calculated from task history
            metadata=agent.meta_data or {}
        )
    
    async def get_available_agents(self, limit: int = 10) -> List[AgentResponse]:
        """Get available agents (status = 'active' or 'inactive')
        
        Args:
            limit: Maximum number of agents to return
            
        Returns:
            List of available agents
        """
        stmt = (
            select(AgentModel)
            .where(or_(
                AgentModel.status == 'active',
                AgentModel.status == 'inactive'
            ))
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        agents = result.scalars().all()
        
        return [await self._to_response(agent) for agent in agents]
    
    async def get_agents_by_status(
        self,
        status: str,
        limit: int = 10
    ) -> List[AgentResponse]:
        """Get agents by status
        
        Args:
            status: Agent status to filter by
            limit: Maximum number of agents to return
            
        Returns:
            List of agents with the specified status
        """
        stmt = (
            select(AgentModel)
            .where(AgentModel.status == status)
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        agents = result.scalars().all()
        
        return [await self._to_response(agent) for agent in agents]