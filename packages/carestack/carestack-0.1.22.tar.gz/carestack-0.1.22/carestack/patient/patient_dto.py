import re
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from carestack.common.enums import (
    Gender,
    PatientIdTypeEnum,
    PatientTypeEnum,
    ResourceType,
    StatesAndUnionTerritories,
)

PatientEntry = TypeVar("PatientEntry")

VALIDATION_MSGS = {
    "firstName": "Must be at least 3 characters long and contain only letters and dots.",
    "lastName": "Must be at least 3 characters long and contain only letters and dots.",
    "mobileNumber": "Invalid format. Expected +91 followed by 10 digits.",
    "emailId": "Invalid email format.",
    "address": "Must be at least 5 characters long.",
    "pincode": "Invalid format. Expected 6 digits.",
    "idType": "Invalid idType.",
    "patientType": "Invalid patientType.",
    "gender": "Invalid gender.",
    "state": "Invalid state.",
    "resourceType": "Invalid resourceType.",
    "birthDate": "Invalid format. Expected YYYY-MM-DD.",
    "organization": "Must be a string.",
    "count": "Must be a string.",
    "identifier": "Must be a string.",
}


class GetPatientResponse(BaseModel):
    """
    DTO for representing the response when getting one or more patients.

    Attributes:
        type (Optional[str]): The type of response.
        message (Optional[str]): A message describing the response.
        request_resource (Optional[Any]): The original request resource.
        total_number_of_records (Optional[int]): Total number of records.
        next_page_link (Optional[str]): Link to the next page of results.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    type: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)
    request_resource: Optional[Any] = Field(None, alias="requestResource")
    total_number_of_records: Optional[int] = Field(None, alias="totalNumberOfRecords")
    next_page_link: Optional[str] = Field(None, alias="nextPageLink")


class Link(BaseModel):
    """
    Represents a pagination link in API responses.

    Attributes:
        next_page (Optional[str]): The link to the next page.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    next_page: Optional[str] = Field(None, alias="nextPage")


class PatientFilterResponse(BaseModel, Generic[PatientEntry]):
    """
    A generic response model for filtering patient entries.

    This class is designed to handle API responses that return a list
    of patient-related data along with pagination links and total count.

    Attributes:
        entry (list[T]): A list of patient entries.
        link (Optional[Link]): Pagination link information (if available).
        total (Optional[int]): Total number of patients (if provided).
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    entry: list[PatientEntry]
    link: Optional[Link] = None
    total: Optional[int] = None


class CreateUpdatePatientResponse(BaseModel):
    """
    DTO for representing the response after creating or updating a patient.

    Attributes:
        type (Optional[str]): The type of response.
        message (Optional[str]): A message describing the response.
        resource_id (Optional[str]): The resource ID of the patient.
        validation_errors (Optional[list[Any]]): List of validation errors, if any.
        resource (Optional[dict[str, Any]]): The patient resource data.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    type: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)
    resource_id: Optional[str] = Field(None, alias="resourceId")
    validation_errors: Optional[list[Any]] = Field(None, alias="validationErrors")
    resource: Optional[dict[str, Any]] = None


