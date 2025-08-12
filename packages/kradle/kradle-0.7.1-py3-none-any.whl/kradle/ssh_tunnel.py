"""
SSH Tunnel module for Kradle Minecraft agents.
Provides clean tunnel management with Pinggy.io integration.
"""

import subprocess
import threading
import re
import logging
from typing import IO, Optional, Callable
from dataclasses import dataclass


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class TunnelConfig:
    """Configuration for SSH tunnel connection."""

    local_port: int
    remote_host: str = "a.pinggy.io"
    remote_port: int = 443
    timeout: int = 15


class SSHTunnel:
    """Manages SSH tunnel connection to Pinggy.io."""

    def __init__(self, config: TunnelConfig):
        self.config = config
        self._process: Optional[subprocess.Popen[str]] = None
        self._url: Optional[str] = None
        self._status_callback: Optional[Callable[[str], None]] = None
        self._lock = threading.Lock()
        self._url_event = threading.Event()

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback function for tunnel status updates."""
        self._status_callback = callback

    def start(self) -> Optional[str]:
        """Start the SSH tunnel and wait for URL."""
        with self._lock:
            try:
                if self._process is not None:
                    return self._url

                command = [
                    "ssh",
                    "-p",
                    str(self.config.remote_port),
                    # Important to use 127.0.0.1 instead of localhost
                    "-R",
                    f"0:127.0.0.1:{self.config.local_port}",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-T",
                    f"a@{self.config.remote_host}",
                ]

                self._process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                )

                self._start_output_monitors()

                # Wait for URL or timeout
                if not self._url_event.wait(timeout=self.config.timeout):
                    raise TimeoutError("Timeout waiting for tunnel URL")

                return self._url

            except Exception as e:
                logger.error(f"Failed to start tunnel: {e}")
                self.stop()
                return None

    def _start_output_monitors(self) -> None:
        """Start monitoring process output streams."""

        def read_stream(stream: IO[str]) -> None:
            """Monitor stream for tunnel URL."""
            url_pattern = re.compile(r"https?://[^/\s]+\.free\.pinggy\.link")
            try:
                for line in iter(stream.readline, ""):
                    match = url_pattern.search(line)
                    if match:
                        url = match.group(0)
                        if url.startswith("https"):  # Only use HTTPS URL
                            self._url = url
                            if self._status_callback:
                                self._status_callback(url)
                            self._url_event.set()  # Signal URL is available
                            break  # We got our URL, no need to keep reading
            except Exception as e:
                logger.error(f"Error reading stream: {e}")

        # Monitor stdout for URL
        assert self._process is not None
        threading.Thread(target=read_stream, args=(self._process.stdout,), daemon=True).start()

        # Monitor stderr just for logging
        def log_stderr(stream: IO[str]) -> None:
            try:
                for line in iter(stream.readline, ""):
                    logger.debug(f"Tunnel stderr: {line.strip()}")
            except Exception as e:
                logger.error(f"Error reading stderr: {e}")

        threading.Thread(target=log_stderr, args=(self._process.stderr,), daemon=True).start()

    def stop(self) -> None:
        """Stop the tunnel and clean up resources."""
        with self._lock:
            if self._process:
                try:
                    self._process.terminate()
                    self._process.wait(timeout=5)
                except Exception as e:
                    logger.error(f"Error stopping tunnel: {e}")
                finally:
                    self._process = None
                    self._url = None
                    self._url_event.clear()


def create_tunnel(port: int) -> tuple[Optional[SSHTunnel], Optional[str]]:
    """
    Create and start a tunnel.

    Args:
        port: Local port to tunnel

    Returns:
        tuple[Optional[SSHTunnel], Optional[str]]: (tunnel instance, public url)
    """
    config = TunnelConfig(local_port=port)
    tunnel = SSHTunnel(config)
    url = tunnel.start()
    if url:
        return tunnel, url
    return None, None
