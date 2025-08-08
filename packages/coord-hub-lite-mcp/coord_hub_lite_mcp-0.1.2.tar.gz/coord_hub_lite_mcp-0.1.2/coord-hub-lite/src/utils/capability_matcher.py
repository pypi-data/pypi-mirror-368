"""Capability matching utilities for agent selection."""
from typing import List
from dataclasses import dataclass


@dataclass
class Agent:
    """Agent data class for capability matching."""
    id: str
    agent_type: str = "executor"
    capabilities: List[str] = None
    status: str = "active"
    workload: int = 0
    metadata: dict = None
    last_heartbeat: float = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.metadata is None:
            self.metadata = {}


class CapabilityMatcher:
    """Matches required capabilities to agent capabilities."""
    
    def calculate_match_score(self, agent_capabilities: List[str], 
                            required_capabilities: List[str]) -> float:
        """Calculate match score between agent and required capabilities.
        
        Args:
            agent_capabilities: List of capabilities the agent has
            required_capabilities: List of required capabilities
            
        Returns:
            Float between 0.0 and 1.0 representing match quality
        """
        if not required_capabilities:
            return 1.0  # Any agent matches empty requirements
        
        if not agent_capabilities:
            return 0.0
        
        # Convert to sets for comparison
        agent_set = set(agent_capabilities)
        required_set = set(required_capabilities)
        
        # Calculate match ratio
        matches = agent_set.intersection(required_set)
        return len(matches) / len(required_set)
    
    def rank_agents(self, agents: List[Agent], 
                   required_capabilities: List[str]) -> List[Agent]:
        """Rank agents by match score and workload.
        
        Args:
            agents: List of available agents
            required_capabilities: List of required capabilities
            
        Returns:
            List of agents sorted by best match and lowest workload
        """
        # Filter out inactive and busy agents
        available_agents = [
            agent for agent in agents 
            if agent.status == "active"
        ]
        
        # Calculate scores and sort
        scored_agents = []
        for agent in available_agents:
            score = self.calculate_match_score(
                agent.capabilities, 
                required_capabilities
            )
            # Only include agents with some match
            if score > 0 or not required_capabilities:
                scored_agents.append((score, -agent.workload, agent))
        
        # Sort by score (desc), then workload (asc), then by agent id for stability
        scored_agents.sort(key=lambda x: (x[0], x[1], x[2].id), reverse=True)
        
        # Return just the agents
        return [agent for _, _, agent in scored_agents]