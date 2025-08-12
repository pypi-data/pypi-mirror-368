from datetime import datetime

from carestack.common.enums import AuthMode
from carestack.encounter.document_linking.dto.create_care_context_dto import (
    CreateCareContextDTO,
)
from carestack.encounter.document_linking.dto.health_document_linking_dto import (
    HealthDocumentLinkingDTO,
)
from carestack.encounter.document_linking.dto.link_care_context_dto import (
    LinkCareContextDTO,
)
from carestack.encounter.document_linking.dto.update_visit_records_dto import (
    UpdateVisitRecordsDTO,
)


def format_appointment_date(start_date: str, end_date: str) -> str:
    """
    Converts ISO-formatted appointment start and end datetime strings into a
    human-readable time range string in `hh:mm am/pm - hh:mm am/pm` format.

    This function handles UTC ‘Z’ suffix by converting it to a timezone-aware datetime,
    then formats the times in 12-hour AM/PM notation in lowercase letters.

    Args:
        start_date (str): ISO 8601 formatted start datetime (e.g., "2025-07-30T09:30:00Z").
        end_date (str): ISO 8601 formatted end datetime (e.g., "2025-07-30T10:30:00Z").

    Returns:
        str: Formatted time range string, e.g., "09:30 am - 10:30 am".

    Example:
        ```
        result = format_appointment_date("2025-07-30T09:30:00Z", "2025-07-30T10:45:00Z")
        print(result)
        ```
    ### Response:
        Sample output for the given example:
        "09:30 am - 10:45 am"
    """
    start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

    def format_time(date):
        return date.strftime("%I:%M %p").lower()

    return f"{format_time(start)} - {format_time(end)}"


def map_to_create_care_context_dto(
    data: HealthDocumentLinkingDTO,
) -> CreateCareContextDTO:
    """
    Transforms a HealthDocumentLinkingDTO instance into a CreateCareContextDTO instance,
    preparing the data for care context creation API calls.

    The function derives a human-readable appointment date string by formatting the
    original start and end datetime fields, and maps corresponding fields between the DTOs.
    It sets `resendOtp` to `False` by default, assuming a new request.

    Args:
        data (HealthDocumentLinkingDTO): Source DTO containing raw health linking data including patient,
                                        practitioner info, appointment times, and more.

    Returns:
        CreateCareContextDTO: The resulting DTO with mapped and formatted fields, ready for API submission.

    Example:
        ```
        linking_dto = HealthDocumentLinkingDTO(
            patientReference="patient-uuid-123",
            practitionerReference="practitioner-uuid-456",
            patientAddress="123 Elm Street",
            patientName="John Doe",
            appointmentStartDate="2025-08-01T09:00:00Z",
            appointmentEndDate="2025-08-01T09:30:00Z",
            appointmentPriority="ROUTINE",
            organizationId="Org001",
            mobileNumber="9876543210",
            hiType="OPConsultation",
            healthRecords=[rawFhir=True, fhirDocument={"key": "value"}, informationType=HealthInformationTypes.OPConsultation],
            appointmentSlot="slot-001",
            reference="appt-123",
            patientAbhaAddress="john@abdm"
        )
        care_context_dto = map_to_create_care_context_dto(linking_dto)
        print(care_context_dto.appointmentDate)  # Output: "09:00 am - 09:30 am"
        ```

    ### Response:
        A CreateCareContextDTO instance with the following fields:
        - patientReference: "patient-uuid-123"
        - patientAbhaAddress: "123 Elm Street"
        - practitionerReference: "practitioner-uuid-456"
        - appointmentReference: "appt-123"
        - hiType: "OPConsultation"
        - appointmentDate: "09:00 am - 09:30 am"
        - resendOtp: False
        - authMode: "DEMOGRAPHICS"
    """
    appointment_date = format_appointment_date(
        data.appointment_start_date, data.appointment_end_date
    )
    return CreateCareContextDTO(
        patientReference=data.patient_reference,
        patientAbhaAddress=data.patient_abha_address,
        practitionerReference=data.practitioner_reference,
        appointmentReference=data.reference,
        hiType=data.hi_type,
        appointmentDate=appointment_date,
        resendOtp=False,
    )