class PatientDTO(BaseModel):
    """
    DTO for creating a new patient.

    Attributes:
        id_number (str): Patient's ID number.
        id_type (str): Type of ID (must match PatientIdTypeEnum).
        abha_address (Optional[str]): ABHA address.
        patient_type (str): Patient type (must match PatientTypeEnum).
        first_name (str): First name (min 3 chars, only letters and dots).
        middle_name (Optional[str]): Middle name.
        last_name (Optional[str]): Last name (min 3 chars, only letters and dots).
        birth_date (str): Birth date (YYYY-MM-DD).
        gender (str): Gender (must match Gender enum).
        mobile_number (Optional[str]): Mobile number (+91 followed by 10 digits).
        email_id (Optional[str]): Email address.
        address (str): Address (min 5 chars).
        pincode (Optional[str]): Pincode (6 digits).
        state (Optional[str]): State (must match StatesAndUnionTerritories).
        wants_to_link_whatsapp (Optional[bool]): Whether to link WhatsApp.
        photo (Optional[str]): Photo.
        resource_type (str): Resource type (must be 'PATIENT').
        resource_id (Optional[str]): Resource ID.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    id_number: str = Field(..., alias="idNumber")
    id_type: str = Field(..., alias="idType")
    abha_address: Optional[str] = Field(None, alias="abhaAddress")
    patient_type: str = Field(..., alias="patientType")
    first_name: str = Field(..., alias="firstName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    last_name: Optional[str] = Field(None, alias="lastName")
    birth_date: str = Field(..., alias="birthDate")
    gender: str
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    email_id: Optional[str] = Field(None, alias="emailId")
    address: str
    pincode: Optional[str] = None
    state: Optional[str] = None
    wants_to_link_whatsapp: Optional[bool] = Field(None, alias="wantsToLinkWhatsapp")
    photo: Optional[str] = None
    resource_type: str = Field(..., alias="resourceType")
    resource_id: Optional[str] = Field(None, alias="resourceId")

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str) -> str:
        if len(value) < 3:
            raise ValueError(VALIDATION_MSGS["firstName"])
        if not re.fullmatch(r"^[a-zA-Z.]+$", value):
            raise ValueError(VALIDATION_MSGS["firstName"])
        return value

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: str) -> str:
        if value and len(value) < 3:
            raise ValueError(VALIDATION_MSGS["lastName"])
        if value and not re.fullmatch(r"^[a-zA-Z.]+$", value):
            raise ValueError(VALIDATION_MSGS["lastName"])
        return value

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str) -> str:
        if value and not re.fullmatch(r"^\+91\d{10}$", value):
            raise ValueError(VALIDATION_MSGS["mobileNumber"])
        return value

    @field_validator("email_id")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if value and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError(VALIDATION_MSGS["emailId"])
        return value

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        if len(value) < 5:
            raise ValueError(VALIDATION_MSGS["address"])
        return value

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: str) -> str:
        if value and not re.fullmatch(r"^\d{6}$", value):
            raise ValueError(VALIDATION_MSGS["pincode"])
        return value

    @field_validator("id_type")
    @classmethod
    def validate_id_type(cls, value: str) -> str:
        if value is not None and value.upper() not in [
            e.value for e in PatientIdTypeEnum
        ]:
            raise ValueError(VALIDATION_MSGS["idType"])
        return value

    @field_validator("patient_type")
    @classmethod
    def validate_patient_type(cls, value: str) -> str:
        if value is not None and value.upper() not in [
            e.value for e in PatientTypeEnum
        ]:
            raise ValueError(VALIDATION_MSGS["patientType"])
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        if value is not None and value.lower() not in [e.value for e in Gender]:
            raise ValueError(VALIDATION_MSGS["gender"])
        return value

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str) -> str:
        if value is not None and value not in [
            e.value for e in StatesAndUnionTerritories
        ]:
            raise ValueError(VALIDATION_MSGS["state"])
        return value

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type(cls, value: str) -> str:
        if value != ResourceType.PATIENT.value:
            raise ValueError(VALIDATION_MSGS["resourceType"])
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birthdate(cls, value: str) -> str:
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(VALIDATION_MSGS["birthDate"]) from exc
        return value


class UpdatePatientDTO(BaseModel):
    """
    DTO for updating an existing patient with specific fields and validations.

    Attributes:
        resource_id (str): The resource ID of the patient.
        email_id (Optional[str]): Email address.
        mobile_number (Optional[str]): Mobile number.
        resource_type (str): Resource type (must be 'PATIENT').
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    resource_id: str = Field(..., alias="resourceId")
    email_id: Optional[str] = Field(None, alias="emailId")
    mobile_number: Optional[str] = Field(None, alias="mobileNumber")
    resource_type: str = Field(..., alias="resourceType")

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str) -> str:
        if value and not re.fullmatch(r"^\+91\d{10}$", value):
            raise ValueError(VALIDATION_MSGS["mobileNumber"])
        return value

    @field_validator("email_id")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if value and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError(VALIDATION_MSGS["emailId"])
        return value

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type(cls, value: str) -> str:
        if value != ResourceType.PATIENT.value:
            raise ValueError(VALIDATION_MSGS["resourceType"])
        return value


class PatientFiltersDTO(BaseModel):
    """
    DTO for filtering patients.

    Attributes:
        first_name (Optional[str]): First name (min 3 chars, only letters and dots).
        last_name (Optional[str]): Last name (min 3 chars, only letters and dots).
        birth_date (Optional[str]): Birth date (YYYY-MM-DD).
        gender (Optional[str]): Gender (must match Gender enum).
        phone (Optional[str]): Phone number (+91 followed by 10 digits).
        state (Optional[str]): State (must match StatesAndUnionTerritories).
        organization (Optional[str]): Organization name.
        count (Optional[int]): Number of results to return.
        identifier (Optional[str]): Identifier string.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    birth_date: Optional[str] = Field(None, alias="birthDate")
    gender: Optional[str] = None
    phone: Optional[str] = Field(None, alias="phone")
    state: Optional[str] = None
    organization: Optional[str] = None
    count: Optional[int] = None
    identifier: Optional[str] = None

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str) -> str:
        if value and len(value) < 3:
            raise ValueError("firstName must be at least 3 characters long")
        if value and not re.fullmatch("^[a-zA-Z.]+$", value):
            raise ValueError("firstName must only contain letters and dots")
        return value

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: str) -> str:
        if value and len(value) < 3:
            raise ValueError("lastName must be at least 3 characters long")
        if value and not re.fullmatch("^[a-zA-Z.]+$", value):
            raise ValueError("lastName must only contain letters and dots")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if value and not re.fullmatch(r"^\+91\d{10}$", value):
            raise ValueError(
                "Invalid mobile number format. It should be +91 followed by 10 digits"
            )
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        if value and value not in [e.value for e in Gender]:
            raise ValueError("Invalid gender")
        return value

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str) -> str:
        if value is not None and value not in [
            e.value for e in StatesAndUnionTerritories
        ]:
            raise ValueError(f"Invalid state: {value}")
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birthdate(cls, value: str) -> str:
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(
                    "Invalid birthDate format. Expected YYYY-MM-DD"
                ) from exc
        return value


class BooleanResponse(BaseModel):
    """
    Simple boolean response model.

    Attributes:
        success (bool): Indicates if the operation was successful.
    """

    success: bool
