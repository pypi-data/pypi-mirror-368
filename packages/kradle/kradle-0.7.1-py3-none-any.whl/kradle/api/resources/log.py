"""Run-specific API operations."""

import json
from typing import Any, Optional
from ..http import HTTPClient


class LogAPI:
    """Log management API endpoints."""

    def __init__(self, http: HTTPClient):
        self.http = http

    def create(self, run_id: str, participant_id: str, message: Any) -> dict[str, Any]:
        if not isinstance(message, str):
            message = json.dumps(message)
        return self.http.post(
            f"runs/{run_id}/logs",
            {"message": message, "participantId": participant_id},
        )

    def dump(self, run_id: str, page_size: int = 20) -> list[dict[str, Any]]:
        """
        Get all logs for a specific run, handling pagination automatically.

        Args:
            run_id: The ID of the run to get logs for
            page_size: Number of logs to return per page

        Returns:
            List of all log entries for the run
        """
        all_logs: list[dict[str, Any]] = []
        page_token: Optional[str] = None

        while True:
            params: dict[str, object] = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token

            response = self.http.get(f"runs/{run_id}/logs", params)

            if "logs" in response and response["logs"]:
                all_logs.extend(response["logs"])

            # Check if there are more pages
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        all_logs.reverse()  # reverse the order of the logs to start with the oldest log

        return all_logs
