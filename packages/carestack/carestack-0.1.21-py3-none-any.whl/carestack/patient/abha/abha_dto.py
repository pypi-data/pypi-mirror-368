from typing import Optional
from pydantic import BaseModel, Field

from carestack.common.enums import AuthMethodV2


class GenerateAadhaarOtpRequest(BaseModel):
    """
    Request payload to initiate Aadhaar-based authentication by generating an OTP.

    This is typically the first step in ABHA (Ayushman Bharat Health Account) creation
    or login workflows. The OTP will be sent to the mobile number linked with the Aadhaar.

    Attributes:
        aadhaar (str): The 12-digit Aadhaar number of the individual.
    """

    aadhaar: str


class VerifyOtpResponse(BaseModel):
    """
    Response returned after verifying the OTP sent to the user's registered mobile number.

    This response includes a transaction ID (`txnId`) which is required for subsequent
    actions such as ABHA enrollment or login.

    Attributes:
        txnId (str): Unique identifier for the authentication session.
        message (str): Server response indicating verification result.
    """

    txnId: str
    message: str


class EnrollWithAadhaar(BaseModel):
    """
    Request payload to enroll a user using Aadhaar OTP verification.

    This request is sent after the OTP has been verified. It is used to create
    an ABHA account or to authenticate the user.

    Attributes:
        otp (str): One-Time Password sent to the user’s mobile.
        txnId (str): Transaction ID obtained from OTP verification.
        mobile (str): Mobile number to be linked with the user's ABHA profile.
    """

    otp: str
    txnId: str
    mobile: str


class AbhaProfile(BaseModel):
    """
    Complete demographic and KYC profile of a user associated with their ABHA account.

     This model contains all the personal and administrative details retrieved from
     the ABHA system after successful authentication or account creation.

    Attributes:
        preferredAddress (Optional[str]): Preferred PHR (Personal Health Record) address.
        firstName (str): User's first name.
        lastName (str): User's last name.
        middleName (str): User's middle name.
        dateOfBirth (Optional[str]): Date of birth (alias: 'dob').
        gender (str): Gender of the user (e.g., M/F/O).
        profilePhoto (Optional[str]): Base64-encoded photo (alias: 'photo').
        mobile (str): Registered mobile number.
        mobileVerified (Optional[bool]): Flag indicating mobile number verification status.
        email (Optional[str]): Email address (if provided).
        phrAddress (Optional[list[str]]): List of user's PHR addresses.
        address (str): Full postal address.
        districtCode (Optional[str]): District administrative code.
        stateCode (Optional[str]): State administrative code.
        pinCode (Optional[str]): Postal code.
        abhaType (str): Type of ABHA ID (e.g., self-created, facility-created).
        stateName (str): Full name of the state.
        districtName (str): Full name of the district.
        ABHANumber (str): User’s unique ABHA number.
        abhaStatus (str): Status of the ABHA account (e.g., Active, Inactive).
        authMethods (Optional[AuthMethodV2]): Available authentication methods.
        emailVerified (Optional[bool]): Email verification status.
        kycPhoto (Optional[str]): KYC image used for verification.
        kycVerified (Optional[bool]): Whether KYC verification was successful.
        monthOfBirth (Optional[str]): User's birth month.
        name (Optional[str]): Full name of the user.
        subDistrictCode (Optional[str]): Code for the sub-district/tehsil.
        subdistrictName (Optional[str]): Name of the sub-district.
        tags (Optional[dict[str, str]]): Metadata tags or flags associated with the user.
        townCode (Optional[str]): Administrative town code.
        townName (Optional[str]): Name of the town.
        verificationStatus (Optional[str]): Status of profile verification.
        verificationType (Optional[str]): Type of verification done.
        villageCode (Optional[str]): Code for the village.
        villageName (Optional[str]): Name of the village.
        wardCode (Optional[str]): Urban ward code.
        wardName (Optional[str]): Urban ward name.
        yearOfBirth (Optional[str]): Year of birth.
    """

    preferredAddress: Optional[str] = None
    firstName: str
    lastName: str
    middleName: str
    dateOfBirth: Optional[str] = Field(None, alias="dob")
    gender: str
    profilePhoto: Optional[str] = Field(None, alias="photo")
    mobile: str
    mobileVerified: Optional[bool] = None
    email: Optional[str] = None
    phrAddress: Optional[list[str]] = None
    address: str
    districtCode: Optional[str] = None
    stateCode: Optional[str] = None
    pinCode: Optional[str] = None
    abhaType: str
    stateName: str
    districtName: str
    ABHANumber: str
    abhaStatus: str

    authMethods: Optional[AuthMethodV2] = None
    emailVerified: Optional[bool] = None
    kycPhoto: Optional[str] = None
    kycVerified: Optional[bool] = None
    monthOfBirth: Optional[str] = None
    name: Optional[str] = None
    subDistrictCode: Optional[str] = None
    subdistrictName: Optional[str] = None
    tags: Optional[dict[str, str]] = None
    townCode: Optional[str] = None
    townName: Optional[str] = None
    verificationStatus: Optional[str] = None
    verificationType: Optional[str] = None
    villageCode: Optional[str] = None
    villageName: Optional[str] = None
    wardCode: Optional[str] = None
    wardName: Optional[str] = None
    yearOfBirth: Optional[str] = None


