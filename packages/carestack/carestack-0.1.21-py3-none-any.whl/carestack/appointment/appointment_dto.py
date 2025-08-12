from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from carestack.common.enums import AppointmentPriority
from carestack.common.error_validation import check_not_empty


class AppointmentDTO(BaseModel):
    """
    Data Transfer Object for creating or updating an appointment.

    Attributes:
        practitioner_reference (str): Reference to the practitioner. Serialized as `practitionerReference`.
        patient_reference (str): Reference to the patient. Serialized as `patientReference`.
        appointment_start_time (datetime): Start time of the appointment. Serialized as `start`.
        appointment_end_time (datetime): End time of the appointment. Serialized as `end`.
        priority (Optional[AppointmentPriority]): Appointment priority (e.g., `EMERGENCY`). Serialized as `priority`.
        organization_id (Optional[str]): Organization identifier. Serialized as `organizationId`.
        slot (Optional[str]): Slot identifier. Serialized as `slot`.
        appointment_reference (Optional[str]): Unique appointment reference. Serialized as `reference`.
    """

    model_config = ConfigDict(from_attributes=True)
    practitioner_reference: str = Field(..., alias="practitionerReference")
    patient_reference: str = Field(..., alias="patientReference")
    appointment_start_time: datetime = Field(..., alias="start")
    appointment_end_time: datetime = Field(..., alias="end")
    priority: Optional[AppointmentPriority] = Field(
        AppointmentPriority.EMERGENCY, alias="priority"
    )
    organization_id: Optional[str] = Field(None, alias="organizationId")
    slot: Optional[str] = Field(None, alias="slot")
    appointment_reference: Optional[str] = Field(None, alias="reference")

    @field_validator(
        "practitioner_reference",
        "patient_reference",
        "appointment_start_time",
        "appointment_end_time",
    )
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        return check_not_empty(v, info.field_name)


class ResourceType(BaseModel):
    """
    Represents the core resource structure for an appointment.

    Attributes:
        appointment_reference (str): Unique appointment reference. Serialized as `reference`.
        practitioner_reference (str): Reference to the practitioner. Serialized as `practitionerReference`.
        patient_reference (str): Reference to the patient. Serialized as `patientReference`.
        slot (str): Slot identifier. Serialized as `slot`.
        priority (str): Appointment priority. Serialized as `priority`.
        appointment_start_time (str): Start time of the appointment. Serialized as `start`.
        appointment_end_time (str): End time of the appointment. Serialized as `end`.
        organization_id (str): Organization identifier. Serialized as `organizationId`.
    """

    model_config = ConfigDict(from_attributes=True)
    appointment_reference: str = Field(..., alias="reference")
    practitioner_reference: str = Field(..., alias="practitionerReference")
    patient_reference: str = Field(..., alias="patientReference")
    slot: str = Field(..., alias="slot")
    priority: str = Field(..., alias="priority")
    appointment_start_time: str = Field(..., alias="start")
    appointment_end_time: str = Field(..., alias="end")
    organization_id: str = Field(..., alias="organizationId")


class CreateAppointmentResponeType(BaseModel):
    """
    Represents the response after creating an appointment.

    Attributes:
        type (str): Response type/status.
        message (str): Informational message about the operation.
        validationErrors (Optional[list[Any]]): List of validation errors, if any.
        resource (ResourceType): The created appointment resource.
        fhirProfileId (Optional[str]): FHIR profile identifier (excluded from serialization).
    """

    model_config = ConfigDict(from_attributes=True)
    type: str
    message: str
    validationErrors: Optional[list[Any]] = None
    resource: ResourceType
    fhirProfileId: Optional[str] = Field(default=None, exclude=True)


class GetAppointmentResponse(BaseModel):
    """
    Represents a paginated response for appointment queries.

    Attributes:
        type (str): Response type/status.
        message (str): Informational message about the operation.
        request_resource (Optional[list[ResourceType]]): List of appointment resources. Serialized as `requestResource`.
        total_records (Optional[int]): Total number of records. Serialized as `totalNumberOfRecords`.
        next_page (Optional[str]): Link or token for the next page. Serialized as `nextPageLink`.
    """

    model_config = ConfigDict(from_attributes=True)
    type: str
    message: str
    request_resource: Optional[list[ResourceType]] = Field(
        None, alias="requestResource"
    )
    total_records: Optional[int] = Field(None, alias="totalNumberOfRecords")
    next_page: Optional[str] = Field(None, alias="nextPageLink")


class AppointmentResponse(BaseModel):
    """
    Represents the response for a single appointment query.

    Attributes:
        type (str): Response type/status.
        message (str): Informational message about the operation.
        request_resource (Optional[ResourceType]): The appointment resource. Serialized as `requestResource`.
        total_records (Optional[int]): Total number of records. Serialized as `totalNumberOfRecords`.
        next_page (Optional[str]): Link or token for the next page. Serialized as `nextPageLink`.
    """

    model_config = ConfigDict(from_attributes=True)
    type: str
    message: str
    request_resource: Optional[ResourceType] = Field(None, alias="requestResource")
    total_records: Optional[int] = Field(None, alias="totalNumberOfRecords")
    next_page: Optional[str] = Field(None, alias="nextPageLink")


class UpdateAppointmentDTO(BaseModel):
    """
    Data Transfer Object for updating an appointment.

    Attributes:
        appointment_start_time (Optional[datetime]): Updated start time. Serialized as `start`.
        appointment_end_time (Optional[datetime]): Updated end time. Serialized as `end`.
        priority (Optional[AppointmentPriority]): Updated priority.
        slot (Optional[str]): Updated slot identifier. Serialized as `slot`.
    """

    model_config = ConfigDict(from_attributes=True)
    appointment_start_time: Optional[datetime] = Field(None, alias="start")
    appointment_end_time: Optional[datetime] = Field(None, alias="end")
    priority: Optional[AppointmentPriority] = Field(None)
    slot: Optional[str] = Field(None, alias="slot")
