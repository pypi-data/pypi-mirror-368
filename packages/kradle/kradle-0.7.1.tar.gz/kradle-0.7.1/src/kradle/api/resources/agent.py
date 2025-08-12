"""Agent-specific API operations."""

from typing import Any, Optional, TypedDict

from ..http import HTTPClient


AGENT_TYPE_SDK_V0 = "sdk_v0"
AGENT_TYPE_PROMPT = "prompt"


class PromptConfig(TypedDict):
    model: str
    persona: str


class AgentAPI:
    """Agent management API endpoints."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def list(self) -> dict[str, Any]:
        """Get all agents."""
        return self.http.get("agents")

    def get(self, username: str) -> dict[str, Any]:
        """Get agent details by username."""
        return self.http.get(f"agents/{username}")

    def create(
        self,
        username: str,
        name: str,
        description: Optional[str] = None,
        url: Optional[str] = None,
        prompt_config: Optional[PromptConfig] = None,
        visibility: str = "private",
    ) -> dict[str, Any]:
        """Create a new agent."""
        # required
        agent_config = prompt_config or {"url": url}
        agent_type = AGENT_TYPE_PROMPT if prompt_config else AGENT_TYPE_SDK_V0

        data = {
            "username": username,
            "name": name,
            "visibility": visibility,
            "agentConfig": agent_config,
            "agentType": agent_type,
        }
        # optional
        if description is not None:
            data["description"] = description

        return self.http.post("agents", data)

    def update(
        self,
        username: str,
        name: str,
        description: Optional[str] = None,
        url: Optional[str] = None,
        prompt_config: Optional[PromptConfig] = None,
        visibility: str = "private",
    ) -> dict[str, Any]:
        """Update an existing agent."""
        # required
        agent_config = prompt_config or {"url": url}
        agent_type = AGENT_TYPE_PROMPT if prompt_config else AGENT_TYPE_SDK_V0

        data = {
            "username": username,
            "name": name,
            "visibility": visibility,
            "agentConfig": agent_config,
            "agentType": agent_type,
        }
        # optional
        if description is not None:
            data["description"] = description

        return self.http.put(f"agents/{username}", data)

    def delete(self, username: str) -> dict[str, Any]:
        """Delete an agent."""
        return self.http.delete(f"agents/{username}")
