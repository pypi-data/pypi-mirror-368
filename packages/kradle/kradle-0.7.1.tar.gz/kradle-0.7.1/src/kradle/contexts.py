from typing import Any, Optional, TypeVar, Union

from kradle.api.client import KradleAPI
from kradle.models import ChallengeInfo


def make_agent_key(participant_id: str, run_id: str) -> str:
    """Creates a consistent key for identifying a run instance."""
    return f"{run_id}:{participant_id}"


# Type variable for generic default in Context.get
_T = TypeVar("_T")


class Context:
    """A participant's context for a specific challenge run.

    During a run, each participant gets their own Context object. This object
    can be used to store arbitrary data associated with the specific participant
    for the duration of the run.

    Context objects are managed by the Kradle SDK. They are created on demand
    just before the run starts and are automatically deleted after the run ends.
    """

    def __init__(self, agent_key: str):
        assert agent_key
        self.agent_key = agent_key

        self._challenge_info: Optional[ChallengeInfo] = None
        self._original_username: Optional[str] = None
        self.user_data: dict[str, Any] = {}
        self.api_client: Optional[KradleAPI] = None

    @property
    def challenge_info(self) -> ChallengeInfo:
        """Returns this participant's challenge info for this run."""
        assert self._challenge_info is not None
        return self._challenge_info

    @property
    def participant_id(self) -> str:
        return self.challenge_info.participant_id

    @property
    def run_id(self) -> str:
        return self.challenge_info.run_id

    def log(self, message: Any) -> None:
        assert self.api_client is not None
        self.api_client.logs.create(
            run_id=self.run_id,
            participant_id=self.participant_id,
            message=message,
        )

    def __getitem__(self, key: str) -> Any:
        return self.user_data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.user_data[key] = value

    def __delitem__(self, key: str) -> None:
        del self.user_data[key]

    def __contains__(self, key: str) -> bool:
        return key in self.user_data

    def get(self, key: str, default: Optional[_T] = None) -> Optional[Union[Any, _T]]:
        return self.user_data.get(key, default)

    def update(self, data: dict[str, Any]) -> None:
        self.user_data.update(data)


class ContextManager:
    """Manages a collection of Context instances, keyed by agent_key."""

    def __init__(self) -> None:
        self._contexts: dict[str, Context] = {}

    def get_or_create(self, agent_key: str) -> Context:
        """Retrieves an existing Context or creates a new one if not found."""
        if agent_key not in self._contexts:
            self._contexts[agent_key] = Context(agent_key)
        return self._contexts[agent_key]

    def get(self, agent_key: str) -> Optional[Context]:
        """Gets a context by agent_key if it exists."""
        return self._contexts.get(agent_key)

    def clear(self, agent_key: str) -> None:
        """Removes a context from the manager."""
        if agent_key in self._contexts:
            del self._contexts[agent_key]

    def clear_all(self) -> None:
        """Clears all stored contexts."""
        self._contexts.clear()


# Global context manager instance
context_manager = ContextManager()
