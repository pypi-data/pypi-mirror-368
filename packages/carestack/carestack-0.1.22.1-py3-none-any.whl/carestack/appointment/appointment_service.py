import logging
from typing import Optional

from carestack.appointment.appointment_dto import (
    AppointmentDTO,
    AppointmentResponse,
    CreateAppointmentResponeType,
    GetAppointmentResponse,
    UpdateAppointmentDTO,
)
from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import AppointmentEndpoints


class Appointment(BaseService):
    """
    AppointmentService provides a high-level interface for managing appointments within the EHR system.

    This service abstracts the underlying API calls, enabling SDK users to seamlessly create, retrieve,
    update, and delete appointments. It ensures consistent error handling, logging, and data validation,
    making it easier for developers to integrate appointment management into their applications.

    !!! note "Key Features"
        - Validates input data using Pydantic models (AppointmentDTO, UpdateAppointmentDTO, etc.)
        - Handles all CRUD operations for appointment resources.
        - Supports advanced filtering and pagination.
        - Provides robust error handling and logging for all operations.

    Methods:
        create(appointment_data: AppointmentDTO) -> CreateAppointmentResponeType
            Creates a new appointment in the EHR system.
        find_all(next_page: Optional[str] = None) -> GetAppointmentResponse
            Retrieves a paginated list of all appointments.
        find_by_id(appointment_reference: str) -> AppointmentResponse
            Retrieves a specific appointment by its unique reference.
        exists(appointment_reference: str) -> bool
            Checks if an appointment with the given reference exists.
        delete(appointment_reference: str) -> None
            Deletes an appointment by its unique reference.
        update(request_body: UpdateAppointmentDTO) -> AppointmentResponse
            Updates an existing appointment with new data.

    ### Args:
        config (ClientConfig): API credentials and settings for service initialization.

    Raises:
        EhrApiError: For validation, API, or unexpected errors during operations.

    Example Usage:
        ```
        config = ClientConfig(
            api_key="your_api_key"
        )
        service = AppointmentService(config)
        new_appt = AppointmentDTO(
            practitioner_reference="Pract123",
            patient_reference="Pat456",
            appointment_start_time=datetime(2025, 8, 10, 14, 30),
            appointment_end_time=datetime(2025, 8, 10, 15, 0),
            priority=AppointmentPriority.ROUTINE,
            organization_id="Org789",
            slot="Slot12"
        )
        created = await service.create(new_appt)
        all_appts = await service.find_all()
        ```
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def create(
        self, appointment_data: AppointmentDTO
    ) -> CreateAppointmentResponeType:
        """
        Creates a new appointment in the EHR system.

        Sends a request to create an appointment with the specified details.

        Args:
            appointment_data (AppointmentDTO): Pydantic model containing all necessary appointment data.

        ### Returns:
            CreateAppointmentResponeType: Contains:
                - type (str): Status/type of response (e.g., "success").
                - message (str): Informational message about creation.
                - validationErrors (Optional[list]): List of any validation errors.
                - resource (ResourceType): The created appointment details.

        Raises:
            EhrApiError: If the API request fails or returns an error.

        Example:
            ```
            appt_data = AppointmentDTO(
                practitioner_reference="Pract123",
                patient_reference="Pat456",
                appointment_start_time=datetime(2025, 8, 10, 14, 30),
                appointment_end_time=datetime(2025, 8, 10, 15, 0),
                priority=AppointmentPriority.ROUTINE,
             )
            response = await service.create(appt_data)
            print(response.message)
            Appointment created successfully.
            ```

        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Appointment created successfully.",
                "validationErrors": None,
                "resource": {
                    "reference": "APT-001234",
                    "practitionerReference": "Pract123",
                    "patientReference": "Pat456",
                    "slot": "Slot12",
                    "priority": "ROUTINE",
                    "start": "2025-08-10T14:30:00Z",
                    "end": "2025-08-10T15:00:00Z",
                    "organizationId": "Org789"
                }
            }
        """

        response = await self.post(
            AppointmentEndpoints.ADD_APPOINTMENT,
            appointment_data.model_dump(by_alias=True, exclude_none=True, mode="json"),
            response_model=CreateAppointmentResponeType,  # type: ignore
        )
        return response

    async def find_all(self, next_page: Optional[str] = None) -> GetAppointmentResponse:
        """
        Retrieves a paginated list of all appointments accessible to the current user or organization.

        Supports pagination via the `next_page` token to retrieve large datasets efficiently.

        Args:
            next_page (Optional[str], optional): Token indicating the next page of results.

        ### Returns:
            GetAppointmentResponse: Contains:
                - type (str): Response status/type.
                - message (str): Informational message.
                - request_resource (Optional[list[ResourceType]]): List of appointments in this page.
                - total_records (Optional[int]): Total number of appointments available.
                - next_page (Optional[str]): Token/link for the next page.

        Raises:
            EhrApiError: If the API request fails or an unexpected error occurs.

        Example:
            ```
            response = await service.find_all()
            print(f"Total appointments: {response.total_records}")
            for appt in response.request_resource or []:
                print(appt.appointment_reference, appt.patient_reference)
            ```

        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Appointments fetched successfully",
                "requestResource": [
                    {
                        "reference": "APT-001234",
                        "practitionerReference": "Pract123",
                        "patientReference": "Pat456",
                        "slot": "Slot12",
                        "priority": "ROUTINE",
                        "start": "2025-08-10T14:30:00Z",
                        "end": "2025-08-10T15:00:00Z",
                        "organizationId": "Org789"
                    },
                    {
                        "reference": "APT-001235",
                        "practitionerReference": "Pract124",
                        "patientReference": "Pat457",
                        "slot": "Slot13",
                        "priority": "EMERGENCY",
                        "start": "2025-08-11T10:00:00Z",
                        "end": "2025-08-11T10:30:00Z",
                        "organizationId": "Org789"
                    }
                    ...
                ],
                "totalNumberOfRecords": 50,
                "nextPageLink": "token12345"
            }
        """

        try:
            params = {"nextPage": next_page} if next_page else None
            response = await self.get(
                AppointmentEndpoints.GET_ALL_APPOINTMENTS,
                response_model=GetAppointmentResponse,
                query_params=params,
            )
            return response
        except EhrApiError as e:
            self.logger.error("Error fetching all appointments: %s", e, exc_info=True)
            raise
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching all appointments: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while fetching all appointments.", 500
            ) from e

    async def find_by_id(self, appointment_reference: str) -> AppointmentResponse:
        """
        Retrieves a specific appointment by its unique reference.

        Args:
            appointment_reference (str): Unique identifier of the appointment.

        ### Returns:
            AppointmentResponse: Contains:
                - type (str): Response status/type.
                - message (str): Informational message.
                - request_resource (Optional[ResourceType]): Detailed appointment.
                - total_records (Optional[int]): Always 1 or 0 here.
                - next_page (Optional[str]): Usually None for single record.

        Raises:
            EhrApiError: If the reference is invalid or API call fails.

        Example:
            ```
            response = await service.find_by_id("APT-001234")
            print(response.request_resource.patient_reference)
            ```

        ### Response :
            Sample Output:
            {
                "type": "success",
                "message": "Appointment found.",
                "requestResource": {
                    "reference": "APT-001234",
                    "practitionerReference": "Pract123",
                    "patientReference": "Pat456",
                    "slot": "Slot12",
                    "priority": "ROUTINE",
                    "start": "2025-08-10T14:30:00Z",
                    "end": "2025-08-10T15:00:00Z",
                    "organizationId": "Org789"
                },
                "totalNumberOfRecords": 1,
                "nextPageLink": None
            }
        """

        if appointment_reference is None or appointment_reference.strip() == "":
            raise EhrApiError("Appointment Reference cannot be null or empty.", 400)
        try:
            response = await self.get(
                AppointmentEndpoints.GET_APPOINTMENT_BY_ID.format(
                    reference=appointment_reference
                ),
                response_model=AppointmentResponse,
            )
            return response
        except EhrApiError as e:
            self.logger.error("Error fetching appointment: %s", e, exc_info=True)
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while fetching appointment: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while fetching appointment.", 500
            )

    async def exists(self, appointment_reference: str) -> bool:
        """
        Checks if an appointment with the given reference exists.

        Args:
            appointment_reference (str): Unique appointment reference.

        ### Returns:
            bool: True if the appointment exists, False otherwise.

        Raises:
            EhrApiError: If the API call fails unexpectedly.

        Example:
           ```
           exists = await service.exists("APT-001234")
           print("Exists:", exists)
           ```

        ### Example Explanation:
            If the appointment exists, the API returns a message like "Appointment Found !!!".
            This method interprets that message to return True.
        """

        if not appointment_reference:
            return False
        try:
            response = await self.get(
                AppointmentEndpoints.APPOINTMENT_EXISTS.format(
                    reference=appointment_reference
                ),
                AppointmentResponse,
            )
            if response.message == "Appointment Found !!!":
                return True
            else:
                return False
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while checking appointment existence: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                "An unexcepted error occurred while checking appointment existence.",
                500,
            ) from e

    async def delete(self, appointment_reference: str) -> None:
        """
        Deletes an appointment by its unique reference.

        This operation is irreversible and removes the appointment entirely.

        Args:
            appointment_reference (str): Unique identifier of the appointment to delete.

        Raises:
            EhrApiError: If deletion fails due to invalid ID or server error.

        Example:
            ```
            await service.delete("APT-001234")
            Deletion completed successfully.
            ```
        """

        if not appointment_reference:
            raise EhrApiError("Appointment Reference cannot be null or empty.", 400)
        try:
            await super().delete(
                AppointmentEndpoints.DELETE_APPOINTMENT.format(
                    reference=appointment_reference
                ),
            )
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while deleting Appointment: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while deleting Appointment: {e}", 500
            ) from e

    async def update(self, request_body: UpdateAppointmentDTO) -> AppointmentResponse:
        """
        Updates an existing appointment's details.

        Only the fields present in the request body are updated.

        Args:
            request_body (UpdateAppointmentDTO): Fields to update.

        ### Returns:
            AppointmentResponse: Updated appointment data and status.

        Raises:
            EhrApiError: If update fails due to validation or server errors.

        Example:
            ```
            update_data = UpdateAppointmentDTO(slot="Slot15", priority=AppointmentPriority.ROUTINE)
            response = await service.update(update_data)
            print(response.message)
            ```

        ### Response:
            Sample Output:
            {
                "type": "success",
                "message": "Appointment updated successfully.",
                "requestResource": {
                    "reference": "APT-001234",
                    "practitionerReference": "Pract123",
                    "patientReference": "Pat456",
                    "slot": "Slot15",
                    "priority": "ROUTINE",
                    "start": "2025-08-10T14:30:00Z",
                    "end": "2025-08-10T15:00:00Z",
                    "organizationId": "Org789"
                },
                "totalNumberOfRecords": 1,
                "nextPageLink": None
            }
        """

        try:
            response = await self.put(
                AppointmentEndpoints.UPDATE_APPOINTMENT,
                request_body.model_dump(by_alias=True, exclude_none=True),
                response_model=AppointmentResponse,
            )
            return response
        except EhrApiError as e:
            self.logger.error("Error updating appointment: %s", e, exc_info=True)
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while updating appointment: %s",
                e,
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while updating appointment.", 500
            ) from e
