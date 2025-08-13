import json
import logging
from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import PractitionerEndPoints
from carestack.practitioner.practitioner_dto import (
    CreatePractitionerDTO,
    CreateUpdatePractitionerResponse,
    GetPractitionerResponse,
    PractitionerFilterResponse,
    PractitionerFiltersDTO,
    UpdatePractitionerDTO,
)

logger = logging.getLogger(__name__)


class Practitioner(BaseService):
    """
    SDK-friendly Practitioner service for managing practitioner-related operations.

    This class provides asynchronous methods to interact with practitioner records:
    retrieving lists and individual records, creating new practitioners, updating existing records,
    deleting practitioners, and searching with complex filters.

    Data validation and transformation is strictly performed via Pydantic-based DTOs for API reliability.
    The service manages errors gracefully and logs operation details for audit and troubleshooting.

    Args:
        config (ClientConfig): Configuration including API keys, base URL, and other connection parameters.

    Raises:
        EhrApiError: If an error occurs during API calls.
        ValidationError: If input data does not conform to expected schemas.

    Example:
        ```
        config = ClientConfig(api_key="your_api_key")
        practitioner_service = Practitioner(config)

        # Fetch first page of practitioners
        practitioners = asyncio.run(practitioner_service.find_all())
        print(f"Total practitioners: {practitioners.total}")

        # Fetch individual practitioner by ID
        practitioner = asyncio.run(practitioner_service.find_by_id("pract123"))
        print(practitioner.request_resource["firstName"])

        # Create a new practitioner
        new_practitioner = {
            "registrationId": "REG12345",
            "department": "Cardiology",
            "designation": "Senior Consultant",
            "status": "Active",
            "joiningDate": "2020-01-15",
            "staffType": "Doctor",
            "firstName": "Alice",
            "lastName": "Smith",
            "birthDate": "1980-06-10",
            "gender": "F",
            "mobileNumber": "+919876543210",
            "emailId": "alice.smith@example.com",
            "address": "123 Medical Street, City",
            "pincode": "110001",
            "state": "Delhi",
            "resourceType": "Practitioner"
        }
        created = asyncio.run(practitioner_service.create(new_practitioner))
        print(created.message)
        ```
    """

    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def __validate_data(
        self, dto_type: Type[BaseModel], request_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validates input data against the specified Pydantic DTO schema.

        Args:
            dto_type (Type[BaseModel]): The Pydantic model class to validate against.
            request_data (dict): The raw input data dictionary.

        Returns:
            dict: Validated data serialized with DTO aliases.

        Raises:
            EhrError: When validation fails with detailed error info.

        Example:
            ```
            validated = await practitioner_service.__validate_data(
                CreatePractitionerDTO,
                {
                    "registrationId": "REG12345",
                    "department": "Cardiology",
                    ...
                },
            )
            ```
        """
        try:
            validated_data = dto_type(**request_data)
            return validated_data.model_dump(by_alias=True)
        except ValidationError as err:
            self.logger.exception("Validation failed in PractitionerService.")
            raise EhrApiError("Validation error in PractitionerService.", 400) from err

    async def __transform_filter_keys(self, filters: dict[str, Any]) -> dict[str, Any]:
        """
        Transforms filter keys from friendly names to backend API parameter names and sanitizes values.

        Args:
            filters (dict): Raw filter key-value pairs entered by users.

        Returns:
            dict: Filter dict with backend-compatible keys and cleaned values.

        Raises:
            EhrError: On invalid filter value (e.g., non-numeric count).

        Example:
            ```
            raw_filters = {"firstName": "Alice", "count": "10"}
            transformed = await practitioner_service.__transform_filter_keys(raw_filters)
            # transformed == {"name": "Alice", "_count": 10}
            ```
        """
        key_mapping = {
            "firstName": "name",
            "lastName": "family",
            "state": "address-state",
            "count": "_count",
        }

        transformed_filters = {
            key_mapping.get(key, key): (
                int(value) if key_mapping.get(key, key) == "_count" else value
            )
            for key, value in filters.items()
            if value is not None
        }

        # Validate _count separately
        if "_count" in transformed_filters:
            try:
                transformed_filters["_count"] = int(transformed_filters["_count"])
            except ValueError as e:
                raise EhrApiError(
                    status_code=400,
                    message="Invalid value for _count. It should be a numeric value.",
                ) from e

        return transformed_filters

    async def create(
        self, practitioner: dict[str, Any]
    ) -> CreateUpdatePractitionerResponse:
        """
        Creates a new practitioner record.

        Args:
            practitioner (CreatePractitionerDTO): Practitioner creation data matching CreatePractitionerDTO schema.

        Returns:
            CreatePractitionerResponse: Confirmation and created resource details.

        Raises:
            EhrError: On validation failure, duplicate record, or API error.

        Example:
            ```
            new_prac = {
                "registrationId": "REG5678",
                "department": "Neurology",
                "designation": "Consultant",
                "status": "Active",
                "joiningDate": "2021-05-10",
                "staffType": "Doctor",
                "firstName": "Bob",
                "lastName": "John",
                "birthDate": "1975-09-22",
                "gender": "M",
                "mobileNumber": "+919876543210",
                "emailId": "bob.john@example.com",
                "address": "456 Medical Lane, City",
                "pincode": "560001",
                "state": "Karnataka",
                "resourceType": "Practitioner"
            }
            created = await practitioner_service.create(new_prac)
            print(created.message)
            ```
        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Practitioner created successfully.",
                "resourceId": "pract123"
            }
        """
        if not practitioner:
            raise EhrApiError("Practitioner data cannot be null.", 400)

        validated_data = await self.__validate_data(CreatePractitionerDTO, practitioner)
        try:
            response = await self.post(
                PractitionerEndPoints.CREATE_PRACTITIONER,
                validated_data,
                response_model=CreateUpdatePractitionerResponse,
            )
            return response
        except EhrApiError as e:
            if e.status_code == 409:
                raise EhrApiError(
                    "Practitioner already exists. Consider updating the existing record instead."
                ) from e
            raise EhrApiError(f"Failed to create practitioner: {str(e)}") from e

    async def find_all(
        self, next_page: Optional[str] = None
    ) -> GetPractitionerResponse:
        """
        Retrieves the list of practitioners, paginated.

        Args:
            next_page (str, optional): Pagination token from previous call to fetch next page.

        Returns:
            GetPractitionerResponse: Contains practitioner list, pagination info, and total count.

        Raises:
            EhrError: On API communication or authentication failure.

        Example:
            ```
            response = await practitioner_service.find_all()
            print(f"Total practitioners: {response.total}")
            for p in response.request_resource:
                print(p["firstName"], p["department"])
            ```
        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Practitioners fetched successfully.",
                "request_resource": [
                    {
                        "registrationId": "REG5678",
                        "firstName": "Alice",
                        "department": "Neurology",
                        ...
                    },
                    ...
                ],
                "total_number_of_records": 25,
                "next_page_link": "token123"
            }
        """
        try:
            params = {"nextPage": next_page} if next_page else None
            response = await self.get(
                PractitionerEndPoints.GET_ALL_PRACTITIONERS,
                response_model=GetPractitionerResponse,
                query_params=params,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.exception(
                "An unexpected error occurred while fetching all practitioners"
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching all practitioners: {e}",
                500,
            ) from e

    async def find_by_id(self, practitioner_id: str) -> GetPractitionerResponse:
        """
        Retrieves detailed information about a specific practitioner.

        Args:
            practitioner_id (str): Unique identifier of the practitioner.

        Returns:
            GetPractitionerResponse: Practitioner data response object.

        Raises:
            EhrError: On invalid ID, not found, or API error.

        Example:
            ```
            practitioner = await practitioner_service.find_by_id("pract123")
            print(practitioner.request_resource["firstName"])
            ```
        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Practitioner found successfully.",
                "request_resource": {
                    "registrationId": "REG5678",
                    "firstName": "Alice",
                    "department": "Neurology",
                    ...
                }
            }
        """
        if not practitioner_id:
            raise EhrApiError("Practitioner ID cannot be null or empty.", 400)
        try:
            response = await self.get(
                PractitionerEndPoints.GET_PRACTITIONER_BY_ID.format(
                    practitioner_id=practitioner_id
                ),
                response_model=GetPractitionerResponse,
            )
            return response
        except EhrApiError as e:
            raise e

    async def exists(self, practitioner_id: str) -> bool:
        """
        Checks if a practitioner exists based on their ID.

        Args:
            practitioner_id (str): Unique practitioner ID.

        Returns:
            bool: True if practitioner exists, False otherwise.

        Raises:
            EhrError: On API errors.

        Example:
            ```
            exists = await practitioner_service.exists("pract123")
            print("Exists:", exists)
            ```
        ### Response:
            Sample Output:
            "Exists: True" or "Exists: False" based on practitioner existence.
        """
        if not practitioner_id:
            return False
        try:
            response = await self.get(
                PractitionerEndPoints.PRACTITIONER_EXISTS.format(
                    practitioner_id=practitioner_id
                ),
                response_model=GetPractitionerResponse,
            )
            return response.message == "Practitioner Found !!!"
        except EhrApiError:
            return False

    async def update(
        self, update_practitioner_data: dict[str, Any]
    ) -> CreateUpdatePractitionerResponse:
        """
        Updates an existing practitioner record.

        Args:
            update_practitioner_data (UpdatePractitionerDTO): Data to update per UpdatePractitionerDTO schema.

        Returns:
            CreatePractitionerResponse: Confirmation and updated resource details.

        Raises:
            EhrError: On validation failure or API error.

        Example:
            ```
            update_info = {
                "registrationId": "REG5678",
                "designation": "Senior Consultant",
                "status": "Active",
                "joiningDate": "2021-05-10",
                "staffType": "Doctor",
                "firstName": "Bob",
                "lastName": "John",
                "birthDate": "1975-09-22",
                "gender": "M",
                "mobileNumber": "+919876543210",
                "emailId": "bob.new@example.com",
                "address": "789 New Medical St, City",
                "pincode": "560002",
                "state": "Karnataka",
                "resourceType": "Practitioner",
                "resourceId": "pract123"
            }
            updated = await practitioner_service.update(update_info)
            print(updated.message)
            ```
        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Practitioner updated successfully.",
                "resourceId": "pract123"
            }
        """
        if not update_practitioner_data:
            raise EhrApiError("Update practitioner data cannot be null.", 400)

        validated_data = await self.__validate_data(
            UpdatePractitionerDTO, update_practitioner_data
        )
        try:
            response = await self.put(
                PractitionerEndPoints.UPDATE_PRACTITIONER,
                validated_data,
                response_model=CreateUpdatePractitionerResponse,
            )
            return response
        except EhrApiError as e:
            raise e

    async def find_by_filters(
        self, filters: dict[str, Any], next_page: Optional[str] = None
    ) -> PractitionerFilterResponse:
        """
        Searches for practitioners matching filter criteria and supports pagination.

        Raw user-entered filter keys are mapped to backend field names.

        Args:
            filters (dict): Filter conditions such as firstName, lastName, state, etc.
            next_page (str, optional): Pagination token for subsequent pages.

        Returns:
            PractitionerFilterResponse: Contains matching practitioner entries and pagination info.

        Raises:
            EhrError: On validation or API failure.

        Example:
            ```
            filter_conditions = {
                "firstName": "Alice",
                "state": "Karnataka",
                "count": 10
            }
            results = await practitioner_service.find_by_filters(filter_conditions)
            print(f"Total found: {results.total}")
            for practitioner in results.entry:
                print(practitioner["firstName"], practitioner["department"])
            ```
        ### Response:
            Sample Output:
            {
                "entry": [
                    {
                        "registrationId": "REG5678",
                        "firstName": "Alice",
                        "department": "Neurology",
                        ...
                    },
                    ...
                ],
                "link": {"nextPage": "token123"},
                "total": 25
            }
        """
        try:
            validated_filters = PractitionerFiltersDTO(**filters).model_dump(
                by_alias=True, exclude_none=True
            )

            transformed_filters = await self.__transform_filter_keys(validated_filters)

            params = {"filters": json.dumps(transformed_filters)}
            if next_page:
                params["nextPage"] = next_page

            response = await self.get(
                PractitionerEndPoints.GET_PRACTITIONER_BY_FILTERS,
                PractitionerFilterResponse,
                params,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred while fetching practitioners by filters: {e}"
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching practitioners by filters: {e}",
                500,
            ) from e

    async def delete(self, practitioner_id: str) -> None:
        """
        Deletes a practitioner by their unique ID.

        Args:
            practitioner_id (str): Unique identifier.

        Raises:
            EhrError: On invalid ID or API failure.

        Example:
            ```
            await practitioner_service.delete("pract123")
            print("Practitioner deleted successfully")
            ```
        ### Response:
            Sample Output:
            "Practitioner deleted successfully" or raises an error if deletion fails.

            ### Note:
            This operation is irreversible. Ensure the practitioner is no longer needed before deletion.
        """
        try:
            await super().delete(
                PractitionerEndPoints.DELETE_PRACTITIONER.format(
                    practitioner_id=practitioner_id
                )
            )
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred while deleting practitioner: {e}"
            )
            raise EhrApiError(f"Failed to delete practitioner: {str(e)}") from e
