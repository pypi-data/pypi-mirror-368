# kradle/models.py
from dataclasses import dataclass, field
from typing import Any, Optional, TypedDict, Union
from enum import Enum
from datetime import datetime
from pprint import pformat
from dataclasses import asdict
import json

# NotRequired becomes built-in with Python 3.11.
from typing_extensions import NotRequired


class MinecraftEvent(str, Enum):
    """
    Enumeration of all possible Minecraft bot event types captured from Mineflayer.

    This enum represents the various events that can occur during bot operation:
    - Idle state
    - Command execution
    - Chat and message interactions
    - Health-related events
    - Regular interval updates

    The event types correspond directly to Mineflayer bot events and are used to:
    1. Classify incoming events from the bot
    2. Trigger appropriate event handlers
    3. Update the observation state

    Event Sources:
        - bot.on('chat') -> CHAT
        - bot.on('message') -> MESSAGE
        - bot.on('health') -> HEALTH
        - bot.on('death') -> DEATH
        - Internal timer -> INTERVAL
        - Command system -> COMMAND_EXECUTED
        - Damage events -> DAMAGE
        - No active events for a while -> IDLE

    Technical Details:
        - Inherits from str for JSON serialization
        - Used as a key field in Observation class
        - Maps directly to Mineflayer event system
        - Case-sensitive string values
    """

    INITIAL_STATE = ("initial_state",)
    IDLE = "idle"
    COMMAND_EXECUTED = "command_executed"
    CHAT = "chat"
    MESSAGE = "message"
    HEALTH = "health"
    DEATH = "death"
    DAMAGE = "damage"
    INTERVAL = "interval"
    SPAWN = "spawn"
    RESPAWN = "respawn"
    GAMEOVER = "game_over"


