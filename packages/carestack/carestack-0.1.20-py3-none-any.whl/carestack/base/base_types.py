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
        api_url (str): The base URL of the API endpoint.
        hprid_auth (str): The HPR ID or additional authentication header value.
    """

    def __init__(
        self,
        api_key: str,
        x_hpr_id: Optional[str] = None,
        api_url: Optional[str] = None,
    ) -> None:
        self.api_key = api_key
        self.hprid_auth = x_hpr_id or os.getenv("X_HPR_ID")
        self.api_url = api_url or os.getenv("API_URL")


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
