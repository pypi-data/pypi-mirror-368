"""Challenge-specific API operations."""

from typing import Any
from ..http import HTTPClient


class ChallengeAPI:
    """Challenge management API endpoints."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def get(self, challenge_slug: str) -> dict[str, Any]:
        """Get challenge details by slug."""
        return self.http.get(f"challenges/{challenge_slug}")
