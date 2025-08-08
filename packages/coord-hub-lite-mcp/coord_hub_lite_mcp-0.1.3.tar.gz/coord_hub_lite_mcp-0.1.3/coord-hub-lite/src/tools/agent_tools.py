"""MCP tools for agent management with security integration."""
from typing import List, Optional, Dict, Any
from fastmcp import Context
from src.services.agent_service import AgentService
from src.database.session import get_async_session

# NO AUTHENTICATION - Local MCP server

# NO AUTH REQUIRED
async def register_agent_tool(agent_id: str, agent_type: str, 
                            capabilities: List[str],
                            metadata: Optional[Dict[str, Any]] = None,
                            context: Optional[Context] = None) -> Dict[str, Any]:
    """Register a new agent with the system.
    
    Args:
        agent_id: Unique agent identifier
        agent_type: Type of agent (executor, reviewer, tester, etc.)
        capabilities: List of agent capabilities
        metadata: Optional metadata dictionary
        context: MCP context for logging
        
    Returns:
        Dictionary with agent registration details
    """
    try:
        # Log the registration attempt
        if context:
            await context.info(f"Registering agent {agent_id} of type {agent_type}")
        
        # Validation
        if not agent_id or not agent_id.strip():
            error_msg = "agent_id is required"
            if context:
                await context.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        
        valid_types = ["executor", "reviewer", "tester", "architect", "data-reviewer"]
        if agent_type not in valid_types:
            error_msg = f"Invalid agent_type. Must be one of: {valid_types}"
            if context:
                await context.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        
        # Register agent using session-per-request pattern
        async with get_async_session() as session:
            service = AgentService()
            agent = await service.register_agent(
                session=session,
                agent_id=agent_id.strip(),
                agent_type=agent_type,
                capabilities=capabilities or [],
                metadata=metadata
            )
            
            if context:
                await context.info(f"Successfully registered agent {agent.id}")
            
            # Return standardized response
            return {
                "success": True,
                "data": {
                    "agent_id": agent.id,
                    "agent_type": agent.agent_type,
                    "capabilities": agent.capabilities,
                    "status": agent.status,
                    "metadata": agent.metadata
                }
            }
            
    except Exception as e:
        error_msg = f"Failed to register agent: {str(e)}"
        if context:
            await context.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }


# NO AUTH REQUIRED
async def find_available_agent_tool(required_capabilities: Optional[List[str]] = None,
                                  agent_type: Optional[str] = None,
                                  context: Optional[Context] = None) -> Dict[str, Any]:
    """Find available agents matching the specified criteria.
    
    Args:
        required_capabilities: Optional list of required capabilities
        agent_type: Optional agent type filter
        context: MCP context for logging
        
    Returns:
        Dictionary with list of matching agents
    """
    try:
        # Log the search attempt
        if context:
            capabilities_str = ', '.join(required_capabilities or [])
            await context.info(f"Finding available agents with capabilities: [{capabilities_str}], type: {agent_type}")
        
        # Find agents using session-per-request pattern
        async with get_async_session() as session:
            service = AgentService()
            agents = await service.find_available_agents(
                session=session,
                required_capabilities=required_capabilities,
                agent_type=agent_type
            )
            
            if context:
                await context.debug(f"Found {len(agents)} agents matching criteria")
            
            # Convert agents to response format
            agent_list = []
            for agent in agents:
                agent_list.append({
                    "agent_id": agent.id,
                    "agent_type": agent.agent_type,
                    "capabilities": agent.capabilities,
                    "status": agent.status,
                    "workload": agent.workload,
                    "metadata": agent.metadata
                })
            
            if context:
                await context.info(f"Successfully found {len(agent_list)} available agents")
            
            return {
                "success": True,
                "data": {
                    "agents": agent_list,
                    "count": len(agent_list)
                }
            }
            
    except Exception as e:
        error_msg = f"Failed to find available agents: {str(e)}"
        if context:
            await context.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }