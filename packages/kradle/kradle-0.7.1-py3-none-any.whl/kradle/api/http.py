"""HTTP request methods for the Kradle API client."""

from typing import Callable, Optional, Any, Union
import requests
from typing import cast
from urllib.parse import urljoin


class KradleAPIError(Exception):
    """Raised when the Kradle API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class HTTPClient:
    """HTTP client methods."""

    def __init__(self, base_url: str, get_headers: Callable[[], dict[str, str]]):
        self.base_url = base_url
        self._get_headers = get_headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the API."""
        url = urljoin(self.base_url, endpoint.lstrip("/"))

        # print(f"Making request to {url} with method {method}")
        # print(f"Headers: {self._get_headers()}")
        # print(f"Params: {params}")
        # print(f"Data: {data}")
        # print(f"JSON: {json}")

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                params=params,
                data=data,
                json=json,
                timeout=30,
            )

            # Raise error for bad responses
            response.raise_for_status()

            return cast(dict[str, Any], response.json())

        except requests.HTTPError as e:
            # Try to get error details from response
            error_msg = "API request failed"
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict):
                    error_msg = str(error_data.get("message", error_data.get("error", error_msg)))
            except:  # noqa: E722
                error_msg = str(e)

            raise KradleAPIError(
                message=error_msg,
                status_code=e.response.status_code,
                response=error_data if "error_data" in locals() else None,
            ) from e

        except requests.RequestException as e:
            raise KradleAPIError(f"Request failed: {str(e)}") from e

    def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Make GET request to API endpoint."""
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Union[dict[str, Any], Any]] = None) -> dict[str, Any]:
        """Make POST request to API endpoint."""
        return self._make_request("POST", endpoint, json=data)

    def put(self, endpoint: str, data: Optional[Union[dict[str, Any], Any]] = None) -> dict[str, Any]:
        """Make PUT request to API endpoint."""
        return self._make_request("PUT", endpoint, json=data)

    def delete(self, endpoint: str) -> dict[str, Any]:
        """Make DELETE request to API endpoint."""
        return self._make_request("DELETE", endpoint)
