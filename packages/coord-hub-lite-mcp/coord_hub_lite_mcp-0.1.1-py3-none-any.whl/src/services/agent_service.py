"""Agent service for managing agent lifecycle with database persistence."""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.capability_matcher import Agent, CapabilityMatcher
from src.dao.agent_dao import AgentDAO
from src.models.agent import AgentRegister, AgentUpdate, AgentResponse


class AgentService:
    """Service for managing agent registration, heartbeats, and discovery with database persistence."""
    
    def __init__(self):
        self._matcher = CapabilityMatcher()
        self._heartbeat_timeout = timedelta(minutes=5)
        self._max_workload = 3  # Max tasks before agent becomes busy
    
    async def register_agent(self, session: AsyncSession, agent_id: str, agent_type: str,
                           capabilities: List[str], 
                           metadata: Optional[Dict[str, Any]] = None) -> Agent:
        """Register a new agent or update existing one.
        
        Args:
            session: Database session for this operation
            agent_id: Unique agent identifier
            agent_type: Type of agent (executor, reviewer, etc.)
            capabilities: List of agent capabilities
            metadata: Optional metadata
            
        Returns:
            Registered Agent instance
        """
        # Use database DAO for persistence
        dao = AgentDAO(session)
        
        # Create agent registration data
        # Convert string capabilities to AgentCapability enum
        from src.models.agent import AgentCapability
        
        # Map common capability strings to enums
        capability_mapping = {
            'python': AgentCapability.EXECUTOR,
            'web-development': AgentCapability.EXECUTOR,
            'implementation': AgentCapability.EXECUTOR,
            'javascript': AgentCapability.EXECUTOR,
            'frontend': AgentCapability.EXECUTOR,
            'code-review': AgentCapability.REVIEWER,
            'quality-assurance': AgentCapability.REVIEWER,
            'testing': AgentCapability.TESTER,
            'architect': AgentCapability.ARCHITECT,
            'data-review': AgentCapability.DATA_REVIEWER
        }
        
        # Convert capabilities to enums, defaulting based on agent_type
        enum_capabilities = []
        for cap in capabilities:
            if cap in capability_mapping:
                enum_capabilities.append(capability_mapping[cap])
        
        # If no capabilities matched, use agent_type as fallback
        if not enum_capabilities:
            if agent_type == 'executor':
                enum_capabilities = [AgentCapability.EXECUTOR]
            elif agent_type == 'reviewer':
                enum_capabilities = [AgentCapability.REVIEWER]
            elif agent_type == 'tester':
                enum_capabilities = [AgentCapability.TESTER]
            elif agent_type == 'architect':
                enum_capabilities = [AgentCapability.ARCHITECT]
            elif agent_type == 'data-reviewer':
                enum_capabilities = [AgentCapability.DATA_REVIEWER]
            else:
                enum_capabilities = [AgentCapability.EXECUTOR]  # Default fallback
        
        # Remove duplicates
        enum_capabilities = list(set(enum_capabilities))
        
        agent_data = AgentRegister(
            name=agent_id,
            capabilities=enum_capabilities,
            metadata=metadata or {}
        )
        
        try:
            # Register agent in database
            agent_response = await dao.register_agent(agent_data, agent_type)
            
            # Convert to internal Agent format for compatibility
            agent = Agent(
                id=agent_response.id,
                agent_type=agent_response.type,
                capabilities=capabilities,
                status="active",
                workload=0,
                metadata=agent_response.metadata,
                last_heartbeat=datetime.now(timezone.utc).timestamp()
            )
            
            return agent
            
        except ValueError as e:
            if "already exists" in str(e):
                # Agent exists, update heartbeat and return existing
                await dao.update_heartbeat(agent_id)
                existing_response = await self._get_agent_from_db(session, agent_id)
                if existing_response:
                    return Agent(
                        id=existing_response.id,
                        agent_type=existing_response.type,
                        capabilities=capabilities,
                        status="active",
                        workload=0,
                        metadata=existing_response.metadata,
                        last_heartbeat=datetime.now(timezone.utc).timestamp()
                    )
            raise
    
    async def _get_agent_from_db(self, session: AsyncSession, agent_id: str) -> Optional[AgentResponse]:
        """Get agent from database by ID."""
        dao = AgentDAO(session)
        try:
            # Find agent in database
            from sqlalchemy import select
            from src.database.models import Agent as AgentModel
            
            stmt = select(AgentModel).where(AgentModel.id == agent_id)
            result = await session.execute(stmt)
            agent_model = result.scalar_one_or_none()
            
            if agent_model:
                return await dao._to_response(agent_model)
            return None
        except Exception:
            return None
    
    async def get_agent(self, agent_id: str, session: Optional[AsyncSession] = None) -> Optional[Agent]:
        """Get agent by ID.
        
        Args:
            agent_id: Agent identifier
            session: Optional database session for this operation
            
        Returns:
            Agent instance or None if not found
        """
        if not session:
            return None
            
        agent_response = await self._get_agent_from_db(session, agent_id)
        if agent_response:
            # Extract capabilities list from JSON format
            capabilities = []
            if hasattr(agent_response, 'capabilities') and agent_response.capabilities:
                capabilities = [cap.value for cap in agent_response.capabilities]
            
            return Agent(
                id=agent_response.id,
                agent_type=agent_response.type,
                capabilities=capabilities,
                status="active",
                workload=0,
                metadata=agent_response.metadata,
                last_heartbeat=datetime.now(timezone.utc).timestamp()
            )
        return None
    
    async def update_heartbeat(self, agent_id: str, session: Optional[AsyncSession] = None) -> None:
        """Update agent heartbeat timestamp.
        
        Args:
            agent_id: Agent identifier
            session: Optional database session for this operation
        """
        if agent_id in self._agents:
            self._agents[agent_id].last_heartbeat = datetime.now(timezone.utc).timestamp()
            # Reset status to active if it was inactive
            if self._agents[agent_id].status == "inactive":
                self._agents[agent_id].status = "active"
    
    async def check_heartbeat_timeouts(self) -> None:
        """Check and update status of agents with expired heartbeats."""
        current_time = datetime.now(timezone.utc)
        timeout_threshold = self._heartbeat_timeout.total_seconds()
        
        for agent in self._agents.values():
            if agent.status != "inactive":
                # Handle both datetime and timestamp formats
                if isinstance(agent.last_heartbeat, datetime):
                    last_heartbeat = agent.last_heartbeat
                else:
                    last_heartbeat = datetime.fromtimestamp(agent.last_heartbeat)
                
                if (current_time - last_heartbeat).total_seconds() > timeout_threshold:
                    agent.status = "inactive"
    
    async def increment_workload(self, agent_id: str, session: Optional[AsyncSession] = None) -> None:
        """Increment agent workload and update status if needed.
        
        Args:
            agent_id: Agent identifier
            session: Optional database session for this operation
        """
        if agent_id in self._agents:
            agent = self._agents[agent_id]
            agent.workload += 1
            
            # Update status to busy if workload exceeds threshold
            if agent.workload > self._max_workload:
                agent.status = "busy"
    
    async def decrement_workload(self, agent_id: str, session: Optional[AsyncSession] = None) -> None:
        """Decrement agent workload and update status if needed.
        
        Args:
            agent_id: Agent identifier
            session: Optional database session for this operation
        """
        if agent_id in self._agents:
            agent = self._agents[agent_id]
            agent.workload = max(0, agent.workload - 1)
            
            # Update status to active if no longer busy
            if agent.status == "busy" and agent.workload <= self._max_workload:
                agent.status = "active"
    
    async def find_available_agents(self, session: AsyncSession, 
                                  required_capabilities: Optional[List[str]] = None,
                                  agent_type: Optional[str] = None) -> List[Agent]:
        """Find available agents matching criteria.
        
        Args:
            session: Database session for this operation
            required_capabilities: Optional list of required capabilities
            agent_type: Optional agent type filter
            
        Returns:
            List of matching agents sorted by best match and workload
        """
        # Query database for all active agents
        from sqlalchemy import select
        from src.database.models import Agent as AgentModel
        
        stmt = select(AgentModel).where(AgentModel.status == 'active')
        
        # Filter by agent type if specified
        if agent_type:
            stmt = stmt.where(AgentModel.type == agent_type)
        
        result = await session.execute(stmt)
        agent_models = result.scalars().all()
        
        # Convert to internal Agent format
        agents = []
        for agent_model in agent_models:
            # Extract capabilities from JSON format
            capabilities = []
            if agent_model.capabilities and 'list' in agent_model.capabilities:
                capabilities = agent_model.capabilities['list']
            
            agent = Agent(
                id=agent_model.id,
                agent_type=agent_model.type,
                capabilities=capabilities,
                status="active",
                workload=0,  # TODO: Calculate real workload from tasks
                metadata=agent_model.meta_data or {},
                last_heartbeat=datetime.now(timezone.utc).timestamp()
            )
            agents.append(agent)
        
        # Use capability matcher to rank agents
        if required_capabilities:
            return self._matcher.rank_agents(agents, required_capabilities)
        else:
            # Just return active agents sorted by ID for consistency
            return sorted(agents, key=lambda a: a.id)