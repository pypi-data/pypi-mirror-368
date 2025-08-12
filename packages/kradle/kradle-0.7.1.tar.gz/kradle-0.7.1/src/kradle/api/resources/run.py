"""Run-specific API operations."""

from typing import Any
from ..http import HTTPClient
from kradle.models import ChallengeParticipant


class RunAPI:
    """Run management API endpoints."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def create(self, challenge_slug: str, participants: list[ChallengeParticipant]) -> dict[str, Any]:
        """Create a new run."""

        return self.http.post(
            "jobs",
            {
                "challenge": challenge_slug,
                "participants": participants,
            },
        )

    def get(self, run_id: str) -> dict[str, Any]:
        """Get run details by ID."""
        return self.http.get(f"runs/{run_id}")

    def send_action(self, run_id: str, action: dict[str, Any], participant_id: str) -> dict[str, Any]:
        """Send an action to a specific run."""
        return self.http.post(
            f"runs/{run_id}/actions",
            {
                "action": action,
                "participantId": participant_id,
            },
        )
