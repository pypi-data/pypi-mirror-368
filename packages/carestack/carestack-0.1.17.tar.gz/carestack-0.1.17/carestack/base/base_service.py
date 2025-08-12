import json
import logging
from abc import ABC
from types import TracebackType
from typing import Any, Optional, Type, TypeVar
import httpx
from pydantic import BaseModel, RootModel
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError, ValidationError
from carestack.encounter.document_linking.dto.update_visit_records_dto import (
    UpdateVisitRecordsResponse,
)


class GetJsonFromTextResponse(BaseModel):
    """
    Pydantic model for responses that return a raw string instead of JSON.
    """

    response: str


logger = logging.getLogger(__name__)

ResT = TypeVar("ResT", bound=BaseModel)  # Response type


class BaseService(ABC):
    """
    Abstract base class for API service clients.

    Handles HTTP requests, authentication, error management, and resource cleanup.
    Subclasses should use this as a foundation for implementing specific API services.

    Args:
        config (ClientConfig): Configuration containing API URL and authentication details.
        timeout (Optional[int]): Timeout for requests in milliseconds (default: 6000000).
        headers (Optional[dict[str, str]]): Additional headers to include in the request.

    Raises:
        ValueError: If required configuration values are missing.
    """

    def __init__(
        self,
        config: "ClientConfig",
        timeout: Optional[int] = 6000000,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Initializes the BaseService with API configuration.

        Args:
            config (ClientConfig): Configuration containing API URL and authentication details.
            timeout (Optional[int]): Timeout for requests (default: 6000000 milliseconds).
            headers (Optional[dict[str, str]]): Additional headers to include in the request.

        Raises:
            ValueError: If required configuration values are missing.
        """
        self.config = config
        self.timeout = timeout

        # Use values directly from the ClientConfig object
        if not self.config.api_key:
            raise ValueError("API_KEY is missing in ClientConfig.")
        if not self.config.api_url:
            raise ValueError("API_URL is missing in ClientConfig.")
        if (
            not self.config.hprid_auth
        ):  # Assuming hprid_auth is a required part of ClientConfig
            raise ValueError("x_hpr_id (hprid_auth) is missing in ClientConfig.")

        # Default headers
        default_headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "x-hprid-auth": self.config.hprid_auth,
        }

        # Merge user-provided headers, allowing overrides
        self.headers = {**default_headers, **(headers or {})}
        self.client = httpx.AsyncClient(
            base_url=self.config.api_url,
            headers=self.headers,
            timeout=self.timeout,
        )

    @classmethod
    def from_config(
        cls,
        config: ClientConfig,
        timeout: Optional[int] = 10,
    ) -> "BaseService":
        """
        Factory method to create a BaseService instance from configuration.

        Args:
            config (ClientConfig): Configuration object.
            timeout (Optional[int]): Timeout for requests.

        Returns:
            BaseService: An instance of the service.
        """
        return cls(config, timeout)

    async def __handle_error(self, response: httpx.Response) -> None:
        """
        Handles API errors by raising EhrApiError with meaningful messages.

        Args:
            response (httpx.Response): The HTTP response object.

        Raises:
            EhrApiError: If the response status code indicates an error.
        """
        if response.status_code >= 400:
            try:
                if response.text:
                    try:
                        error_data = response.json()
                        error_message = error_data.get(
                            "message",
                            f"""Unknown error. Response: {
                                response.text}""",
                        )
                    except json.JSONDecodeError:
                        error_message = f"""Invalid JSON response: {
                            response.text}"""
                else:
                    error_message = f"""Empty response body with status code {
                        response.status_code}"""
                logger.exception(
                    "API Error: Status Code: %s, Message: %s",
                    response.status_code,
                    error_message,
                )
                raise EhrApiError(error_message, response.status_code)
            except json.JSONDecodeError as e:
                logger.exception(
                    "API Error: Status Code: %s, Raw Response: %s",
                    response.status_code,
                    response.text,
                )
                raise EhrApiError(
                    f"An unexpected error occurred: {e}", response.status_code
                ) from e

    async def __make_request(
        self,
        method: str,
        endpoint: str,
        response_model: Optional[Type[ResT]],
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> ResT:
        """
        Makes an API request with dynamic HTTP method.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE).
            endpoint (str): API endpoint.
            data (Optional[dict[str, Any]]): JSON payload for POST/PUT requests.
            params (Optional[dict[str, Any]]): Query parameters for GET requests.
            response_model (Optional[Type[ResT]]): Pydantic model to parse the response.

        Returns:
            ResT: Parsed response as a Pydantic model.

        Raises:
            EhrApiError: If the API request fails or response cannot be parsed.
            TypeError: If the response cannot be mapped to the expected model.
        """

        response_text: Optional[str] = None
        if data:
            # Be careful logging sensitive data in production
            logger.debug(f"Request data: {data}")
        try:
            logger.info(f"Making request: {method} {endpoint}")
            if data:
                logger.debug(f"Request data: {data}")  # Consider masking sensitive data

            response = await self.client.request(
                method, endpoint, json=data, params=params
            )

            # Read the response body as text FIRST
            response_text_bytes = await response.aread()
            response_text = response_text_bytes.decode("utf-8", errors="replace")

            logger.info(
                f"Received response status: {response.status_code} for {method} {endpoint}"
            )
            logger.debug(f"Raw response text: {response_text}")

            await self.__handle_error(response)
            response_data = response.json()

            if response_model is GetJsonFromTextResponse:
                logger.debug("Handling GetJsonFromTextResponse from raw string")
                # Directly instantiate with the raw string response
                try:
                    # Pydantic will validate if 'response_text' is a string
                    return GetJsonFromTextResponse(response=response_text)  # type: ignore
                except ValidationError as e:
                    logger.error(
                        f"Pydantic validation failed for GetJsonFromTextResponse: {e}. Raw text: {response_text}"
                    )
                    raise EhrApiError(
                        f"Validation failed for GetJsonFromTextResponse: {e}",
                        response.status_code,
                    ) from e

            # --- If not GetJsonFromTextResponse, THEN try parsing as JSON ---
            try:
                # Handle empty body explicitly after error check and GetJsonFromTextResponse check
                if not response_text.strip():
                    logger.warning(
                        f"Empty response body received for {method} {endpoint} (expected JSON)"
                    )
                    # Raising an error is usually appropriate if JSON was expected
                    raise ValueError(
                        "Received empty response body when expecting JSON data."
                    )

                response_data = json.loads(response_text)
                logger.debug(f"Parsed response data type: {type(response_data)}")

            except json.JSONDecodeError as json_err:
                # This error occurs if response_text is not valid JSON
                error_msg = f"Failed to decode JSON response for {method} {endpoint}. Status: {response.status_code}. Error: {json_err}. Response text: {response_text}"
                logger.error(error_msg)
                raise EhrApiError(
                    error_msg, response.status_code, response
                ) from json_err
            except ValueError as val_err:  # Catch the empty body error
                logger.error(
                    f"ValueError after parsing attempt: {val_err}. Raw text: {response_text}"
                )
                raise EhrApiError(
                    f"Data processing error: {val_err}", response.status_code
                ) from val_err

            if response_model is UpdateVisitRecordsResponse and isinstance(
                response_data, bool
            ):
                # Manually create the response object
                # Cast is safe here because we checked the type and model
                return UpdateVisitRecordsResponse(success=response_data)  # type: ignore

            # Handle RootModel
            elif response_model and issubclass(response_model, RootModel):
                # For RootModel, pass the data directly
                return response_model(response_data)

            elif response_model and isinstance(response_data, dict):
                # For standard BaseModel, unpack the dictionary
                return response_model(**response_data)
            else:

                # Handle unexpected case: Model is not RootModel, but data isn't a dict
                error_msg = (
                    f"Cannot instantiate {response_model.__name__ if response_model else 'unknown'}: "
                    f"Expected a dictionary response for this model, but received type {type(response_data)}"
                )
                logger.error(error_msg)
                raise TypeError(error_msg)

        except EhrApiError as e:
            raise e

    async def get(
        self,
        endpoint: str,
        response_model: Type[ResT],
        query_params: Optional[dict[str, Any]] = None,
    ) -> ResT:
        """
        Makes a GET request.

        Args:
            endpoint (str): API endpoint.
            response_model (Type[ResT]): Pydantic model to parse the response.
            query_params (Optional[dict[str, Any]]): Query parameters.

        Returns:
            ResT: Parsed response as a Pydantic model.
        """
        response_data = await self.__make_request(
            "GET", endpoint, response_model=response_model, params=query_params
        )
        return response_data

    async def post(
        self, endpoint: str, data: dict[str, Any], response_model: Type[ResT]
    ) -> ResT:
        """
        Makes a POST request.

        Args:
            endpoint (str): API endpoint.
            data (dict[str, Any]): JSON payload.
            response_model (Type[ResT]): Pydantic model to parse the response.

        Returns:
            ResT: Parsed response as a Pydantic model.
        """
        response_data: ResT = await self.__make_request(
            "POST", endpoint, response_model=response_model, data=data
        )
        return response_data

    async def put(
        self, endpoint: str, data: dict[str, Any], response_model: Type[ResT]
    ) -> ResT:
        """
        Makes a PUT request.

        Args:
            endpoint (str): API endpoint.
            data (dict[str, Any]): JSON payload.
            response_model (Type[ResT]): Pydantic model to parse the response.

        Returns:
            ResT: Parsed response as a Pydantic model.
        """
        return await self.__make_request(
            "PUT", endpoint, response_model=response_model, data=data
        )

    async def delete(
        self, endpoint: str, response_model: Optional[Type[ResT]] = None
    ) -> Optional[ResT]:
        """
        Makes a DELETE request.

        Args:
            endpoint (str): API endpoint.
            response_model (Optional[Type[ResT]]): Pydantic model to parse the response.

        Returns:
            Optional[ResT]: Parsed response as a Pydantic model, or None.
        """
        return await self.__make_request(
            "DELETE", endpoint, response_model=response_model
        )

    async def close(self) -> None:
        """
        Closes the HTTP client session.
        """
        await self.client.aclose()

    async def __aenter__(self) -> "BaseService":
        """
        Enables async context manager support.

        Returns:
            BaseService: The service instance.
        """
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Closes session on exit.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Traceback type.
        """
        await self.close()
