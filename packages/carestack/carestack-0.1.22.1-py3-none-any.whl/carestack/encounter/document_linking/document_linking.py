import logging
import re
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, RootModel, ValidationError

from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import DOCUMENT_LINKING_ENDPOINTS, HealthInformationTypes

from carestack.encounter.document_linking.dto.create_care_context_dto import (
    CreateCareContextDTO,
    CreateCareContextResponse,
)
from carestack.encounter.document_linking.dto.health_document_linking_dto import (
    HealthDocumentLinkingDTO,
)
from carestack.encounter.document_linking.dto.link_care_context_dto import (
    LinkCareContextDTO,
)
from carestack.encounter.document_linking.dto.update_visit_records_dto import (
    UpdateVisitRecordsDTO,
    UpdateVisitRecordsResponse,
)
from carestack.encounter.document_linking.schema import (
    map_to_consultation_dto,
    map_to_create_care_context_dto,
    map_to_link_care_context_dto,
)


class TransactionState:
    """
    Represents the state of a document linking transaction.

    Attributes:
        care_context_reference (Optional[str]): Reference to the created care context.
        request_id (Optional[str]): Unique request identifier for the transaction.
        appointment_created (bool): Indicates if the appointment was created.
        care_context_created (bool): Indicates if the care context was created.
        visit_records_updated (bool): Indicates if visit records were updated.
        care_context_linked (bool): Indicates if the care context was linked.
    """

    def __init__(self) -> None:
        self.care_context_reference: Optional[str] = None
        self.request_id: Optional[str] = None
        self.appointment_created: bool = False
        self.care_context_created: bool = False
        self.visit_records_updated: bool = False
        self.care_context_linked: bool = False

    def __str__(self) -> str:
        return (
            f"care_context_reference={self._mask_data(self.care_context_reference)}, request_id={self._mask_data(self.request_id)}, "
            f"appointment_created={self.appointment_created}, care_context_created={self.care_context_created}, "
            f"visit_records_updated={self.visit_records_updated}, care_context_linked={self.care_context_linked})"
        )

    def _mask_data(self, data: Optional[str]) -> str:
        """
        Masks sensitive data for logging purposes.

        Args:
            data (Optional[str]): The data to mask.

        Returns:
            str: Masked data string.
        """
        if data is None:
            return "null"
        if len(data) <= 4:
            return "*" * len(data)
        return data[:2] + "*" * (len(data) - 4) + data[-2:]


class GenericDictResponseSchema(RootModel[dict[str, Any]]):
    """
    Root model for generic dictionary-based API responses.
    """

    pass