class TimeOfDay(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


class Weather(str, Enum):
    CLEAR = "clear"
    RAIN = "rain"
    THUNDER = "thunder"


class GameMode(str, Enum):
    SURVIVAL = "survival"
    CREATIVE = "creative"
    ADVENTURE = "adventure"
    SPECTATOR = "spectator"


@dataclass
class ChatMessage:
    sender: str
    chat_msg: str


@dataclass
class ChallengeInfo:
    participant_id: str
    run_id: str
    task: str
    agent_modes: dict[str, Union[str, bool]]
    js_functions: dict[str, dict[str, str]]
    available_events: list[str]


@dataclass
class Observation:
    """
    Comprehensive representation of a Minecraft bot's state at a single point in time.
    Captures the complete state from the Mineflayer bot including location, surroundings,
    inventory, and events.

    Identity Attributes:
        name (str): Bot's username in the game
            Example: "Bot123"
        participant_id (str): Unique identifier for this bot instance
            Example: "uuid-1234-5678"
        run_id (str): Unique identifier for this Run
            Example: "1234-5678"
        observation_id (str): Unique identifier for this specific observation
            Example: "obs-1234-5678"
        past_observation_id (Optional[str]): Reference to previous observation
            Example: "obs-1234-5677"

    Event Information:
        event (str): Current event type from EventType enum
            Example: "chat", "death", "idle"
        idle (bool): Whether bot is currently idle
            Example: True if no active tasks
        executing (Optional[str]): Command currently being executed
            Example: "move forward", None if no command
        output (Optional[str]): Output from last executed command
            Example: "Successfully moved to coordinates"

    Location Data:
        position: Dict[str, float]
            Example: {"x": 123.45, "y": 64.0, "z": -789.01, "pitch": 45.0, "yaw": 90.0}

    Player State:
        health (float): Health points normalized to 0-1 range
            Example: 0.85 (17/20 hearts)
        hunger (float): Hunger points normalized to 0-1 range
            Example: 0.9 (18/20 food points)
        xp (float): Experience level
            Example: 30.0
        gamemode (GameMode): Current game mode enum
            Example: GameMode.SURVIVAL
        is_alive (bool): Whether bot is currently alive
            Example: True
        on_ground (bool): Whether bot is on solid ground
            Example: True
        equipped (str): Currently equipped item name
            Example: "diamond_sword"

    Environment State:
        biome (str): Current biome name
            Example: "plains", "desert", "forest"
        weather (Weather): Current weather enum
            Example: Weather.RAIN
        time (int): Minecraft time in ticks (0-24000)
            Example: 13000
        time_of_day (TimeOfDay): Time category enum
            Example: TimeOfDay.MORNING
        day_count (int): Number of in-game days passed
            Example: 42
        rain_state (float): Rain intensity from 0-1
            Example: 0.7
        thunder_state (float): Thunder intensity from 0-1
            Example: 0.0
        light_level (int): Block light level (0-15)
            Example: 14
        dimension (str): Current dimension name
            Example: "overworld", "nether", "end"

    World State:
        players (List[str]): Names of nearby players
            Example: ["Steve", "Alex"]
        blocks (List[str]): Visible block types in bot's range
            Example: ["stone", "dirt", "oak_log", "diamond_ore"]
        entities (List[str]): Nearby entity types
            Example: ["zombie", "sheep", "creeper"]
        craftable (List[str]): Items that can be crafted with current inventory
            Example: ["wooden_pickaxe", "torch", "crafting_table"]
        inventory (Dict[str, int]): Current inventory items and their counts
            Example: {"cobblestone": 64, "iron_ingot": 5}
        chat_messages (List[ChatMessage]): Recent chat messages
            Example: [ChatMessage(role="player", content="Hello")]

    Data Sources:
        - Location: bot.entity.position
        - Health/Hunger: bot.health, bot.food
        - Inventory: bot.inventory.items()
        - Blocks: bot.findBlocks() with range of 64 blocks
        - Entities: bot.nearbyEntities with range of 64 blocks
        - Weather: bot.world.weatherData
        - Time: bot.time.timeOfDay
        - Messages: bot.chat events

    Methods:
        from_event(data: Dict) -> Observation:
            Creates new Observation from raw event data
        get_summary() -> str:
            Returns formatted summary of current state
        to_json() -> str:
            Returns JSON serialized state
        __str__() -> str:
            Returns formatted string representation
    """

    # Identity fields
    name: str = ""
    participant_id: str = ""
    run_id: str = ""
    observation_id: str = ""
    past_observation_id: Optional[str] = None

    # Event info
    event: str = "idle"
    idle: bool = True
    executing: Optional[str] = None
    output: Optional[str] = None

    # Location
    position: dict[str, float] = field(default_factory=dict)

    # Player state
    health: float = 1.0  # Normalized to 0-1 range
    hunger: float = 1.0  # Normalized to 0-1 range
    xp: float = 0.0
    gamemode: GameMode = GameMode.SURVIVAL
    is_alive: bool = True
    on_ground: bool = True
    equipped: str = ""

    # Environment
    biome: str = "plains"
    weather: Weather = Weather.CLEAR
    time: int = 0  # 0-24000
    time_of_day: TimeOfDay = TimeOfDay.MORNING
    day_count: int = 0
    rain_state: float = 0.0
    thunder_state: float = 0.0
    light_level: int = 15
    dimension: str = "overworld"
    screenshot: Optional[str] = None

    # World state
    players: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    craftable: list[str] = field(default_factory=list)
    inventory: dict[str, int] = field(default_factory=dict)
    chat_messages: list[ChatMessage] = field(default_factory=list)

    @classmethod
    def from_event(cls, data: dict[str, Any]) -> "Observation":
        """Create state from event data with validation"""
        try:
            # Validate time range
            time = int(data.get("time", 0))
            if not 0 <= time <= 24000:
                time = time % 24000

            # Validate health/hunger are between 0-1
            health = float(data.get("health", 20))
            hunger = float(data.get("hunger", 20))
            health = max(0.0, min(1.0, health))
            hunger = max(0.0, min(1.0, hunger))

            return cls(
                # Identity
                name=str(data.get("name", "")),
                participant_id=str(data.get("participantId", "")),
                run_id=str(data.get("runId", "")),
                observation_id=str(data.get("observationId", "")),
                past_observation_id=data.get("past_observationid"),
                # Event
                event=str(data.get("event", "idle")),
                idle=bool(data.get("idle", True)),
                executing=data.get("executing"),
                output=data.get("output"),
                # Location
                position=data.get("position", {}),
                # Player State
                health=health,
                hunger=hunger,
                xp=float(data.get("xp", 0)),
                gamemode=GameMode(str(data.get("gamemode", "survival"))),
                is_alive=bool(data.get("is_alive", True)),
                on_ground=bool(data.get("on_ground", True)),
                equipped=str(data.get("equipped", "")),
                # Environment
                biome=str(data.get("biome", "plains")),
                weather=Weather(str(data.get("weather", "clear"))),
                time=time,
                time_of_day=TimeOfDay(str(data.get("timeOfDay", "morning"))),
                day_count=int(data.get("day_count", 0)),
                rain_state=float(data.get("rain_state", 0)),
                thunder_state=float(data.get("thunder_state", 0)),
                light_level=int(data.get("light_level", 15)),
                dimension=str(data.get("dimension", "overworld")),
                screenshot=data.get("screenshot", None),
                # World State
                players=list(data.get("players", [])),
                blocks=list(data.get("blocks", [])),
                entities=list(data.get("entities", [])),
                craftable=list(data.get("craftable", [])),
                inventory=dict(data.get("inventory", {})),
                chat_messages=[
                    ChatMessage(
                        sender=str(msg.get("sender", "unknown")),
                        chat_msg=("to me: " if msg.get("dm", False) else " to general chat: ")
                        + str(msg.get("message", "")),
                    )
                    for msg in data.get("chat_messages", [])
                ],
            )
        except Exception as e:
            raise ValueError(f"Failed to parse state data: {str(e)}") from e

    def get_summary(self) -> str:
        """Returns a formatted summary of the observation state"""
        chat_msg_history = (
            "\n    - No messages"
            if not self.chat_messages
            else "".join(f"\n    - {msg.sender}: {msg.chat_msg}" for msg in self.chat_messages)
        )

        x = self.position.get("x", "None")
        y = self.position.get("y", "None")
        z = self.position.get("z", "None")

        return f"""Player Status:
            - Health: {self.health * 100}%
            - Hunger: {self.hunger * 100}%
            - XP Level: {self.xp}
            - Gamemode: {self.gamemode}
            - Is Alive: {self.is_alive}
            - Equipment: {self.equipped}

            Location & Environment:
            - Position: x={x}, y={y}, z={z}
            - Dimension: {self.dimension}
            - Biome: {self.biome}
            - Time: {self.time_of_day}
            - Weather: {self.weather}
            - Light Level: {self.light_level}

            World State:
            - Nearby Blocks: {", ".join(self.blocks) if self.blocks else "None"}
            - Nearby Entities: {", ".join(self.entities) if self.entities else "None"}
            - Craftable Items: {", ".join(self.craftable) if self.craftable else "None"}
            - Inventory: {json.dumps(self.inventory) if self.inventory else "Empty"}

            Chat Messages:{chat_msg_history}

            Output from previous command: {self.output if self.output else "None"}"""

    def __str__(self) -> str:
        """Clean, formatted string representation of all fields"""
        return pformat(asdict(self), indent=2, width=80, sort_dicts=False)

    def to_json(self) -> str:
        """Returns a JSON string representation of the observation."""
        return json.dumps(asdict(self), indent=4, default=str)


class InitParticipantResponse(TypedDict):
    """The response from the server when an agent is initialized."""

    listenTo: list[MinecraftEvent]
    # we may add more fields in the future


class OnEventResponse(TypedDict):
    """The response from the server when an event is received."""

    code: str
    message: str
    thoughts: NotRequired[str]
    delay: NotRequired[float]
    # we may add more fields in the future


# TODO this should be generated from the ActionType schema
JSON_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "action",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The code to execute"},
                "message": {
                    "type": "string",
                    "description": "The chat message that will be visible to all participants",
                },
                "thoughts": {"type": "string", "description": "The agent's thoughts that will remain private"},
            },
            "required": ["code", "message", "thoughts"],
            "additionalProperties": False,
        },
    },
}


