from datetime import datetime
from typing import Any, Optional

from pydantic import UUID4, BaseModel, Field, ValidationInfo, field_validator

from carestack.common.enums import AuthMode, HealthInformationTypes
from carestack.common.error_validation import check_not_empty


class CreateCareContextDTO(BaseModel):
    """
    Request DTO for creating a care context.

    Attributes:
        patient_reference (str): Unique reference for the patient.
        patient_abha_address (Optional[str]): Patient's ABHA address, if available.
        practitioner_reference (str): Unique reference for the practitioner.
        appointment_reference (str): Unique reference for the appointment.
        hi_type (HealthInformationTypes): Type of health information being linked.
        appointment_date (str): Date of the appointment (ISO format).
        resend_otp (bool): Whether to resend the OTP for authentication.

    Example Usage:
        ```
        dto = CreateCareContextDTO(
            patientReference="pat-123",
            practitionerReference="prac-456",
            appointmentReference="appt-789",
            hiType=HealthInformationTypes.OPConsultation,
            appointmentDate="2024-07-30",
            resendOtp=False
        )
        ```
    """

    patient_reference: str = Field(..., alias="patientReference")
    patient_abha_address: Optional[str] = Field(None, alias="patientAbhaAddress")
    practitioner_reference: str = Field(..., alias="practitionerReference")
    appointment_reference: str = Field(..., alias="appointmentReference")
    hi_type: HealthInformationTypes = Field(..., alias="hiType")
    appointment_date: str = Field(..., alias="appointmentDate")
    resend_otp: bool = Field(..., alias="resendOtp")

    # Uncomment and use these validators for stricter field validation if needed.
    # @field_validator(
    #     "appointment_reference",
    #     "appointment_date",
    #     "patient_reference",
    #     "practitioner_reference",
    # )
    # @classmethod
    # def _validate_fields(cls, v: Any, info: ValidationInfo) -> Any:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("hi_type")
    # @classmethod
    # def _hi_type_not_empty(
    #     cls, v: HealthInformationTypes, info: ValidationInfo
    # ) -> HealthInformationTypes:
    #     """Validates that the HI type is not empty."""
    #     return check_not_empty(v, info.field_name)

    # @field_validator("resend_otp")
    # @classmethod
    # def _validate_resend_otp(cls, v: bool, info: ValidationInfo) -> bool:
    #     """Validates that required fields are not empty."""
    #     return check_not_empty(v, info.field_name)


class CreateCareContextResponse(BaseModel):
    """
    Response DTO for care context creation.

    Attributes:
        care_context_reference (str): Unique reference for the created care context.
        request_id (str): Request ID for tracking the operation.
        auth_modes (list[AuthMode]): List of supported authentication modes for the care context.
    """

    care_context_reference: str = Field(..., alias="careContextReference")
    request_id: str = Field(..., alias="requestId")
    auth_modes: list[AuthMode] = Field(..., alias="authModes")