class DocumentLinking(BaseService):
    """
    Service responsible for linking health documents through a multi-step process.

    This service manages the workflow for associating health records, care contexts, and visit records
    with a patient, ensuring data validation, serialization, and robust error handling throughout the process.

    !!! note "Key Features"
        - Validates and serializes DTOs for document linking operations.
        - Handles creation of care contexts, updating visit records, and linking care contexts.
        - Maintains transaction state for traceability and error reporting.
        - Provides detailed logging and error messages for each step.

    Methods:
        create_care_context: Maps and validates care context data.
        send_care_context_request: Sends care context creation request to the API.
        update_visit_records: Updates visit records with consultation data.
        link_care_context: Links the care context to the health document.
        link_health_document: Orchestrates the complete document linking process.

    Args:
        config (ClientConfig): API credentials and settings for service initialization.

    Raises:
        EhrApiError: For validation, API, or unexpected errors during operations.

    Example Usage:
        ```
        config = ClientConfig(
            api_key="your_api_key",
        )
        service = DocumentLinking(config)

        health_document_linking_dto = HealthDocumentLinkingDTO(
            patientReference="pat-123",
            practitionerReference="prac-456",
            appointmentReference="appt-789",
            patientAddress="123 Main St",
            patientName="John Doe",
            appointmentStartDate="2024-07-30T09:00:00",
            appointmentEndDate="2024-07-30T10:00:00",
            appointmentPriority=AppointmentPriority.ROUTINE,
            appointmentType=AppointmentType.VISIT,
            organizationId="org-789",
            appointmentSlot="slot-001",
            reference="ref-001",
            mobileNumber="1234567890",
            healthRecords=[HealthInformationDTO(
                rawFhir=True,
                fhirDocument={"key": "value"},
                informationType=HealthInformationTypes.OPConsultation
            )]
        )
        await service.link_health_document(health_document_linking_dto)
        ```
    """

    def __init__(self, config: ClientConfig) -> None:
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def _validate_data(self, data: Any) -> None:
        """
        Validates the input data against the expected DTO type.

        Args:
            data (Any): The DTO instance to validate.

        Raises:
            ValueError: If validation fails or the DTO type is unsupported.
        """
        if data is None:
            raise ValueError("Input data cannot be null")
        try:
            if isinstance(data, HealthDocumentLinkingDTO):
                self._validate_health_document_linking_dto(data)
            elif isinstance(data, CreateCareContextDTO):
                self._validate_create_care_context_dto(data)
            elif isinstance(data, UpdateVisitRecordsDTO):
                self._validate_consultation_dto(data)
            elif isinstance(data, LinkCareContextDTO):
                self._validate_link_care_context_dto(data)
            else:
                raise TypeError(f"Unsupported DTO type: {type(data)}")
        except ValidationError as e:
            self.logger.exception(f"Validation error: {e}")
            raise ValueError(f"Validation failed: {e}") from e

    def _validate_health_document_linking_dto(
        self, dto: HealthDocumentLinkingDTO
    ) -> None:
        """
        Validates the HealthDocumentLinkingDTO fields for required values and correct formats.

        Args:
            dto (HealthDocumentLinkingDTO): The DTO to validate.

        Raises:
            ValueError: If any required field is missing or invalid.
        """
        self._validate_not_empty(dto.patient_reference, "patientReference")
        self._validate_not_empty(dto.practitioner_reference, "practitionerReference")

        if not (
            len(dto.patient_reference) in (32, 36)
            and dto.patient_reference.replace("-", "").isalnum()
        ):
            raise ValueError(
                "Patient reference must be a valid 32 or 36 character UUID"
            )

        self._validate_not_empty(
            str(dto.appointment_start_date), "appointmentStartDate"
        )
        self._validate_not_empty(str(dto.appointment_end_date), "appointmentEndDate")
        if dto.appointment_priority is not None and not dto.appointment_priority.value:
            raise ValueError("Appointment priority cannot be empty")
        self._validate_not_empty(dto.organization_id, "organizationID")
        self._validate_not_empty(dto.mobile_number, "mobileNumber")

    def _validate_create_care_context_dto(self, dto: CreateCareContextDTO) -> None:
        """
        Validates the CreateCareContextDTO fields for required values and correct UUID formats.

        Args:
            dto (CreateCareContextDTO): The DTO to validate.

        Raises:
            ValueError: If any required field is missing or invalid.
        """
        self._validate_not_empty(str(dto.patient_reference), "patientReference")
        self._validate_not_empty(
            str(dto.practitioner_reference), "practitionerReference"
        )
        self._validate_not_empty(dto.appointment_reference, "appointmentReference")
        self._validate_not_empty(dto.appointment_date, "appointmentDate")

        uuid_pattern = r"^[a-fA-F0-9-]{36}$"
        for value, field in [
            (dto.patient_reference, "patientReference"),
            (dto.practitioner_reference, "practitionerReference"),
            (dto.appointment_reference, "appointmentReference"),
        ]:
            if not re.fullmatch(uuid_pattern, str(value)):
                raise ValueError(f"{field} must be a valid 36-character UUID")

        if dto.resend_otp is None:
            raise ValueError("Resend OTP flag is required")

    def _validate_consultation_dto(self, dto: UpdateVisitRecordsDTO) -> None:
        """
        Validates the UpdateVisitRecordsDTO fields for required values.

        Args:
            dto (UpdateVisitRecordsDTO): The DTO to validate.

        Raises:
            ValueError: If any required field is missing.
        """
        for field_value, field_name in [
            (dto.care_context_reference, "careContextReference"),
            (dto.patient_reference, "patientReference"),
            (dto.practitioner_reference, "practitionerReference"),
            (dto.appointment_reference, "appointmentReference"),
        ]:
            self._validate_not_empty(field_value, field_name)

    def _validate_link_care_context_dto(self, dto: LinkCareContextDTO) -> None:
        """
        Validates the LinkCareContextDTO fields for required values.

        Args:
            dto (LinkCareContextDTO): The DTO to validate.

        Raises:
            ValueError: If any required field is missing.
        """
        for field_value, field_name in [
            (dto.request_id, "requestId"),
            (dto.appointment_reference, "appointmentReference"),
            (dto.patient_address, "patientAddress"),
            (dto.patient_reference, "patientReference"),
            (dto.care_context_reference, "careContextReference"),
            (dto.auth_mode.value, "authMode"),
        ]:
            self._validate_not_empty(field_value, field_name)

    def _validate_not_empty(self, value: Optional[str], field_name: str) -> None:
        """
        Checks if a value is not None or empty.

        Args:
            value (Optional[str]): The value to check.
            field_name (str): The name of the field.

        Raises:
            ValueError: If the value is None or empty.
        """
        if not value:
            raise ValueError(f"{field_name} cannot be null or empty")

    def _serialize_model(self, model: BaseModel) -> dict[str, Any]:
        """
        Helper function to serialize a Pydantic model, handling special types like UUID and enums.

        Args:
            model (BaseModel): The Pydantic model to serialize.

        Returns:
            dict[str, Any]: The serialized dictionary.
        """
        serialized: dict[str, Any] = {}
        for key, value in model.model_dump(
            by_alias=True, exclude_none=True, mode="json"
        ).items():
            if isinstance(value, UUID):
                serialized[key] = str(value)
            elif isinstance(value, HealthInformationTypes):
                serialized[key] = value.value
            elif isinstance(value, list):
                serialized[key] = [
                    self._serialize_model(item) if isinstance(item, BaseModel) else item
                    for item in value
                ]
            else:
                serialized[key] = value
        return serialized

    async def create_care_context(
        self,
        health_document_linking_dto: HealthDocumentLinkingDTO,
    ) -> CreateCareContextDTO:
        """
        Creates care context data from the provided health document linking information.

        This method maps the incoming HealthDocumentLinkingDTO into a CreateCareContextDTO,
        then validates the mapped DTO before returning it for further processing.

        Args:
            health_document_linking_dto (HealthDocumentLinkingDTO):
                DTO containing health document linking data, including patient/practitioner references,
                appointment dates, priority, organization, mobile number, and health records.

        Returns:
            CreateCareContextDTO: A new DTO representing the care context ready to be sent to the API.

        Raises:
            ValueError: If the input data is None or not a HealthDocumentLinkingDTO instance,
                        or if validation fails.

        Example:
            ```
            linking_dto = HealthDocumentLinkingDTO(
                patientReference="123e4567-e89b-12d3-a456-426614174000",
                practitionerReference="321e4567-e89b-12d3-a456-426614174000",
                patientAddress="123 Elm St",
                patientName="John Doe",
                appointmentStartDate="2025-08-01T09:00:00Z",
                appointmentEndDate="2025-08-01T09:30:00Z",
                appointmentPriority="ROUTINE",
                organizationId="Org123",
                mobileNumber="9876543210",
                hiType="OPConsultation",
                healthRecords=[rawFhir=True, fhirDocument={"key": "value"}, informationType=HealthInformationTypes.OPConsultation]
            )
            care_context_dto = await service._create_care_context(linking_dto)
            print(care_context_dto)
            ```

        ### Response:
            The returned `CreateCareContextDTO` instance, validated and ready for API use.
            {
                "patientReference": "123e4567-e89b-12d3-a456-426614174000",
                "practitionerReference": "321e4567-e89b-12d3-a456-426614174000",
                "appointmentReference": "appt-123",
                "appointmentDate": "2025-08-01T09:00:00Z",
                "resendOtp": false,
                "hiType": "OPConsultation"
            }
        """
        if health_document_linking_dto is None or not isinstance(
            health_document_linking_dto, HealthDocumentLinkingDTO
        ):
            raise ValueError("Input data cannot be null")
        care_context_data = map_to_create_care_context_dto(
            health_document_linking_dto,
        )
        await self._validate_data(care_context_data)
        return care_context_data

    async def send_care_context_request(
        self, care_context_data: CreateCareContextDTO
    ) -> CreateCareContextResponse:
        """
        Sends the care context creation request to the backend API.

        Serializes the care context DTO to a dictionary, sends it to the specified endpoint,
        and parses the response into CreateCareContextResponse.

        Args:
            care_context_data (CreateCareContextDTO): Validated care context data to transmit.

        Returns:
            CreateCareContextResponse: API response containing care context reference, request ID, and status.

        Example:
            ```
            response = await service._send_care_context_request(care_context_dto)
            print(response.care_context_reference, response.request_id)
            ```

        ### Response:
            Sample Output:
            {
                "careContextReference": "cc-12345",
                "requestId": "req-12345",
                "authModes": ["DEMOGRAPHICS", "MOBILE_OTP"]
            }
        """
        data_to_send = self._serialize_model(care_context_data)
        response = await self.post(
            DOCUMENT_LINKING_ENDPOINTS.CREATE_CARE_CONTEXT,
            data_to_send,
            response_model=CreateCareContextResponse,
        )
        return response

    async def update_visit_records(
        self,
        health_document_linking_dto: HealthDocumentLinkingDTO,
        care_context_response: CreateCareContextResponse,
    ) -> UpdateVisitRecordsResponse:
        """
        Updates visit records with the consultation data mapped from health document linking information.

        This method maps the DTO into UpdateVisitRecordsDTO, validates it, serializes it,
        and calls the update visit records API endpoint.

        Args:
            health_document_linking_dto (HealthDocumentLinkingDTO): Input data containing health document details.
            care_context_response (CreateCareContextResponse): Response from care context creation to extract references.

        ### Returns:
            UpdateVisitRecordsResponse: API response indicating success or failure of the visit record update.

        Example:
            ```
            update_response = await service._update_visit_records(
                linking_dto, care_context_response
            )
            print(update_response.success)
            ```

        ### Response:
            Sample Output:
            {
                "success": True,
            }
        """
        consultation_data = map_to_consultation_dto(
            health_document_linking_dto,
            care_context_response.care_context_reference,
            care_context_response.request_id,
        )

        await self._validate_data(consultation_data)
        data_to_send = self._serialize_model(consultation_data)

        return await self.post(
            DOCUMENT_LINKING_ENDPOINTS.UPDATE_VISIT_RECORDS,
            data_to_send,
            response_model=UpdateVisitRecordsResponse,
        )

    async def link_care_context(
        self,
        health_document_linking_dto: HealthDocumentLinkingDTO,
        care_context_response: dict[str, Any],
    ) -> bool:
        """
        Links the care context with the existing health document.

        This performs the linkage by mapping to a LinkCareContextDTO, validating, and invoking the API.
        Returns True if linkage was successful.

        Args:
            health_document_linking_dto (HealthDocumentLinkingDTO): DTO with document linking info.
            care_context_response (dict[str, Any]): Response containing careContextReference and requestId.

        Returns:
            bool: True if link operation succeeded, False otherwise.

        Raises:
            ValueError: If required fields are missing or invalid in the DTO.
            EhrApiError: If the API call fails or returns an error status.

        Example:
            ```
            success = await service._link_care_context(
                linking_dto, care_context_resp.model_dump()
            )
            print("Link success:", success)
            ```

        ### Response:
            True  # Indicates linking succeeded
            False  # Indicates linking failed, possibly due to missing care context reference or request ID.

        """
        link_data = map_to_link_care_context_dto(
            health_document_linking_dto,
            care_context_response["careContextReference"],
            care_context_response["requestId"],
        )
        await self._validate_data(link_data)
        response = await self.post(
            DOCUMENT_LINKING_ENDPOINTS.LINK_CARE_CONTEXT,
            link_data.model_dump(by_alias=True, exclude_none=True, mode="json"),
            response_model=bool,
        )
        self.logger.info(f"LinkCareContext API response: {response}")
        return bool(response)

    async def link_health_document(
        self, health_document_linking_dto: HealthDocumentLinkingDTO
    ) -> bool:
        """
        Executes the complete health document linking workflow in three key steps:
          1. Creation of a care context in the system using the provided healthcare document details.
          2. Updating visit records if health records exist within the provided DTO.
          3. Linking the care context with the existing health document to finalize the association.

        This method orchestrates the entire transaction, ensuring validation of all input data,
        managing intermediate responses, maintaining transactional state,
        logging progress comprehensively, and raising detailed exceptions on failures.

        Args:
            health_document_linking_dto (HealthDocumentLinkingDTO):
                A fully populated DTO containing all necessary patient, practitioner, appointment, and health information
                required for the linking operation. This includes references, appointment timings, priority, mobile number,
                health records, and document type.

        Returns:
            bool:
                Returns True if all steps succeed and the health document is fully linked.
                Returns False or raises exceptions if any step fails.

        Raises:
            ValueError:
                Raised when the input data or any intermediate DTO fails validation checks.

            EhrApiError:
                Raised when any interaction with the backend API returns a failure status.
                The error message includes a detailed transaction state snapshot for easier debugging.

            Exception:
                Raised for any unexpected errors that occur during processing.
                Wrapped in EhrApiError with status code 500 and transaction state details.

        Workflow Steps Overview:
            - Validation of the top-level HealthDocumentLinkingDTO.
            - Mapping and validation of CreateCareContextDTO derived from input.
            - Sending create care context request and storing references.
            - Conditional updating of visit records if health records provided.
            - Linking care context to the health document.
            - Updating and logging transaction state throughout.

        Example:
            ```
            # Prepare a DTO with all necessary fields filled
            linking_dto = HealthDocumentLinkingDTO(
                patientReference="123e4567-e89b-12d3-a456-426614174000",
                practitionerReference="321e4567-e89b-12d3-a456-426614174000",
                patientAddress="123 Cedar Street",
                patientName="Jane Doe",
                appointmentStartDate="2025-08-15T14:00:00Z",
                appointmentEndDate="2025-08-15T14:30:00Z",
                appointmentPriority="ROUTINE",
                organizationId="Org987",
                mobileNumber="9998887776",
                hiType="OPConsultation",
                healthRecords=[rawFhir=True, fhirDocument={"key": "value"}, informationType=HealthInformationTypes.OPConsultation]
            )
            # Execute the linking process
            success = await service._link_health_document(linking_dto)
            print("Document linked successfully:", success)
            ```
        ### Response:
            Sample Response:
            True  # Indicates the health document was successfully linked
            False  # Indicates the linking process did not complete successfully, possibly due to missing health records or other issues.
            False if no health records were provided, indicating no visit record update was needed.

        ### Notes:
            - This method assumes the existence of mapping functions:
              `map_to_create_care_context_dto`, `map_to_consultation_dto`, and `map_to_link_care_context_dto`
              to transform data between DTOs.
            - The `TransactionState` object tracks the stages completed and is included in exceptions for traceability.
            - Logging at each step provides detailed insights in case of issues.
        """
        transaction_state = TransactionState()

        try:
            await self._validate_data(health_document_linking_dto)

            # Step 1: Create Care Context
            care_context_data = await self.create_care_context(
                health_document_linking_dto,
            )
            care_context_response = await self.send_care_context_request(
                care_context_data
            )

            transaction_state.care_context_reference = (
                care_context_response.care_context_reference
            )
            transaction_state.request_id = care_context_response.request_id
            transaction_state.care_context_created = True
            self.logger.info(
                f"Care context created with reference: {transaction_state.care_context_reference}"
            )
            response = UpdateVisitRecordsResponse(success=False)

            # Step 2: Update Visit Records (if available)
            if health_document_linking_dto.health_records:
                # If health records are present, update visit records accordingly.
                response = await self.update_visit_records(
                    health_document_linking_dto,
                    care_context_response,
                )
                transaction_state.visit_records_updated = True
            else:
                self.logger.info(
                    "No health records provided. Skipping visit record update."
                )
            # Step 3: Link care context
            link_success = await self.link_care_context(
                health_document_linking_dto,
                care_context_response,
            )
            if link_success:
                transaction_state.care_context_linked = True
                self.logger.info("Health document successfully linked.")

            return response

        except ValueError as e:
            raise ValueError(
                f"Transaction failed due to data validation error: {e}"
            ) from e
        except EhrApiError as e:
            raise EhrApiError(
                message=f"Transaction failed due to API error: {e.message}. Current state: {transaction_state}",
                status_code=e.status_code,
            ) from e
        except Exception as e:
            raise EhrApiError(
                message=f"Transaction failed due to unexpected error: {e}. Current state: {transaction_state}",
                status_code=500,
            ) from e
