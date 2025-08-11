import re
from datetime import datetime
from typing import Any, ClassVar, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from carestack.common.enums import (
    Departments,
    Gender,
    ResourceType,
    StatesAndUnionTerritories,
)

VALIDATION_MSGS = {
    "registration_id": "registrationId cannot be empty.",
    "first_name": "Must be at least 3 characters long and contain only letters and dots.",
    "last_name": "Must be at least 3 characters long and contain only letters and dots.",
    "mobile_number": "Invalid format. Expected +91 followed by 10 digits.",
    "emailId": "Invalid email format.",
    "address": "Must be at least 5 characters long.",
    "pincode": "Invalid format. Expected 6 digits.",
    "idType": "Invalid idType.",
    "patient_type": "Invalid patientType.",
    "department": "Invalid department.",
    "gender": "Invalid gender.",
    "state": "Invalid state.",
    "resource_type": "Invalid resourceType.",
    "birth_date": "Invalid format. Expected YYYY-MM-DD.",
    "organization": "Must be a string.",
    "count": "Must be a string.",
    "identifier": "Must be a string.",
    "designation": "designation cannot be empty.",
    "status": "status cannot be empty.",
    "joining_date": "joiningDate cannot be empty.",
    "staff_type": "staffType cannot be empty.",
}

PractitionerEntry = TypeVar("PractitionerEntry")


class Link(BaseModel):
    """
    Represents a pagination link in a response, typically used for handling
    the next page in paginated data.

    Attributes:
        next_page (str, optional): The URL or link to the next page in a paginated list.

    Configuration:
        model_config: Configuration settings to enable population by name and
        use enum values for the model fields.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    next_page: Optional[str] = Field(
        None,
        alias="nextPage",
        description="The URL or link to the next page in a paginated list.",
    )


class PractitionerFilterResponse(BaseModel, Generic[PractitionerEntry]):
    """
    Represents the response containing a list of practitioners, along with pagination
    information and the total count.

    Attributes:
        entry (list[PractitionerEntry]): A list of practitioner entries in the response.
        link (Link, optional): A link object that contains the URL for the next page in
                               the paginated list, if available.
        total (int, optional): The total number of practitioners available in the dataset.

    Configuration:
        model_config: Configuration settings to enable population by name and use
                      enum values for the model fields.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    entry: list[PractitionerEntry] = Field(
        ..., description="A list of practitioner entries in the response."
    )
    link: Optional[Link] = Field(
        None,
        description="A link object for the next page in the paginated list, if available.",
    )
    total: Optional[int] = Field(
        None, description="The total number of practitioners available in the dataset."
    )


class GetPractitionerResponse(BaseModel):
    """
    DTO for representing the response when getting one or more practitioners.

    Attributes:
        type (Optional[str]): The type of response.
        message (Optional[str]): A message describing the response.
        request_resource (Optional[Any]): The original request resource.
        total_number_of_records (Optional[int]): Total number of records.
        next_page_link (Optional[str]): Link to the next page of results.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    type: Optional[str] = Field(None, description="The type of response.")
    message: Optional[str] = Field(
        None, description="A message describing the response."
    )
    request_resource: Optional[Any] = Field(
        None, alias="requestResource", description="The original request resource."
    )
    total_number_of_records: Optional[int] = Field(
        None, alias="totalNumberOfRecords", description="Total number of records."
    )
    next_page_link: Optional[str] = Field(
        None, alias="nextPageLink", description="Link to the next page of results."
    )


class CreateUpdatePractitionerResponse(BaseModel):
    """
    DTO for representing the response after creating or updating a practitioner.

    Attributes:
        type (Optional[str]): The type of response.
        message (Optional[str]): A message describing the response.
        resource_id (Optional[str]): The resource ID of the practitioner.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    type: Optional[str] = Field(None, description="The type of response.")
    message: Optional[str] = Field(
        None, description="A message describing the response."
    )
    resource_id: Optional[str] = Field(
        None, alias="resourceId", description="The resource ID of the practitioner."
    )


