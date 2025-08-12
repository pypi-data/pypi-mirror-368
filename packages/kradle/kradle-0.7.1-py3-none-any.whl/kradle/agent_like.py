from typing import Optional, Protocol

from kradle.api.client import KradleAPI
from kradle.models import ChallengeInfo, InitParticipantResponse, Observation, OnEventResponse


class Participant(Protocol):
    """A participant in a challenge.

    Participants are associated with a specific challenge run. Users define an
    agent, and for each challenge run, the agent creates a participant.
    """

    def init_participant(self, challenge_info: ChallengeInfo) -> InitParticipantResponse: ...

    def on_event(self, observation: Observation) -> OnEventResponse: ...

    @property
    def _original_username(self) -> Optional[str]: ...

    @_original_username.setter
    def _original_username(self, username: Optional[str]) -> None: ...


class AgentLike(Protocol):
    """An agent is a kind of factory for participants.

    An agent knows its identity and can create participants.
    """

    @property
    def name(self) -> str:
        """Returns the name of the agent."""
        ...

    @property
    def display_name(self) -> str:
        """Returns the display name of the agent, if different from the name."""
        ...

    @property
    def description(self) -> str:
        """Returns a short description of the agent."""
        ...

    @property
    def _implementation_name(self) -> str:
        """Returns the name of the agent implementation."""
        ...

    def _create_participant(self, api_client: KradleAPI, participant_id: str, run_id: str) -> Participant:
        """Creates a participant that will participate in the challenge."""
        # TODO(wilhuff): Remove api_client when MinecraftAgent is removed.
        ...
