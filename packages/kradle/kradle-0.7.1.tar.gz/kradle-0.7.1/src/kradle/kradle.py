import os
from typing import Optional, TypeVar

from flask import Flask

from kradle.agent import Agent, ConfigValue
from kradle.api.client import KradleAPI

# URL of the Kradle web application UI where users can get API keys. This is
# different from the API endpoint URL used by KradleAPI.
KRADLE_URL = "https://app.kradle.ai"

T = TypeVar("T")


class Kradle:
    """
    Main entry point for the Kradle SDK. This class provides the interface
    for creating and serving agents.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        create_public_url: bool = False,
        public_url: Optional[str] = None,
        host: str = "localhost",
        port: Optional[int] = None,
        debug: bool = False,
    ) -> None:
        """
        Initialize a new Kradle instance.

        Args:
            api_key: The API key for authenticating with the Kradle API. If not
                provided, will attempt to read from the KRADLE_API_KEY
                environment variable.
            create_public_url: Whether to create a public URL for the agent
                server using an SSH tunnel.
            public_url: A custom public URL to use for the agent server. Cannot
                be specified if create_public_url is True.
            host: The hostname to use for the agent server.
            port: The port to use for the agent server. If not provided, a free
                port will be found.
            debug: Whether to run the server in debug mode.
        """
        self.create_public_url = create_public_url
        self.public_url = public_url
        self.host = host
        self.port = port
        self.debug = debug

        self._app_url = os.getenv("KRADLE_URL") or KRADLE_URL
        self._api_client = KradleAPI(api_key)
        self._validate_api_key()

        # Flask app and server URL (set once server is created)
        self._app: Optional[Flask] = None
        self.url: Optional[str] = None

    def _validate_api_key(self) -> None:
        """Validate the API key and print a helpful error message if it's not set."""
        try:
            self._api_client.validate_api_key()
        except Exception as e:
            raise ValueError(
                f"\n> API key required\n\n"
                f"Setup:\n"
                f"  1. Get your key: {self._app_url}\n"
                f"  2. EITHER set the KRADLE_API_KEY environment variable as your key\n"
                f"     OR pass api_key='your-key' when creating the Kradle instance\n"
            ) from e

    @property
    def api(self) -> KradleAPI:
        return self._api_client

    def agent(
        self,
        name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[dict[str, ConfigValue]] = None,
    ) -> Agent:
        """
        Creates a new agent.

        Args:
            name: The name for the agent. Must be unique within your account and
                URL-friendly.
            display_name: The display name for the agent for use in the Kradle
                UI. If not provided, this will default to the name.
            description: A short description of the agent.
            config: A dictionary containing additional user-specified
                configuration that will be passed to the agent at runtime. Use
                this to parameterize the agent's behavior to test variations of
                your agent code or strategy. Values are limited to primitive
                types but are not interpreted by Kradle.

        Returns:
            A new Agent instance
        """
        if display_name is None:
            display_name = name
        if description is None:
            description = "Created by the Kradle Python SDK"
        if config is None:
            config = {}
        return Agent(self, name, display_name, description, config)

    def serve(self, *agents: Agent) -> tuple[Flask, dict[str, str]]:
        """
        Serves the specified agents.

        Args:
            *agents: The agents to serve

        Returns:
            The Flask app and a dictionary mapping agent names to their URLs
        """
        if len(agents) == 0:
            raise ValueError("At least one agent must be provided")

        urls: dict[str, str] = {}

        for agent in agents:
            app, url = agent.serve()
            urls[agent.name] = url

        return app, urls
