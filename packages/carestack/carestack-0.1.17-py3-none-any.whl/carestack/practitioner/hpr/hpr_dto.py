from typing import Optional
from pydantic import (
    BaseModel,
    RootModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
)
from pydantic_core.core_schema import FieldValidationInfo

from carestack.common.error_validation import check_not_empty


def validate_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value.strip()


class GenerateAadhaarOtpRequestSchema(BaseModel):
    """
    Request schema for generating Aadhaar OTP.

    Attributes:
        aadhaar (str): Aadhaar number.
    """

    aadhaar: str = Field(..., description="Aadhaar number")

    @field_validator("aadhaar")
    @classmethod
    def validate_aadhaar(cls, value: str) -> str:
        if not value:
            raise ValueError("Aadhaar cannot be empty")
        if not value.isdigit() or len(value) != 12:
            raise ValueError("Aadhaar must be exactly 12 digits")
        return value


class GenerateAadhaarOtpResponseSchema(BaseModel):
    """
    Response schema for generating Aadhaar OTP.

    Attributes:
        txnId (str): Transaction ID.
        mobileNumber (str): Mobile number.
    """

    txnId: str = Field(..., description="Transaction ID")
    mobileNumber: str = Field(..., description="Mobile number")


class VerifyAadhaarOtpRequestSchema(BaseModel):
    """
    Request schema for verifying Aadhaar OTP.

    Attributes:
        domainName (str): Domain name.
        idType (str): ID type.
        otp (str): OTP.
        restrictions (Optional[str]): Restrictions (optional).
        txnId (str): Transaction ID.
    """

    domainName: str = Field(..., description="Domain name")
    idType: str = Field(..., description="ID type")
    otp: str = Field(..., description="OTP")
    restrictions: Optional[str] = Field(None, description="Restrictions (optional)")
    txnId: str = Field(..., description="Transaction ID")

    @field_validator("domainName", "idType", "otp", "txnId")
    @classmethod
    def validate_required_field(cls, value: str, info: ValidationInfo) -> str:
        """Reusable function to validate required fields."""
        return check_not_empty(value, info.field_name)


class VerifyAadhaarOtpResponseSchema(BaseModel):
    """
    Response schema for verifying Aadhaar OTP.

    Attributes:
        txnId (str): Transaction ID.
        mobileNumber (Optional[str]): Mobile number.
        profilePhoto (Optional[str]): Profile photo.
        gender (str): Gender.
        name (str): Name.
        email (Optional[str]): Email.
        pincode (str): Pincode.
        birthDate (Optional[str]): Birth date.
        careOf (Optional[str]): Care of.
        house (Optional[str]): House.
        street (Optional[str]): Street.
        landmark (Optional[str]): Landmark.
        locality (Optional[str]): Locality.
        villageTownCity (Optional[str]): Village/Town/City.
        subDist (Optional[str]): Sub-district.
        district (str): District.
        state (str): State.
        postOffice (Optional[str]): Post office.
        address (str): Address.
    """

    txnId: str
    mobileNumber: Optional[str] = Field(
        None, description="Mobile number", alias="mobile"
    )
    profilePhoto: Optional[str] = Field(
        None, description="Profile photo", alias="photo"
    )
    gender: str
    name: str
    email: Optional[str] = None
    pincode: str
    birthDate: Optional[str] = None
    careOf: Optional[str] = None
    house: Optional[str] = None
    street: Optional[str] = None
    landmark: Optional[str] = None
    locality: Optional[str] = None
    villageTownCity: Optional[str] = None
    subDist: Optional[str] = None
    district: str
    state: str
    postOffice: Optional[str] = None
    address: str


class CheckAccountExistRequestSchema(BaseModel):
    """
    Request schema for checking account existence.

    Attributes:
        txnId (str): Transaction ID.
        preverifiedCheck (bool): Whether to check for preverified account.
    """

    txnId: str
    preverifiedCheck: bool

    @field_validator("txnId")
    @classmethod
    def validate_required_fields(cls, value: str) -> str:
        if not value:
            raise ValueError("This field cannot be empty")
        return value


