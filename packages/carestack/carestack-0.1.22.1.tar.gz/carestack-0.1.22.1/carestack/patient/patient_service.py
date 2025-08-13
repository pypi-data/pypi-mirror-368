import json
import logging
from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import PatientEndpoints
from carestack.patient.patient_dto import (
    CreateUpdatePatientResponse,
    GetPatientResponse,
    PatientDTO,
    PatientFilterResponse,
    PatientFiltersDTO,
    UpdatePatientDTO,
)


class Patient(BaseService):
    """
    SDK-friendly PatientService for managing patient-related operations.

    This service provides methods to interact with patient records in the backend,
    including creating, updating, deleting, and retrieving patient information.
    It abstracts the underlying API calls and provides a clean interface for client applications.
    It also includes advanced filtering capabilities to search for patients based on various criteria.

    All data is validated and transformed via Pydantic DTOs ensuring type safety and correct API usage.
    The service also includes robust logging and error handling for operational reliability.

    !!! note "Key Features"
        - Fetch all patients with pagination support.
        - Retrieve patient details by ID.
        - Create new patient records with validation.
        - Update existing patient records.
        - Delete patient records by ID.
        - Advanced filtering capabilities for patient search.

    Methods:
        find_all: Fetches all patients with optional pagination.
        find_by_id: Retrieves a patient by their unique ID.
        exists: Checks if a patient exists by their ID.
        create: Creates a new patient record.
        update: Updates an existing patient record.
        delete: Deletes a patient record by their ID.
        find_by_filters: Retrieves patients based on advanced filters.



    Args:
        config (ClientConfig): API credentials and configuration for backend connection.

    Example Usage:
        ```
        config = ClientConfig(api_key="your_api_key")
        patient_service = Patient(config)

        # Fetch all patients (first page)
        patients = await patient_service.find_all()

        # Fetch a specific patient by ID
        patient = await patient_service.find_by_id("patient12345")

        # Create a new patient
        new_patient_data = {
        "idNumber": "123456789012",
        "idType": "Aadhaar",
        "patientType": "OPD",
        "firstName": "John",
        "lastName": "Doe",
        "birthDate": "1980-01-01",
        "gender": "M",
        "address": "123 Main Street",
        "resourceType": "PATIENT"
        }
        created_patient = await patient_service.create(new_patient_data)
        ```
    """

    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def __validate_data(
        self, dto_type: Type[BaseModel], request_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate input data with the specified Pydantic DTO schema.

        ### Args:
            dto_type (Type[BaseModel]): Pydantic model class for validating the input.
            request_data (dict[str, Any]): Raw input data dictionary.

        Returns:
            dict[str, Any]: Validated data dictionary with aliased keys.

        ### Raises:
            EhrApiError: If validation fails with details logged.

        Example:
            ```
            validated = await patient_service.__validate_data(PatientDTO, {
                "idNumber": "123456789012",
                "idType": "Aadhaar",
                ...
            })
            ```
        """
        try:
            validated_data = dto_type(**request_data)
            return validated_data.model_dump(by_alias=True)
        except ValidationError as err:
            self.logger.exception("Validation failed during DTO parsing.")
            raise EhrApiError("Patient data validation error.", 400) from err

    async def __transform_filter_keys(self, filters: dict[str, Any]) -> dict[str, Any]:
        """
        Transforms filter keys to match the expected API format.

        ### Args:
            filters (dict[str, Any]): Input filters.

        Returns:
            dict[str, Any]: Transformed filters.
        """
        key_mapping = {
            "first_name": "name",
            "last_name": "family",
            "email": "email",
            "state": "address-state",
            "count": "_count",
            "id_number": "identifier",
            "phone": "phone",
            "gender": "gender",
            "birth_date": "birthDate",
            "organization": "organization",
            "from_date": "from_date",
            "to_date": "to_date",
            "page_size": "page_size",
        }

        return {
            key_mapping.get(key.lower(), key): value for key, value in filters.items()
        }

    async def create(self, patient: dict[str, Any]) -> CreateUpdatePatientResponse:
        """
        Creates a new patient record in the system.

        Args:
            patient (PatientDTO): Data for the new patient to be created.

        Returns:
            CreateUpdatePatientResponse: Details about the created patient.


        Raises:
            EhrApiError: For validation failures or backend errors.

        Example:
            ```
            new_patient = {
                "idNumber": "123456789012",
                "idType": "Aadhaar",
                "patientType": "OPD",
                "firstName": "Jane",
                "lastName": "Doe",
                "birthDate": "1990-05-10",
                "gender": "F",
                "address": "456 Secondary Rd",
                "resourceType": "PATIENT"
            }
            created = await patient_service.create(new_patient)
            print(created.resource['idNumber'], created.message)
            ```
        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Patient created successfully",
                "resourceId": "patient123",
                "resource": {
                    "idNumber": "123456789012",
                    "firstName": "Jane",
                    "lastName": "Doe",
                    ...
                },
                "validationErrors": []
            }
        """
        if not patient:
            raise EhrApiError("Patient data cannot be null.", 400)

        validated_data = await self.__validate_data(PatientDTO, patient)
        try:
            response = await self.post(
                PatientEndpoints.CREATE_PATIENT,
                validated_data,
                response_model=CreateUpdatePatientResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while creating patient: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while creating patient: {e}", 500
            ) from e

    async def find_all(self, next_page: Optional[str] = None) -> GetPatientResponse:
        """
        Retrieves a paginated list of all patients accessible to the current user or organization.

        Args:
            next_page (Optional[str]): Token for fetching the next page of results.

        Returns:
            GetPatientResponse: Contains patient entries, pagination info, and metadata.

        Raises:
            EhrApiError: For HTTP or backend errors.

        Example:
            ```
            response = await patient_service.find_all()
            print(f"Total records: {response.total_records}")
            for patient in response.request_resource or []:
                print(patient['idNumber'], patient['firstName'])
            ```
        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Patients retrieved successfully",
                "requestResource": [
                    {
                        "idNumber": "123456789012",
                        "firstName": "John",
                        "lastName": "Doe",
                        ...
                    },
                    ...
                ],
                "totalNumberOfRecords": 150,
                "nextPage": "token_abc123"
            }
        """
        try:
            params = {"nextPage": next_page} if next_page else None
            response = await self.get(
                PatientEndpoints.GET_ALL_PATIENTS,
                response_model=GetPatientResponse,
                query_params=params,
            )
            return response
        except EhrApiError as e:
            self.logger.error("Error fetching all patients: %s", e, exc_info=True)
            raise
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching all patients: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching all patients: {e}", 500
            ) from e

    async def find_by_id(self, patient_id: str) -> GetPatientResponse:
        """
        Retrieves detailed information for a patient by their unique ID.

        Args:
            patient_id (str): Unique patient identifier.

        Returns:
            GetPatientResponse: Patient detail response object.

        Raises:
            EhrApiError: For invalid ID or API errors.

        Example:
            ```
            patient = await patient_service.find_by_id("patient123")
            print(patient.request_resource['firstName'], patient.request_resource['lastName'])
            ```
        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Patient found",
                "requestResource": {
                    "idNumber": "123456789012",
                    "firstName": "John",
                    "lastName": "Doe",
                    "birthDate": "1980-01-01",
                    ...
                },
                "totalNumberOfRecords": 1,
                "nextPage": null
            }
        """
        if patient_id is None or patient_id.strip() == "":
            raise EhrApiError("Patient ID cannot be null or empty.", 400)
        try:
            response = await self.get(
                PatientEndpoints.GET_PATIENT_BY_ID.format(patient_id=patient_id),
                response_model=GetPatientResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching all patients: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching patient by Id: {e}", 500
            ) from e

    async def exists(self, patient_id: str) -> bool:
        """
        Checks whether a patient exists in the registry by patient ID.

        Args:
            patient_id (str): Unique ID of the patient.

        Returns:
            bool: True if the patient exists, False otherwise.

        Raises:
            EhrApiError: If there is an error during the API request.
            Exception: For unexpected errors during the operation.

        Example:
            ```
            exists = await patient_service.exists("patient123")
            print("Exists:", exists)
            ```
        ### Response:
            Sample Output:
            True if patient exists, False if not found or error occurs.
            False if patient ID is invalid or not found.

        """
        if not patient_id:
            return False
        try:
            response = await self.get(
                PatientEndpoints.PATIENT_EXISTS.format(patient_id=patient_id),
                GetPatientResponse,
            )
            return response.message == "Patient Found !!!"
        except EhrApiError:
            return False

        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching patient: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching patient by Id: {e}", 500
            ) from e

    async def update(
        self, update_patient_data: dict[str, Any]
    ) -> CreateUpdatePatientResponse:
        """
        Updates an existing patient record with provided data.

        Args:
            update_patient_data (UpdatePatientDTO): Data for updating the patient record.

        Returns:
            CreateUpdatePatientResponse: Updated patient details.

        ### Raises:
            EhrApiError: For validation or API errors.

        Example:
            ```
            update_fields = {
                "resourceId": "patient123",
                "emailId": "jane.doe@example.com",
                "mobileNumber": "+919876543210",
                "resourceType": "PATIENT"
            }
            updated = await patient_service.update(update_fields)
            print(updated.message)
            ```
        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Patient updated successfully",
                "resourceId": "patient123",
                "resource": {
                    "emailId": "jane.doe@example.com",
                    "mobileNumber": "+919876543210",
                    ...
                },
                "validationErrors": []
            }
        """
        if not update_patient_data:
            raise EhrApiError("Update patient data cannot be null.", 400)

        validated_data = await self.__validate_data(
            UpdatePatientDTO, update_patient_data
        )
        try:
            response = await self.put(
                PatientEndpoints.UPDATE_PATIENT,
                validated_data,
                CreateUpdatePatientResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while updating patient: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while updating patient: {e}", 500
            ) from e

    async def delete(self, patient_id: str) -> None:
        """
        Deletes a patient record by their unique ID.

        Args:
            patient_id (str): Unique identifier of the patient.

        Raises:
            EhrApiError: When ID is invalid or deletion fails.

        Example:
            ```
            await patient_service.delete("patient123")
            print("Patient deleted successfully.")
            ```
        ### Response:
            Sample Output:
            No content returned on successful deletion.

            ### Raises:
            EhrApiError: If patient ID is invalid or deletion fails.
            Exception: Any other unexpected exceptions during deletion.
        """
        if not patient_id:
            raise EhrApiError("Patient ID cannot be null or empty.", 400)
        try:
            await super().delete(
                PatientEndpoints.DELETE_PATIENT.format(patient_id=patient_id),
            )
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while deleting patient: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while deleting patient: {e}", 500
            ) from e

    async def find_by_filters(
        self, filters: dict[str, Any], next_page: Optional[str] = None
    ) -> PatientFilterResponse:
        """
        Retrieves patients based on filter criteria.

        Args:
            filters (dict[str, Any]): Filtering criteria.
            next_page (Optional[str]): Pagination token.

        Returns:
            PatientFilterResponse: Filtered patient data.

        Raises:
            EhrApiError: If there is an error during the API request or validation.
        """
        try:
            validated_filters = PatientFiltersDTO(**filters).model_dump(
                by_alias=True, exclude_none=True
            )
            transformed_filters = await self.__transform_filter_keys(validated_filters)
            params = {"filters": json.dumps(transformed_filters)}
            if next_page:
                params["nextPage"] = next_page

            response = await self.get(
                PatientEndpoints.GET_PATIENT_BY_FILTERS, PatientFilterResponse, params
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching patients by filters: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while fetching patients by filters: {e}",
                500,
            ) from e
