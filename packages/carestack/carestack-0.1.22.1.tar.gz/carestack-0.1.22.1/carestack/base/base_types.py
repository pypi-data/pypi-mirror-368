import os
from typing import Any, Optional

from carestack.default_config import DEFAULT_API_URL, DEFAULT_X_HPR_ID
from dotenv import load_dotenv

load_dotenv()


class ClientConfig:
    """
    Configuration object for initializing API clients.

    Attributes:
        api_key (str): The API key used for authenticating requests.
        hprid_auth Optional(str): The HPR ID or additional authentication header value.
        api_url Optional(str): The base URL of the API endpoint.

    """

    def __init__(
        self,
        api_key: str,
        x_hpr_id: Optional[str] = None,
        api_url: Optional[str] = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required and cannot be empty")

        self.api_key = api_key
        self.hprid_auth = x_hpr_id or os.getenv("X_HPR_ID", DEFAULT_X_HPR_ID)
        self.api_url = api_url or os.getenv("API_URL", DEFAULT_API_URL)

        # Detect if placeholders were not replaced during build
        if self.api_url.startswith("__") and self.api_url.endswith("__"):
            raise ValueError(
                f"API_URL is not configured correctly. Found placeholder value: {self.api_url}"
            )


class ApiResponse:
    """
    Standardized structure for API responses.

    Attributes:
        data (Any): The response payload or data returned from the API.
        status (int): The HTTP status code or custom status indicator.
        message (str): Informational or error message related to the response.
    """

    def __init__(self, data: Any, status: int, message: str) -> None:
        self.data = data
        self.status = status
        self.message = message
