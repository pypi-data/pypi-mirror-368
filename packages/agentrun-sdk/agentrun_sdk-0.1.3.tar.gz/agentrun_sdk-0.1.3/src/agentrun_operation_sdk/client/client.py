import json
import logging
from typing import Any, Dict, Iterator, Optional
from pydantic import BaseModel, Field
from ..services.runtime import generate_session_id, LocalAgentRunClient, AgentRunClient

log = logging.getLogger(__name__)


class InvokeResult(BaseModel):
    """Result of invoke operation."""

    response: Dict[str, Any] = Field(..., description="Response from Agentrun endpoint")
    session_id: str = Field(..., description="Session ID used for invocation")


class Session:
    def __init__(self, session_id: str, 
                 local_mode: Optional[bool] = False, 
                 agent_id: Optional[str] = None,
                 stream: Optional[bool] = False,
                 region: Optional[str] = "cn-north-4"):
        self.session_id = session_id
        self.agent_id = agent_id
        self.local_mode = local_mode
        self.stream = stream
        self.region = region

    def invoke(
            self,
            payload: Any
    ) -> InvokeResult:
        """Invoke deployed Bedrock AgentCore endpoint."""
        mode = "locally" if self.local_mode else "via cloud endpoint"
        log.info("Invoking BedrockAgentCore agent '%s' %s", self.agent_id, mode)
        if not self.session_id:
            self.session_id = generate_session_id()

        if isinstance(payload, dict):
            payload_str = json.dumps(payload, ensure_ascii=False)
        else:
            payload_str = str(payload)

        if self.local_mode:
            client = LocalAgentRunClient("http://0.0.0.0:8080")
            response = client.invoke_endpoint(self.session_id, payload_str, self.stream)
        else:
            client = AgentRunClient(self.region)
            response = client.invoke_endpoint(
                agent_id=self.agent_id,
                payload=payload_str,
                session_id=self.session_id,
                stream=self.stream
            )
        return InvokeResult(
            response=response,
            session_id=self.session_id
        )

class Client:
    def __init__(self, local_mode: Optional[bool] = True, 
                 stream: Optional[bool] = True, 
                 region: Optional[str] = "cn-north-4"):
        self.session_id = generate_session_id()
        self.local_mode = local_mode
        self.stream = stream
        self.region = region

    def get_or_create_session(self, agent_id: str) -> Session:
        session = Session(self.session_id, 
                          self.local_mode, 
                          agent_id,
                          stream=self.stream,
                          region=self.region)
        return session