class PractitionerBaseDTO(BaseModel):
    """
    Base DTO for practitioner data with common validations.

    This class is used as a base for both create and update practitioner DTOs,
    providing field definitions and validation logic for practitioner data.

    Attributes:
        registration_id (str): Unique registration ID for the practitioner.
        department (str): Department to which the practitioner belongs.
        designation (str): Designation of the practitioner.
        status (str): Current status of the practitioner (e.g., Active, Inactive).
        joining_date (str): Date of joining (YYYY-MM-DD).
        staff_type (str): Type of staff (e.g., Doctor, Nurse).
        first_name (str): First name of the practitioner.
        middle_name (Optional[str]): Middle name of the practitioner.
        last_name (Optional[str]): Last name of the practitioner.
        birth_date (Optional[str]): Date of birth (YYYY-MM-DD).
        gender (str): Gender of the practitioner.
        mobile_number (Optional[str]): Mobile number (+91 followed by 10 digits).
        email_id (Optional[str]): Email address.
        address (str): Address of the practitioner.
        pincode (Optional[str]): Pincode (6 digits).
        state (Optional[str]): State (must match StatesAndUnionTerritories).
        wants_to_link_whatsapp (Optional[bool]): Whether to link WhatsApp.
        photo (Optional[str]): Photo.
        resource_type (str): Resource type (must match ResourceType).
        resource_id (Optional[str]): Resource ID.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    registration_id: str = Field(
        ...,
        alias="registrationId",
        description="Unique registration ID for the practitioner.",
    )
    department: str = Field(
        ..., description="Department to which the practitioner belongs."
    )
    designation: str = Field(..., description="Designation of the practitioner.")
    status: str = Field(
        ..., description="Current status of the practitioner (e.g., Active, Inactive)."
    )
    joining_date: str = Field(
        ..., alias="joiningDate", description="Date of joining (YYYY-MM-DD)."
    )
    staff_type: str = Field(
        ..., alias="staffType", description="Type of staff (e.g., Doctor, Nurse)."
    )
    first_name: str = Field(
        ..., alias="firstName", description="First name of the practitioner."
    )
    middle_name: Optional[str] = Field(
        None, alias="middleName", description="Middle name of the practitioner."
    )
    last_name: Optional[str] = Field(
        None, alias="lastName", description="Last name of the practitioner."
    )
    birth_date: Optional[str] = Field(
        None, alias="birthDate", description="Date of birth (YYYY-MM-DD)."
    )
    gender: str = Field(..., description="Gender of the practitioner.")
    mobile_number: Optional[str] = Field(
        None,
        alias="mobileNumber",
        description="Mobile number (+91 followed by 10 digits).",
    )
    email_id: Optional[str] = Field(None, alias="emailId", description="Email address.")
    address: str = Field(..., description="Address of the practitioner.")
    pincode: Optional[str] = Field(None, description="Pincode (6 digits).")
    state: Optional[str] = Field(
        None, description="State (must match StatesAndUnionTerritories)."
    )
    wants_to_link_whatsapp: Optional[bool] = Field(
        None, alias="wantsToLinkWhatsapp", description="Whether to link WhatsApp."
    )
    photo: Optional[str] = Field(None, description="Photo.")
    resource_type: str = Field(
        ...,
        alias="resourceType",
        description="Resource type (must match ResourceType).",
    )
    resource_id: Optional[str] = Field(
        None, alias="resourceId", description="Resource ID."
    )

    _department_values: ClassVar[set[str]] = {e.value for e in Departments}
    _gender_values: ClassVar[set[str]] = {e.value.lower() for e in Gender}
    _state_values: ClassVar[set[str]] = {e.value for e in StatesAndUnionTerritories}
    _resource_type_values: ClassVar[set[str]] = {e.value for e in ResourceType}

    @field_validator("registration_id")
    @classmethod
    def validate_registration_id(cls, value: str) -> str:
        if not value:
            raise ValueError(VALIDATION_MSGS["registration_id"])
        return value

    @field_validator("department")
    @classmethod
    def validate_department(cls, value: str) -> str:
        if value not in cls._department_values:
            raise ValueError(VALIDATION_MSGS["department"])
        return value

    @field_validator("designation")
    @classmethod
    def validate_designation(cls, value: str) -> str:
        if not value:
            raise ValueError(VALIDATION_MSGS["designation"])
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if not value:
            raise ValueError(VALIDATION_MSGS["status"])
        return value

    @field_validator("joining_date")
    @classmethod
    def validate_joining_date(cls, value: str) -> str:
        if not value:
            raise ValueError(VALIDATION_MSGS["joining_date"])
        return value

    @field_validator("staff_type")
    @classmethod
    def validate_staff_type(cls, value: str) -> str:
        if not value:
            raise ValueError(VALIDATION_MSGS["staff_type"])
        return value

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str) -> str:
        if not re.fullmatch(r"^[a-zA-Z.]+$", value):
            raise ValueError(VALIDATION_MSGS["first_name"])
        return value

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: Optional[str]) -> Optional[str]:
        if value and not re.fullmatch(r"^[a-zA-Z.]+$", value):
            raise ValueError(VALIDATION_MSGS["last_name"])
        return value

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: Optional[str]) -> Optional[str]:
        if value and not re.fullmatch(r"^\d{6}$", value):
            raise ValueError(VALIDATION_MSGS["pincode"])
        return value

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not re.fullmatch(r"^\+91\d{10}$", value):
            raise ValueError(VALIDATION_MSGS["mobile_number"])
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birthdate(cls, value: str) -> str:
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError(VALIDATION_MSGS["birth_date"]) from exc
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        if value.lower() not in cls._gender_values:
            raise ValueError(VALIDATION_MSGS["gender"])
        return value

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        if not value:
            raise ValueError(VALIDATION_MSGS["address"])
        return value

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: Optional[str]) -> Optional[str]:
        if value and value not in cls._state_values:
            raise ValueError(VALIDATION_MSGS["state"])
        return value

    @field_validator("resource_type")
    @classmethod
    def validate_resource_type(cls, value: str) -> str:
        if value not in cls._resource_type_values:
            raise ValueError(VALIDATION_MSGS["resource_type"])
        return value


class CreatePractitionerDTO(PractitionerBaseDTO):
    """
    DTO for creating a new practitioner.

    Inherits all fields and validations from PractitionerBaseDTO.
    """


class UpdatePractitionerDTO(PractitionerBaseDTO):
    """
    DTO for updating an existing practitioner.

    Inherits all fields and validations from PractitionerBaseDTO.
    """


class PractitionerFiltersDTO(BaseModel):
    """
    Data Transfer Object (DTO) for filtering Practitioner records.

    Attributes:
        first_name (Optional[str]): The practitioner's first name.
        last_name (Optional[str]): The practitioner's last name.
        birth_date (Optional[str]): The practitioner's birth date.
        gender (Optional[str]): The practitioner's gender.
        mobile_number (Optional[str]): The practitioner's mobile number.
        email_id (Optional[str]): The practitioner's email ID.
        count (Optional[int]): The number of records to fetch.
        state (Optional[str]): The practitioner's state.

    Configuration:
        model_config: Configuration settings to enable population by name and use enum values.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    first_name: Optional[str] = Field(
        None, alias="firstName", description="The practitioner's first name."
    )
    last_name: Optional[str] = Field(
        None, alias="lastName", description="The practitioner's last name."
    )
    birth_date: Optional[str] = Field(
        None, alias="birthDate", description="The practitioner's birth date."
    )
    gender: Optional[str] = Field(None, description="The practitioner's gender.")
    mobile_number: Optional[str] = Field(
        None, alias="mobileNumber", description="The practitioner's mobile number."
    )
    email_id: Optional[str] = Field(
        None, alias="emailId", description="The practitioner's email ID."
    )
    count: Optional[int] = Field(None, description="The number of records to fetch.")
    state: Optional[str] = Field(None, description="The practitioner's state.")
