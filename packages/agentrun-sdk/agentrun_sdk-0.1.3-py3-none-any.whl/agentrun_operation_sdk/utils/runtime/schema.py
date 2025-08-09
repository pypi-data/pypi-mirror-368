from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class AgentRunAgentSchema(BaseModel):
    name: str = Field(..., description="Name of the AgentRun application")
    entrypoint: str = Field(..., description="Entrypoint file path")
    platform: str = Field(default="linux/amd64", description="Target platform")
    container_runtime: str = Field(default="docker", description="Container runtime to use")
   
    def validate(self, for_local: bool = False) -> List[str]:
        """Validate configuration and return list of errors.

        Args:
            for_local: Whether validating for local deployment

        Returns:
            List of validation error messages
        """
        errors = []

        # Required fields for all deployments
        if not self.name:
            errors.append("Missing 'name' field")
        if not self.entrypoint:
            errors.append("Missing 'entrypoint' field")

        return errors
    
class AgentRunConfigSchema(BaseModel):
    default_agent: Optional[str] = Field(default=None, description="Default agent name for operations")
    agents: Dict[str, AgentRunAgentSchema] = Field(
        default_factory=dict, description="Named agent configurations"
    )

    def get_agent_config(self, agent_name: Optional[str] = None) -> AgentRunAgentSchema:
        """Get agent config by name or default.

        Args:
            agent_name: Agent name from --agent parameter, or None for default
        """
        target_name = agent_name or self.default_agent
        if not target_name:
            if len(self.agents) == 1:
                agent = list(self.agents.values())[0]
                self.default_agent = agent.name
                return agent
            raise ValueError("No agent specified and no default set")

        if target_name not in self.agents:
            available = list(self.agents.keys())
            if available:
                raise ValueError(f"Agent '{target_name}' not found. Available agents: {available}")
            else:
                raise ValueError("No agents configured")

        return self.agents[target_name]