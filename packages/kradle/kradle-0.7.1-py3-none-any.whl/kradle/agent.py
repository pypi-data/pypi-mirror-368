from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, Union

from flask import Flask
from typing_extensions import TypeAlias

from kradle.agent_like import Participant
from kradle.agent_manager import AgentManager
from kradle.api.client import KradleAPI
from kradle.contexts import Context, context_manager, make_agent_key
from kradle.models import ChallengeInfo, InitParticipantResponse, MinecraftEvent, Observation, OnEventResponse

# Handle the circular import between kradle and agent. Break the cycle here but
# the kradle module imports this one normally.
if TYPE_CHECKING:
    from kradle.kradle import Kradle


T = TypeVar("T")


# Type for primitively-typed values that can be used in the config dictionary.
ConfigValue = Union[str, int, float, bool, None]


InitHandler: TypeAlias = Callable[[ChallengeInfo, Context], Any]
EventHandler: TypeAlias = Callable[[Observation, Context], OnEventResponse]


class Agent:
    """
    Represents an agent that can be registered with Kradle. Provides methods
    for registering event handlers.
    """

    def __init__(
        self,
        kradle: "Kradle",
        name: str,
        display_name: str,
        description: str,
        config: dict[str, ConfigValue],
    ) -> None:
        self.kradle = kradle

        # Kradle-specific configuration for the agent.
        self.name = name
        self.display_name = display_name
        self.description = description

        # User-specified configuration for the agent.
        self.config = config

        self._init_handler: Optional[InitHandler] = None
        self._event_handlers: dict[MinecraftEvent, EventHandler] = {}

    def init(
        self,
        fn: Optional[InitHandler] = None,
    ) -> Union[InitHandler, Callable[[InitHandler], InitHandler]]:
        """
        A decorator that registers a function to be called when a run is started.

        Args:
            fn: The function to call when a run is started
        """
        if fn is None:

            def decorator(f: InitHandler) -> InitHandler:
                self.init(f)
                return f

            return decorator

        self._init_handler = fn
        return fn

    def event(self, *event_types: MinecraftEvent) -> Callable[[EventHandler], EventHandler]:
        """
        A decorator that registers a function to be called when an event occurs.

        Args:
            event_type: The type of event to listen for.
        """

        def decorator(fn: EventHandler) -> EventHandler:
            for event_type in event_types:
                self._event_handlers[event_type] = fn
            return fn

        return decorator

    def serve(self) -> tuple[Flask, str]:
        """
        Serve this agent, connecting to the Kradle server and making the agent
        available to participate in challenges.

        Returns:
            The Flask app and the URL where the agent is being served
        """
        manager = AgentManager()
        manager._api_client = self.kradle._api_client

        return AgentManager.serve(
            self,
            create_public_url=self.kradle.create_public_url,
            public_url=self.kradle.public_url,
            host=self.kradle.host,
            port=self.kradle.port,
            debug=self.kradle.debug,
        )

    def clone(
        self,
        name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[dict[str, ConfigValue]] = None,
    ) -> "Agent":
        """
        Creates a new agent with updated configuration. All existing handlers
        will be copied to the new agent.

        Args:
            name: The name for the agent. Must be unique within your account and
                URL-friendly. This must be different from the name of the agent
                that you are cloning.
            display_name: The display name for the agent for use in the Kradle
                UI. If not provided, this will default to the name.
            description: A short description of the agent.
            config: A dictionary containing user-specified configuration that
                will be passed to the agent at runtime. Values are limited to
                primitive types but are not interpreted by Kradle.

        Returns:
            A new Agent instance with the updated configuration
        """
        if display_name is None:
            display_name = name
        if description is None:
            description = "Created by the Kradle Python SDK"
        if config is None:
            user_config = dict(self.config)
        else:
            user_config = config

        clone = Agent(self.kradle, name, display_name, description, user_config)

        # Copy handlers
        clone._init_handler = self._init_handler
        clone._event_handlers = dict(self._event_handlers)

        return clone

    @property
    def _implementation_name(self) -> str:
        return "kradle.agent.Agent"

    def _create_participant(self, api_client: KradleAPI, participant_id: str, run_id: str) -> Participant:
        return _EventDispatchingParticipant(self, participant_id, run_id)


class _EventDispatchingParticipant(Participant):
    def __init__(self, agent: Agent, participant_id: str, run_id: str) -> None:
        self.agent = agent
        self.participant_id = participant_id
        self.run_id = run_id

        # Explicit getters and setters are required for this value in order to
        # conform to the Participant protocol.
        self._original_username_value: Optional[str] = None

    @property
    def _original_username(self) -> Optional[str]:
        return self._original_username_value

    @_original_username.setter
    def _original_username(self, username: Optional[str]) -> None:
        self._original_username_value = username

    def init_participant(self, challenge_info: ChallengeInfo) -> InitParticipantResponse:
        # Populate the context.
        agent_key = make_agent_key(challenge_info.participant_id, challenge_info.run_id)
        context = context_manager.get_or_create(agent_key)
        context._challenge_info = challenge_info
        context._original_username = self._original_username
        context.api_client = self.agent.kradle._api_client
        context.update(self.agent.config)

        # Call the user's init handler.
        if self.agent._init_handler is not None:
            self.agent._init_handler(challenge_info, context)

        # Return the event names that the agent wants to listen to based on the
        # event handlers that the user has registered.
        event_names = list(self.agent._event_handlers.keys())
        return InitParticipantResponse({"listenTo": event_names})

    def on_event(self, observation: Observation) -> OnEventResponse:
        # TODO(wilhuff): The Observation.event field is a string, not an
        # enum.
        event_key = MinecraftEvent(observation.event)
        event_handler = self.agent._event_handlers.get(event_key)

        agent_key = make_agent_key(observation.participant_id, observation.run_id)
        context = context_manager.get_or_create(agent_key)

        if event_handler is None:
            return {
                "code": "",
                "message": f"Ignored un-subscribed event {observation.event}",
            }

        return event_handler(observation, context)