class DomainEnum(str, Enum):
    MINECRAFT = "minecraft"


@dataclass
class RunArena:
    """The arena in which the run is taking place."""

    arena_id: str  # Unique identifier for the arena
    domain: DomainEnum  # Domain of the arena
    public_address: Optional[str]  # Public address of the arena


class RunFinishedStatusEnum(str, Enum):
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    DISCONNECT = "disconnect"
    GAME_OVER = "game_over"


@dataclass
class RunParameters:
    creator_username: Optional[str]  # Username of the creator


@dataclass
class RunAggregatedResults:
    participant_count: int
    successful_participant_count: int
    successful_participant_ids: list[str]
    unsuccessful_participant_count: int
    unsuccessful_participant_ids: list[str]
    total_time: float


@dataclass
class RunParticipantResult:
    agent: str
    winner: bool
    score: Optional[float]
    time_to_success: Optional[float]


@dataclass
class Run:
    """A run is a single execution of an agent in a challenge."""

    id: str  # Unique identifier for the run
    arena: Optional[RunArena]  # Contains arenaId, domain, and publicAddress
    challenge: str  # Challenge identifier
    creation_time: datetime  # ISO timestamp when run was created
    update_time: Optional[datetime]  # ISO timestamp when run was last updated
    creator: Optional[str]  # User who created the run
    status: str  # Current status of the run (e.g., 'finished')
    start_time: Optional[datetime]  # ISO timestamp when run started
    end_time: Optional[datetime]  # ISO timestamp when run ended
    total_time: Optional[float]  # Total run time in milliseconds
    finished_status: Optional[RunFinishedStatusEnum]  # Final status when run is complete (e.g., 'game_over')
    job_id: Optional[str]  # Associated job identifier
    runParameters: Optional[RunParameters]  # Custom parameters for this run
    aggregated_results: Optional[RunAggregatedResults]
    participant_results: Optional[dict[str, RunParticipantResult]]

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "Run":
        """
        Create a Run instance from an API response dictionary.

        Args:
            data: Dictionary containing run data from the API

        Returns:
            Run: A properly structured Run object
        """
        arena = _parse_arena(data.get("arena"))

        # Parse datetime strings to datetime objects
        creation_time = _parse_datetime(data.get("creationTime"))
        update_time = _parse_datetime(data.get("updateTime"))
        start_time = _parse_datetime(data.get("startTime"))
        end_time = _parse_datetime(data.get("endTime"))

        if creation_time is None:
            raise ValueError("Incomplete API response: creationTime is required")

        # Convert aggregated results
        agg_results = data.get("aggregatedResults")
        aggregated_results = (
            RunAggregatedResults(
                participant_count=agg_results.get("participantCount", 0),
                successful_participant_count=agg_results.get("successfulParticipantCount", 0),
                successful_participant_ids=agg_results.get("successfulParticipantIds", []),
                unsuccessful_participant_count=agg_results.get("unsuccessfulParticipantCount", 0),
                unsuccessful_participant_ids=agg_results.get("unsuccessfulParticipantIds", []),
                total_time=agg_results.get("totalTime", 0.0),
            )
            if agg_results
            else None
        )

        # Convert participant results
        participant_results = {}
        if data.get("participantResults"):
            for participant_id, result in data.get("participantResults", {}).items():
                participant_results[participant_id] = RunParticipantResult(
                    agent=result.get("agent", ""),
                    winner=result.get("winner", False),
                    score=result.get("score"),
                    time_to_success=result.get("timeToSuccess"),
                )

        # Create and return the Run object
        return cls(
            id=data.get("id", ""),
            arena=arena,
            challenge=data.get("challenge", ""),
            creation_time=creation_time,
            update_time=update_time,
            creator=data.get("creator"),
            status=data.get("status", ""),
            start_time=start_time,
            end_time=end_time,
            total_time=data.get("totalTime"),
            finished_status=RunFinishedStatusEnum(data.get("finishedStatus")) if data.get("finishedStatus") else None,
            job_id=data.get("jobId"),
            runParameters=RunParameters(data.get("runParameters", {})),
            aggregated_results=aggregated_results,
            participant_results=participant_results,
        )


