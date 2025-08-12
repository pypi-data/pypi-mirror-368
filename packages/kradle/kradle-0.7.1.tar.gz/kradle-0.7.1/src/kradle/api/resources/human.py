"""Challenge-specific API operations."""

from typing import Any, Optional
from ..http import HTTPClient


class HumanAPI:
    """Human management API endpoints."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def get(self, human_id: Optional[str] = None) -> dict[str, Any]:
        """Get human details. If called with no arguments, will return human that owns the Kradle API key."""
        if human_id is None:
            return self.http.get("human")
        return self.http.get(f"humans/{human_id}")
