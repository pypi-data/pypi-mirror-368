from typing import Optional

from pydantic import BaseModel, Field

from carestack.encounter.document_linking.dto.health_information_dto import (
    HealthInformationDTO,
)


class UpdateVisitRecordsDTO(BaseModel):
    """
    Data Transfer Object (DTO) for updating visit records.

    Attributes:
        care_context_reference (str): Unique reference for the care context.
        patient_reference (str): Unique reference for the patient.
        practitioner_reference (str): Unique reference for the practitioner.
        appointment_reference (str): Unique reference for the appointment.
        patient_abha_address (Optional[str]): Patient's ABHA address, if available.
        health_records (list[HealthInformationDTO]): List of health records to be updated.
        mobile_number (Optional[str]): Patient's mobile number.
        request_id (Optional[str]): Unique request identifier for the update operation.

    Validation:
        - All required fields should not be empty.
        - health_records list must not be empty.
        - If provided, mobile_number must not contain '*' characters.
    """

    care_context_reference: str = Field(..., alias="careContextReference")
    patient_reference: str = Field(..., alias="patientReference")
    practitioner_reference: str = Field(..., alias="practitionerReference")
    appointment_reference: str = Field(..., alias="appointmentReference")
    patient_abha_address: Optional[str] = Field(None, alias="patientAbhaAddress")
    health_records: list[HealthInformationDTO] = Field(..., alias="healthRecords")
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    request_id: Optional[str] = Field(None, alias="requestId")

    # @field_validator(
    #     "care_context_reference",
    #     "appointment_reference",
    #     "patient_reference",
    #     "practitioner_reference",
    # )
    # @classmethod
    # def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("health_records")
    # @classmethod
    # def _health_records_not_empty(
    #     cls, v: list[HealthInformationDTO]
    # ) -> list[HealthInformationDTO]:
    #     """Validates that the health records list is not empty."""
    #     return check_not_empty(v, "health records list")

    # @field_validator("mobile_number")
    # @classmethod
    # def _mobile_number_format(cls, v: Optional[str]) -> Optional[str]:
    #     """
    #     Validates that the mobile number does not contain '*' characters when provided.
    #     """
    #     if v and "*" in v:
    #         raise ValueError("Mobile number cannot contain * characters")
    #     return v


class UpdateVisitRecordsResponse(BaseModel):
    """
    Response DTO for updating visit records.

    Attributes:
        success (bool): Indicates if the update operation was successful.
    """

    success: bool