def _parse_arena(data: Optional[dict[str, Any]]) -> Optional[RunArena]:
    if data is None:
        return None
    arena_id = data.get("arenaId")
    domain = data.get("domain")
    public_address = data.get("publicAddress")
    if arena_id is None or domain is None:
        return None
    return RunArena(arena_id=arena_id, domain=DomainEnum(domain), public_address=public_address)


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class ChallengeParticipant(TypedDict):
    """A participant in a challenge."""

    agent: str
    role: NotRequired[str]


@dataclass
class RunRequest:
    """A request to create a run."""

    challenge_slug: str  # challenge slug
    participants: list[ChallengeParticipant]  # list of participant tuples


@dataclass
class ExperimentParticipantResult:
    agent: str
    num_runs_finished: int
    win_count: int
    total_score: float
    average_score: float
    times_to_success: list[float]
    average_time_to_success: Optional[float]


@dataclass
class ExperimentResult:
    num_runs: int
    num_runs_finished: int
    results: dict[str, ExperimentParticipantResult]  # keyed by participant id
    runs: dict[str, Run]  # keyed by run id
    logs: dict[str, list[dict[str, Any]]]  # keyed by run id
    duration: float  # time duration of the experiment

    def display_results(self) -> None:
        print(f"----- Experiment Results -----")
        print(f"  Number of runs: {self.num_runs}")
        print(f"  Number of runs finished: {self.num_runs_finished}")
        print(f"  Total experiment duration: {self.duration:.2f} seconds")
        print(f"  Overall Evaluation:")
        for participant_id, result in self.results.items():
            print(f"\n  Participant: {participant_id}")
            print(f"    Agent: {result.agent}")
            print(f"    Win Count: {result.win_count} ({(result.win_count / result.num_runs_finished) * 100}%)")
            print(f"    Total Score: {result.total_score}")
            print(f"    Average Score: {result.average_score}")
            if result.win_count > 0:
                print(
                    f"    Average Time to Success: "
                    f"{f'{result.average_time_to_success:.2f} seconds' if result.win_count > 0 else 'N/A'}"
                )

    def display_runs(self, show_logs: bool = False) -> None:
        print("\n----- Run Details -----")
        for run in self.runs.values():
            print(f"\n[[[ Run ID: {run.id} ]]]")
            print(f"  Status: {run.status}")
            print(f"  Finished Status: {run.finished_status}")
            print(
                f"  Total time: "
                f"{'N/A' if not isinstance(run.total_time, (int, float)) else f'{run.total_time / 1000:.2f} seconds'}"
            )
            # print(f"  Start Time: {run.start_time}")
            # print(f"  End Time: {run.end_time}")

            print("\n  Participant Results:")
            if run.participant_results:
                for participant_id, result in run.participant_results.items():
                    print(f"    {participant_id}:")
                    print(f"      Agent: {result.agent}")
                    print(f"      Winner: {result.winner}")
                    print(f"      Score: {result.score}")
                    print(f"      Time to Success: {result.time_to_success if result.time_to_success else 'N/A'}")

            if show_logs and run.id in self.logs:
                print("\n  Logs:")
                for log in self.logs[run.id]:
                    print(f"Creation time: {log['creationTime']}")
                    print(f"Participant: {log['participantId']}")
                    print(f"Level: {log['level']}")
                    print(f"Message: {log['message']}")

    def dump_as_json(self) -> str:
        return json.dumps(asdict(self), indent=4, default=str)