class HprAccountResponse(BaseModel):
    """
    Response schema for checking account existence when HPR ID is present.

    Attributes:
        token (str): Token.
        hprIdNumber (str): HPR ID number.
        hprId (str): HPR ID.
        categoryId (int): Category ID.
        subCategoryId (int): Sub-category ID.
        new (bool): Indicates if the account is new.
        categoryName (str): Category name.
        categorySubName (str): Category sub name.
    """

    model_config = ConfigDict(
        populate_by_name=True, use_enum_values=True, validate_by_alias=True
    )
    token: str = Field(..., description="token", alias="token")
    hprIdNumber: str = Field(..., description="hprIdNumber", alias="hprIdNumber")
    hprId: str = Field(..., description="HPR ID", alias="hprId")
    categoryId: int = Field(..., description="Category ID", alias="categoryId")
    subCategoryId: int = Field(
        ..., description="Sub-category ID", alias="subCategoryId"
    )
    new: bool = Field(..., description="new")
    categoryName: str = Field(..., description="Category name", alias="categoryName")
    categorySubName: str = Field(
        ..., description="Category sub name", alias="categorySubName"
    )


class NonHprAccountResponse(BaseModel):
    """
    Response schema for checking account existence when HPR ID is not present.

    Attributes:
        txnId (Optional[str]): Transaction ID.
        token (str): Token.
        hprIdNumber (str): HPR ID number.
        name (Optional[str]): Name.
        firstName (Optional[str]): First name.
        lastName (Optional[str]): Last name.
        middleName (Optional[str]): Middle name.
        gender (Optional[str]): Gender.
        yearOfBirth (Optional[str]): Year of birth.
        monthOfBirth (Optional[str]): Month of birth.
        dayOfBirth (Optional[str]): Day of birth.
        districtCode (Optional[str]): District code.
        stateCode (Optional[str]): State code.
        stateName (Optional[str]): State name.
        districtName (Optional[str]): District name.
        address (Optional[str]): Address.
        pincode (Optional[str]): Pincode.
        profilePhoto (Optional[str]): Profile photo.
        categoryId (int): Category ID.
        subCategoryId (int): Sub-category ID.
        new (bool): Indicates if the account is new.
    """

    model_config = ConfigDict(
        populate_by_name=True, use_enum_values=True, validate_by_alias=True
    )
    txnId: Optional[str] = Field(None, description="Transaction ID")
    token: str = Field(..., description="token", alias="token")
    hprIdNumber: str = Field(..., description="hprIdNumber", alias="hprIdNumber")
    name: Optional[str] = Field(None, description="Name", alias="name")
    firstName: Optional[str] = Field(None, description="First name", alias="firstName")
    lastName: Optional[str] = Field(None, description="last name", alias="lastName")
    middleName: Optional[str] = Field(
        None, description="Middle name", alias="middleName"
    )
    gender: Optional[str] = Field(None, description="Gender")
    yearOfBirth: Optional[str] = Field(
        None, description="year of birth", alias="yearOfBirth"
    )
    monthOfBirth: Optional[str] = Field(
        None, description="month of birth", alias="monthOfBirth"
    )
    dayOfBirth: Optional[str] = Field(
        None, description="Day of birth", alias="dayOfBirth"
    )
    districtCode: Optional[str] = Field(
        None, description="Disrict Code", alias="districtCode"
    )
    stateCode: Optional[str] = Field(None, description="state Code", alias="stateCode")
    stateName: Optional[str] = Field(None, description="State Name", alias="stateName")
    districtName: Optional[str] = Field(
        None, description="District Name", alias="districtName"
    )
    address: Optional[str] = Field(None, description="Address")
    pincode: Optional[str] = Field(None, description="Pincode")
    profilePhoto: Optional[str] = Field(
        None, description="Profile photo", alias="profilePhoto"
    )
    categoryId: int = Field(..., description="Category ID", alias="categoryId")
    subCategoryId: int = Field(
        ..., description="Sub-category ID", alias="subCategoryId"
    )
    new: bool = Field(..., description="new")