def map_to_consultation_dto(
    data: HealthDocumentLinkingDTO,
    care_context_reference: str,
    request_id: str,
) -> UpdateVisitRecordsDTO:
    """
    Converts HealthDocumentLinkingDTO and associated care context identifiers into an
    UpdateVisitRecordsDTO for updating patient consultation and visit records.

    This mapping associates the care context reference and request ID with the health document details,
    carrying forward health records and patient identification information.

    Args:
        data (HealthDocumentLinkingDTO): Source health document linking DTO.
        care_context_reference (str): The unique care context identifier received from care context creation.
        request_id (str): The request ID corresponding to the transaction.

    Returns:
        UpdateVisitRecordsDTO: Mapped DTO ready to be used in visit records update API calls.

    Example:
        ```
        consultation_dto = map_to_consultation_dto(linking_dto, "care-context-123", "req-456")
        print(consultation_dto.careContextReference)  # Output: "care-context-123"
        ```
    ### Response:
        An UpdateVisitRecordsDTO instance with the following fields:
        - careContextReference: "care-context-123"
        - patientReference: "patient-uuid-123"
        - practitionerReference: "practitioner-uuid-456"
        - appointmentReference: "appt-123"
        - patientAbhaAddress: "123 Elm Street"
        - healthRecords: [rawFhir=True, fhirDocument={"key": "value"}, informationType=HealthInformationTypes.OPConsultation]
        - mobileNumber: "9876543210"
        - requestId: "req-456"
        - appointmentDate: "hh:mm am/pm - hh:mm am/pm"
        - authMode: "DEMOGRAPHICS"
        - appointmentType: "Emergency"
        - appointmentStatus: "scheduled"
    """
    return UpdateVisitRecordsDTO(
        careContextReference=care_context_reference,
        patientReference=data.patient_reference,
        practitionerReference=data.practitioner_reference,
        appointmentReference=data.reference,
        patientAbhaAddress=data.patient_abha_address,
        healthRecords=data.health_records or [],
        mobileNumber=data.mobile_number,
        requestId=request_id,
    )


def map_to_link_care_context_dto(
    data: HealthDocumentLinkingDTO,
    care_context_reference: str,
    request_id: str,
) -> LinkCareContextDTO:
    """
    Maps HealthDocumentLinkingDTO along with care context and request identifiers
    into a LinkCareContextDTO for linking care contexts to existing health documents.

    Sets the authorization mode to `AuthMode.DEMOGRAPHICS` by default,
    indicating linkage is based on demographic authentication.

    Args:
        data (HealthDocumentLinkingDTO): Source health document linking DTO.
        care_context_reference (str): The care context reference to link.
        request_id (str): The unique transaction/request ID.

    Returns:
        LinkCareContextDTO: The mapped DTO ready for care context linking API calls.

    Example:
        ```
        link_care_context_dto = map_to_link_care_context_dto(linking_dto, "care-context-123", "req-456")
        print(link_care_context_dto.authMode)  # Output: AuthMode.DEMOGRAPHICS
        ```
    ### Response:
        A LinkCareContextDTO instance with the following fields:
        - requestId: "req-456"
        - appointmentReference: "appt-123"
        - patientAddress: "123 Elm Street"
        - patientName: "John Doe"
        - patientReference: "patient-uuid-123"
        - careContextReference: "care-context-123"
        - authMode: "DEMOGRAPHICS"
    """
    return LinkCareContextDTO(
        requestId=request_id or "",
        appointmentReference=data.reference,
        patientAddress=data.patient_address,
        patientName=data.patient_name,
        patientReference=data.patient_reference,
        careContextReference=care_context_reference,
        authMode=AuthMode.DEMOGRAPHICS,
    )
