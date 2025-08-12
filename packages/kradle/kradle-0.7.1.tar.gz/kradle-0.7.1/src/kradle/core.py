"""
Core implementation of the Kradle Minecraft agent.
"""

from typing import Optional
from rich.console import Console
from kradle.models import (
    ChallengeInfo,
    InitParticipantResponse,
    Observation,
    OnEventResponse,
)
from kradle.memory.standard_memory import StandardMemory
from kradle.api.client import KradleAPI


class MinecraftAgent:
    """Base class for Kradle Minecraft agents"""

    username: str = "minecraft-agent"  # Default username for the agent
    display_name: str = "Minecraft Agent"  # Default display name for the agent
    description: str = "A Minecraft agent created by the Kradle Python SDK"  # Default description for the agent

    def __init__(
        self,
        api_client: KradleAPI,
        participant_id: Optional[str] = None,
        run_id: Optional[str] = None,
        # IMPORTANT: Using None instead of StandardMemory() as the default value
        # to avoid the "mutable default argument" problem in Python.
        # If we used StandardMemory() here, all agents would share the same memory instance,
        # causing unexpected memory sharing between different agents/sessions.
        memory: Optional[StandardMemory] = None,
        action_delay: int = 100,
    ):
        # Basic configuration
        self.action_delay = action_delay
        self.console = Console()

        # State management
        self.participant_id: Optional[str] = participant_id
        self.run_id: Optional[str] = run_id

        # Create memory with proper namespacing
        if memory is not None:
            self.memory = memory
        else:
            self.memory = StandardMemory(participant_id=participant_id, run_id=run_id)
            # If we have both run_id and participant_id, save them to memory
            if participant_id and run_id:
                self.memory.save_memory("_run_id", run_id, participant_id, run_id)

        # An API client for internal use
        self._internal_api_client = api_client

        # Styling
        self._agent_colors = [
            "cyan",
            "magenta",
            "green",
            "yellow",
            "blue",
            "red",
            "white",
        ]
        self.color = self._agent_colors[hash(self.username) % len(self._agent_colors)]
        self._original_username: Optional[str] = None

    def log(self, message: str) -> None:
        if self.run_id is None:
            raise ValueError("Run ID is required to log messages")
        if self.participant_id is None:
            raise ValueError("Participant ID is required to log messages")

        """Log a message to the Kradle Run."""
        try:
            self._internal_api_client.logs.create(
                run_id=self.run_id,
                participant_id=self.participant_id,
                message=message,
            )
        except Exception as e:
            print(f"Error logging message: {e}")

    def init_participant(self, challenge_info: ChallengeInfo) -> InitParticipantResponse:
        """Called when agent is initialized. Override in subclass."""
        return InitParticipantResponse(listenTo=[])

    def on_event(self, observation: Observation) -> OnEventResponse:
        """Process the current state and return an action. Must be implemented by subclasses."""
        raise NotImplementedError("Agents must implement on_event() method")
