import logging
import sys
from typing import Optional, Any
from rich.console import Console
from rich.logging import RichHandler


class KradleLogger:
    def __init__(self) -> None:
        self.console = Console()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging with Rich handler for beautiful formatting"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(rich_tracebacks=True, markup=True, show_time=False)],
        )
        # Keep Flask debug logs clean
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.handlers = []
        werkzeug_handler = logging.StreamHandler(sys.stdout)
        werkzeug_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", "%H:%M:%S"))
        werkzeug_logger.addHandler(werkzeug_handler)
        werkzeug_logger.setLevel(logging.INFO)

    def display_agent_registered_banner(self, config: dict[str, Any]) -> None:
        """Display a beautiful new agent banner with server information"""
        self.console.print("\n")
        self.log_success(
            f"✨ {config.get('agent_username')} registered with Kradle, run at: "
            f"[link={config.get('agent_edit_url')}]{config.get('agent_edit_url')}[/link]\n"
        )

    def log_success(self, message: str) -> None:
        """Log a success message"""
        self.console.print(f"✓ {message}", style="green")

    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """Log an error message with optional exception details"""
        self.console.print(f"✕ {message}", style="red")
        if error:
            self.console.print(f"  → {type(error).__name__}: {str(error)}", style="red dim")

    def log_warning(self, message: str) -> None:
        """Log a warning message"""
        self.console.print(f"! {message}", style="yellow")

    def log_info(self, message: str) -> None:
        """Log an informational message"""
        self.console.print(f"○ {message}", style="blue")

    def log_debug(self, message: str) -> None:
        """Log a debug message"""
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            self.console.print(f"· {message}", style="dim")

    def log_api_call(self, method: str, endpoint: str, status: int) -> None:
        """Log an API call with color-coded status"""
        status_color = "green" if 200 <= status < 300 else "red"
        method_width = 6  # Consistent width for method
        self.console.print(
            f"  {method:<{method_width}} {endpoint} [{status_color}]{status}[/]",
            style="dim",
        )

    def on_shutdown(self) -> None:
        """Display shutdown message"""
        self.console.print("\n[yellow]Shutting down Kradle Agent Server...[/yellow]")