class DemographicAuthViaMobileRequestSchema(BaseModel):
    """
    Request schema for demographic authentication via mobile.

    Attributes:
        txnId (str): Transaction ID.
        mobileNumber (str): Mobile number.
    """

    txnId: str = Field(..., description="Transaction ID")
    mobileNumber: str = Field(..., description="Mobile number")

    @field_validator("txnId", "mobileNumber")
    @classmethod
    def validate_required_fields(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("This field cannot be empty")
        return value


class DemographicAuthViaMobileResponseSchema(BaseModel):
    """
    Response schema for demographic authentication via mobile.

    Attributes:
        verified (bool): Verification status.
    """

    verified: bool = Field(..., description="Verification status")


class GenerateMobileOtpRequestSchema(BaseModel):
    """
    Request schema for generating mobile OTP.

    Attributes:
        mobile (str): Mobile number.
        txnId (str): Transaction ID.
    """

    mobile: str = Field(..., description="Mobile number")
    txnId: str = Field(..., description="Transaction ID")

    @field_validator("mobile", "txnId")
    @classmethod
    def validate_required_fields(cls, value: str, info: FieldValidationInfo) -> str:
        """Ensure the field is not empty."""
        return check_not_empty(value, info.field_name)


class MobileOtpResponseSchema(BaseModel):
    """
    Response schema for generating mobile OTP.

    Attributes:
        txnId (str): Transaction ID.
        mobileNumber (Optional[str]): Mobile number (always null).
    """

    txnId: str = Field(..., description="Transaction ID")
    mobileNumber: Optional[str] = Field(None, description="Mobile number (always null)")


class VerifyMobileOtpRequestSchema(BaseModel):
    """
    Request schema for verifying mobile OTP.

    Attributes:
        otp (str): OTP.
        txnId (str): Transaction ID.
    """

    otp: str = Field(..., description="OTP")
    txnId: str = Field(..., description="Transaction ID")

    @field_validator("otp", "txnId")
    @classmethod
    def validate_required_fields(cls, value: str, info: FieldValidationInfo) -> str:
        return check_not_empty(value, info.field_name)


class HpIdSuggestionRequestSchema(BaseModel):
    """
    Request schema for HP ID suggestion.

    Attributes:
        txnId (str): Transaction ID.
    """

    txnId: str = Field(..., description="Transaction ID")

    @field_validator("txnId")
    @classmethod
    def validate_txnId(cls, value: str) -> str:
        if not value:
            raise ValueError("txnId cannot be empty")
        return value


class HprIdSuggestionResponse(RootModel[list[str]]):
    """
    Response schema for HPR ID suggestions, which is a list of strings.
    """


class CreateHprIdWithPreVerifiedRequestBody(BaseModel):
    """
    Request body schema for creating HPR ID with pre-verified data.

    Attributes:
        address (str): Address.
        dayOfBirth (str): Day of birth.
        districtCode (str): District code.
        email (str): Email.
        firstName (str): First name.
        hpCategoryCode (str): HP category code.
        hpSubCategoryCode (str): HP subcategory code.
        hprId (str): HPR ID.
        lastName (str): Last name.
        middleName (Optional[str]): Middle name (optional).
        monthOfBirth (str): Month of birth.
        password (str): Password.
        pincode (str): Pincode.
        profilePhoto (Optional[str]): Profile photo (optional).
        stateCode (str): State code.
        txnId (str): Transaction ID.
        yearOfBirth (str): Year of birth.
    """

    address: str = Field(..., description="Address")
    dayOfBirth: str = Field(..., description="Day of birth")
    districtCode: str = Field(..., description="District code")
    email: str = Field(..., description="Email")
    firstName: str = Field(..., description="First name")
    hpCategoryCode: str = Field(..., description="HP category code")
    hpSubCategoryCode: str = Field(..., description="HP subcategory code")
    hprId: str = Field(..., description="HPR ID")
    lastName: str = Field(..., description="Last name")
    middleName: Optional[str] = Field(None, description="Middle name (optional)")
    monthOfBirth: str = Field(..., description="Month of birth")
    password: str = Field(..., description="Password")
    pincode: str = Field(..., description="Pincode")
    profilePhoto: Optional[str] = Field(None, description="Profile photo (optional)")
    stateCode: str = Field(..., description="State code")
    txnId: str = Field(..., description="Transaction ID")
    yearOfBirth: str = Field(..., description="Year of birth")

    @field_validator(
        "address",
        "dayOfBirth",
        "districtCode",
        "email",
        "firstName",
        "hpCategoryCode",
        "hpSubCategoryCode",
        "hprId",
        "lastName",
        "monthOfBirth",
        "password",
        "pincode",
        "stateCode",
        "txnId",
        "yearOfBirth",
    )
    @classmethod
    def check_required_field(cls, value: str, info: FieldValidationInfo) -> str:
        return check_not_empty(value, info.field_name)

    @field_validator("dayOfBirth", "monthOfBirth", "yearOfBirth")
    @classmethod
    def check_number_string(cls, value: str, info: FieldValidationInfo) -> str:
        if not value.isdigit():
            raise ValueError(f"{info.field_name} must contain numeric characters only")

        num_value = int(value)

        if info.field_name == "dayOfBirth" and not (1 <= num_value <= 31):
            raise ValueError("dayOfBirth must be between 1 and 31")

        if info.field_name == "monthOfBirth" and not (1 <= num_value <= 12):
            raise ValueError("monthOfBirth must be between 1 and 12")

        if info.field_name == "yearOfBirth" and len(value) != 4:
            raise ValueError("yearOfBirth must be exactly 4 digits")

        return value


class CreateHprIdWithPreVerifiedResponseBody(BaseModel):
    """
    Response body schema for creating HPR ID with pre-verified data.

    Attributes:
        token (str): Token.
        hprIdNumber (str): HPR ID number.
        name (str): Name.
        gender (str): Gender.
        yearOfBirth (str): Year of birth.
        monthOfBirth (str): Month of birth.
        dayOfBirth (str): Day of birth.
        firstName (str): First name.
        hprId (str): HPR ID.
        lastName (str): Last name.
        middleName (Optional[str]): Middle name.
        stateCode (str): State code.
        districtCode (Optional[str]): District code.
        stateName (str): State name.
        districtName (Optional[str]): District name.
        email (Optional[str]): Email.
        kycPhoto (str): KYC photo.
        mobile (str): Mobile number.
        categoryId (int): Category ID.
        subCategoryId (int): Subcategory ID.
        authMethods (list[str]): Authentication methods.
        new (bool): New flag.
    """

    token: str = Field(..., description="Token")
    hprIdNumber: str = Field(..., description="HPR ID number", alias="hprIdNumber")
    name: str = Field(..., description="Name", alias="name")
    gender: str = Field(..., description="Gender", alias="gender")
    yearOfBirth: str = Field(..., description="Year of birth", alias="yearOfBirth")
    monthOfBirth: str = Field(..., description="Month of birth", alias="monthOfBirth")
    dayOfBirth: str = Field(..., description="Day of birth", alias="dayOfBirth")
    firstName: str = Field(..., description="First name", alias="firstName")
    hprId: str = Field(..., description="HPR ID", alias="hprId")
    lastName: str = Field(..., description="Last name", alias="lastName")
    middleName: Optional[str] = Field(
        None, description="Middle name", alias="middleName"
    )
    stateCode: str = Field(..., description="State code", alias="stateCode")
    districtCode: Optional[str] = Field(
        None, description="District code", alias="districtCode"
    )
    stateName: str = Field(..., description="State name", alias="stateName")
    districtName: Optional[str] = Field(
        None, description="District name", alias="districtName"
    )
    email: Optional[str] = Field(None, description="Email", alias="email")
    kycPhoto: str = Field(..., description="KYC photo", alias="kycPhoto")
    mobile: str = Field(..., description="Mobile number", alias="mobile")
    categoryId: int = Field(..., description="Category ID", alias="categoryId")
    subCategoryId: int = Field(..., description="Subcategory ID", alias="subCategoryId")
    authMethods: list[str] = Field(
        ..., description="Authentication methods", alias="authMethods"
    )
    new: bool = Field(..., description="New flag", alias="new")