class AbhaTokens(BaseModel):
    """
    Authentication tokens issued after successful login or enrollment.

    These tokens are essential for making authorized requests to ABHA APIs.
    The access token is short-lived, while the refresh token can be used to obtain a new access token.

    Attributes:
        token (str): Bearer token used for authentication.
        expiresIn (int): Access token's validity in seconds.
        refreshToken (str): Token to refresh the session without login.
        refreshExpiresIn (int): Validity of the refresh token in seconds.
    """

    token: str
    expiresIn: int
    refreshToken: str
    refreshExpiresIn: int


class EnrollWithAadhaarResponse(BaseModel):
    """
    Response received after a successful ABHA enrollment using Aadhaar.

    Combines the profile, authentication tokens, and other enrollment metadata.

    Attributes:
        message (str): Server message regarding the result of the enrollment.
        txnId (str): Transaction ID for the enrollment operation.
        ABHAProfile (AbhaProfile): Detailed user profile.
        tokens (AbhaTokens): Authentication tokens for future API access.
        isNew (bool): Indicates whether a new ABHA account was created.
    """

    message: str
    txnId: str
    ABHAProfile: AbhaProfile
    tokens: AbhaTokens
    isNew: bool


class AbhaAddressSuggestionsResponse(BaseModel):
    """
    Response containing suggested available ABHA addresses (PHRs) for the user.

    These addresses are generated based on the user’s details and availability.

    Attributes:
        abhaAddressList (list[str]): Suggested unique ABHA addresses.
        txnId (str): Transaction ID for this operation.
    """

    abhaAddressList: list[str]
    txnId: str


class CreateAbhaAddressRequest(BaseModel):
    """
    Request to create a new ABHA address (PHR) from one of the available suggestions.

    Attributes:
        abhaAddress (str): Desired ABHA address selected by the user.
        txnId (str): Transaction ID from the address suggestion step.
    """

    abhaAddress: str
    txnId: str


class CreateAbhaAddressResponse(BaseModel):
    """
    Response after successfully creating a new ABHA address.

    Attributes:
        txnId (str): Transaction ID for the creation.
        healthIdNumber (str): Newly created ABHA number.
        preferredAbhaAddress (str): Final chosen and active ABHA address.
    """

    txnId: str
    healthIdNumber: str
    preferredAbhaAddress: str


class UpdateMobileNumberRequest(BaseModel):
    """
    Request to initiate the mobile number update process for a user’s ABHA profile.

    The backend will send an OTP to the new number for verification.

    Attributes:
        updateValue (str): New mobile number to be registered.
        txnId (str): Transaction ID of the session for traceability.
    """

    updateValue: str = Field(..., alias="updateValue")
    txnId: str


class VerifyMobileOtpRequest(BaseModel):
    """
    Request payload to verify OTP sent to the new mobile number during mobile update.

    Attributes:
        otp (str): OTP received on the new mobile number.
        txnId (str): Transaction ID used for the update session.
    """

    otp: str
    txnId: str


class VerifyMobileOtpResponse(BaseModel):
    """
    Final response confirming the mobile number update after OTP verification.

    Attributes:
        message (str): Server status message.
        txnId (str): Transaction ID of the verification session.
        authResult (str): Result of authentication and mobile update.
    """

    message: str
    txnId: str
    authResult: str
