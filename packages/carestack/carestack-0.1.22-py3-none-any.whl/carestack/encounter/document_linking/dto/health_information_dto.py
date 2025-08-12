from typing import Optional, Any
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from carestack.common.enums import HealthInformationTypes
from carestack.common.error_validation import check_not_empty


class HealthInformationDTO(BaseModel):
    """
    Data Transfer Object (DTO) representing health information data for document linking.

    Attributes:
        raw_fhir (Optional[bool]): Indicates if the FHIR document is in raw format.
        fhir_document (dict[str, Any]): The FHIR document data.
        information_type (HealthInformationTypes): The type of health information (e.g., OPConsultation, DischargeSummary).

    Validation:
        - If `raw_fhir` is True, `fhir_document` must be provided.
        - `information_type` must not be empty.
    """

    raw_fhir: bool = Field(..., alias="rawFhir")
    fhir_document: dict[str, Any] = Field(None, alias="fhirDocument")
    information_type: HealthInformationTypes = Field(..., alias="informationType")

    @field_validator("fhir_document")
    @classmethod
    def _fhir_document_validate_if_raw_fhir(
        cls, v: Optional[dict], info: ValidationInfo
    ) -> Optional[dict]:
        if info.data.get("raw_fhir") and v is None:
            raise ValueError("fhirDocument must be provided when rawFhir is True")
        return v

    @field_validator("information_type")
    @classmethod
    def _information_type_not_empty(
        cls,
        v: HealthInformationTypes,
        info: ValidationInfo,
    ) -> HealthInformationTypes:
        return check_not_empty(v, info.field_name)
