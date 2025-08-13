import logging
from typing import Any, Type, TypeVar, Union
from pydantic import BaseModel, ValidationError
from carestack.common.enums import HPR_API_ENDPOINTS
from carestack.practitioner.hpr.hpr_dto import (
    CheckAccountExistRequestSchema,
    CreateHprIdWithPreVerifiedRequestBody,
    CreateHprIdWithPreVerifiedResponseBody,
    DemographicAuthViaMobileRequestSchema,
    DemographicAuthViaMobileResponseSchema,
    GenerateAadhaarOtpRequestSchema,
    GenerateAadhaarOtpResponseSchema,
    GenerateMobileOtpRequestSchema,
    HpIdSuggestionRequestSchema,
    HprIdSuggestionResponse,
    HprAccountResponse,
    MobileOtpResponseSchema,
    NonHprAccountResponse,
    VerifyAadhaarOtpRequestSchema,
    VerifyAadhaarOtpResponseSchema,
    VerifyMobileOtpRequestSchema,
)
from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError

T = TypeVar("T")


class HPRService(BaseService):
    """
    Service for handling HPR (Healthcare Professional Registry) registration-related operations.

    This service provides methods for interacting with the HPR registration API, including:
        - Aadhaar OTP generation and verification
        - Mobile OTP generation and verification
        - Demographic authentication via mobile
        - Checking for existing HPR accounts
        - Retrieving HPR ID suggestions
        - Creating HPR IDs with pre-verified data

    All methods handle validation, error logging, and robust exception management.

    Args:
        config (ClientConfig): Configuration object containing API credentials and settings.

    Returns:
        HPRService: An instance of the HPRService class.

    Raises:
        EhrApiError: If any API call fails or if validation errors occur.
        ValidationError: If input data does not conform to expected schemas.

    Example usage:
        ```
        config = ClientConfig(
            api_key="your_api_key"
        )
        hpr_service = HPRService(config)
        otp_response = await hpr_service.generate_aadhaar_otp({"aadhaar": "123456789012"})
        ```
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def validate_data(
        self, dto_type: Type[BaseModel], request_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validates the provided data dict against a Pydantic DTO schema.

        ### Args:
            dto_type (Type[BaseModel]): The Pydantic model class to validate against.
            request_data (dict[str, Any]): The input data dictionary.

        Returns:
            dict[str, Any]: Validated data serialized with alias names.

        Raises:
            EhrApiError: If validation fails with detailed error message.

        Example:

            await hpr_service.validate_data(GenerateAadhaarOtpRequest, {"aadhaar":"123456789012"})
            {'aadhaar': '123456789012'}
        """
        try:
            validated_data = dto_type(**request_data)
            return validated_data.model_dump(by_alias=True)
        except ValidationError as err:
            self.logger.exception("Validation failed with pydantic error.")
            raise EhrApiError(f"Validation failed: {err}", 400) from err

    async def generate_aadhaar_otp(
        self, request_data: dict[str, Any]
    ) -> GenerateAadhaarOtpResponseSchema:
        """
        Initiate Aadhaar OTP flow for user authentication.

        This method validates the Aadhaar number, sends it to the API, and returns a transaction ID to be used
        in the next step.

        Args:
            request_data (GenerateAadhaarOtpRequestSchema): Must include 'aadhaar' (12-digit string).

        Returns:
            GenerateAadhaarOtpResponseSchema: Includes:
                - txnId (str): Transaction/session ID for the OTP flow.
                - mobileNumber (str): Mobile number (masked) registered with the Aadhaar record.

        Raises:
            EhrApiError: On missing/invalid Aadhaar number or API error.

        Example:
            ```
            resp = await hpr_service.generate_aadhaar_otp({'aadhaar': '123456789012'})
            print(resp.txnId, resp.mobileNumber)
            ```
        ### Response:
            Sample Output:
            {
                "txnId": "txn_abcdef123456",
                "mobileNumber": "9871XXXX23"
            }
        """
        if not request_data.get("aadhaar"):
            raise EhrApiError("Aadhaar number is required", 400)

        validated_data = await self.validate_data(
            GenerateAadhaarOtpRequestSchema, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.GENERATE_AADHAAR_OTP,
                validated_data,
                GenerateAadhaarOtpResponseSchema,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while generating Aadhaar OTP",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while generating Aadhaar OTP"
            ) from e

    async def verify_aadhaar_otp(
        self, request_data: dict[str, Any]
    ) -> VerifyAadhaarOtpResponseSchema:
        """
        Verify the OTP received on Aadhaar-linked mobile number.

        Validates all required fields and verifies the OTP via the API.
        Returns all fetched demographic profile details.

        Args:
            request_data (VerifyAadhaarOtpRequestSchema): Must include
                - 'otp' (str), 'txnId' (str), 'domainName' (str), 'idType' (str)
                - 'restrictions' (Optional[str])

        Returns:
            VerifyAadhaarOtpResponseSchema: Includes:
                - txnId (str), gender (str), name (str), address (str), etc.

        ### Raises:
            EhrApiError: On missing/invalid OTP or API error.

        Example:
            ```
            resp = await hpr_service.verify_aadhaar_otp({
                "otp": "123456", "txnId": "txn_abcdef123456", "domainName": "ndhm.gov.in", "idType": "aadhaar"
            })
            print(resp.txnId, resp.name, resp.gender)
            ```
        ### Response:
            Sample Output:
            {
                "txnId": "txn_abcdef123456",
                "mobileNumber": "9871XXXX23",
                "gender": "M",
                "name": "John Doe",
                "address": "123 Main St, Delhi",
                ...
            }
        """
        if not request_data.get("otp"):
            raise EhrApiError("OTP is required", 400)
        validated_data = await self.validate_data(
            VerifyAadhaarOtpRequestSchema, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.VERIFY_AADHAAR_OTP,
                validated_data,
                VerifyAadhaarOtpResponseSchema,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while verifying Aadhaar OTP",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while verifying Aadhaar OTP",
                status_code=500,
            ) from e

    async def check_account_exist(
        self, request_data: dict[str, Any]
    ) -> Union[HprAccountResponse, NonHprAccountResponse]:
        """
        Checks if there is an existing HPR account for the provided transaction.

        Returns rich account info if present, or demographic info indicating non-existence.

        Args:
            request_data (CheckAccountExistRequestSchema): Must include:
                - 'txnId' (str): The OTP or auth transaction ID.
                - 'preverifiedCheck' (bool): Flag for existence of preverified account.

        Returns:
            HprAccountResponse: if account exists,
            NonHprAccountResponse: else.

        Raises:
            EhrApiError: On validation or API errors.

        Example:
            ```
            resp = await hpr_service.check_account_exist({"txnId": "txn_abcdef123456", "preverifiedCheck": True})
            if isinstance(resp, HprAccountResponse):
                print("Account exists:", resp.hprIdNumber)
            else:
                print("No existing account.")
            ```
        ### Response:
            Sample Output (existing):
            {
                "token": "auth.jwt.token",
                "hprIdNumber": "HPR123456",
                "hprId": "HPR123456",
                "categoryId": 10,
                "subCategoryId": 1,
                "new": False,
                "categoryName": "Physician",
                "categorySubName": "Allopathic"
            }

            Sample Output (non-existing):
            {
                "txnId": "txn_abcdef123456",
                "token": "auth.jwt.token",
                "hprIdNumber": "",
                "name": "John Doe",
                "gender": "M",
                "address": "New Delhi",
                ...
            }
        """
        if not request_data.get("txnId"):
            raise EhrApiError("Transaction ID is required", 400)

        validated_data = await self.validate_data(
            CheckAccountExistRequestSchema, request_data
        )

        try:
            # Get the raw response as a dictionary first by not passing a response_model
            response_data = await self.post(
                HPR_API_ENDPOINTS.CHECK_ACCOUNT_EXIST,
                validated_data,
                response_model=dict,
            )

            if not isinstance(response_data, dict):
                raise EhrApiError("Invalid response format from API", 500)

            # Check if hprIdNumber is present and not empty, then parse with the correct model
            if response_data.get("hprIdNumber"):
                return HprAccountResponse(**response_data)
            else:
                return NonHprAccountResponse(**response_data)
        except ValidationError as e:
            self.logger.error(
                "Pydantic validation failed for account existence check: %s", e
            )
            raise EhrApiError(f"Response validation failed: {e}", 400) from e
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while checking account existence",
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while checking account existence: {e}"
            ) from e

    async def demographic_auth_via_mobile(
        self, request_data: dict[str, Any]
    ) -> DemographicAuthViaMobileResponseSchema:
        """
        Authenticates user demographics using a mobile number.

        Args:
            request_data (DemographicAuthViaMobileRequestSchema): Must include:
                - 'txnId': The authentication transaction ID
                - 'mobileNumber': The mobile number to authenticate

        Returns:
            DemographicAuthViaMobileResponseSchema:
                - verified (bool): Whether the provided details matched

        Raises:
            EhrApiError: On API or validation failure

        Example:
            ```
            resp = await hpr_service.demographic_auth_via_mobile({"txnId": "txn_abc123", "mobileNumber": "9876543210"})
            print(resp.verified)
            ```
        ### Response:
            Sample Output:
            {"verified": True} if the mobile number matches the transaction ID,
            {"verified": False} if it does not match.

        """
        if not request_data.get("mobileNumber"):
            raise EhrApiError("Mobile number is required", 400)
        validated_data = await self.validate_data(
            DemographicAuthViaMobileRequestSchema, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.DEMOGRAPHIC_AUTH_MOBILE,
                validated_data,
                DemographicAuthViaMobileResponseSchema,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while verifying demographic auth via mobile",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while verifying demographic auth via mobile"
            ) from e

    async def generate_mobile_otp(
        self, request_data: dict[str, Any]
    ) -> MobileOtpResponseSchema:
        """
        Initiates OTP generation for mobile number verification/authentication.

        Args:
            request_data (GenerateMobileOtpRequestSchema): Must include:
                - 'mobile' (str): The mobile number
                - 'txnId' (str): Transaction/session ID

        Returns:
            MobileOtpResponseSchema:
                - txnId: Transaction ID
                - mobileNumber: Always null for this API

        Raises:
            EhrApiError: On input validation or API error

        Example:
            ```
            resp = await hpr_service.generate_mobile_otp({"mobile": "9876543210", "txnId": "txn_xyz123"})
            print(resp.txnId)
            ```
        ### Response:
            Sample Output:
            {
                "txnId": "txn_xyz123",
                "mobileNumber": null
            }
        """
        if not request_data.get("mobile"):
            raise EhrApiError("Mobile number is required", 400)
        validated_data = await self.validate_data(
            GenerateMobileOtpRequestSchema, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.GENERATE_MOBILE_OTP,
                validated_data,
                MobileOtpResponseSchema,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while generating mobile OTP",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while generating mobile OTP"
            ) from e

    async def verify_mobile_otp(
        self, request_data: dict[str, Any]
    ) -> MobileOtpResponseSchema:
        """
        Verifies a provided mobile OTP code.

        Args:
            request_data (VerifyMobileOtpRequestSchema): Must include:
                - 'otp': The OTP code
                - 'txnId': The related transaction ID

        Returns:
            MobileOtpResponseSchema:
                - txnId (str)

        Raises:
            EhrApiError: On input/API error

        Example:
            ```
            resp = await hpr_service.verify_mobile_otp({"otp": "654321", "txnId": "txn_abcdefgh"})
            print(resp.txnId)
            ```
        ### Response:
            Sample Output:
            {
                "txnId": "txn_abcdefgh",
                "mobileNumber": null
            }
        """
        if not request_data.get("otp"):
            raise EhrApiError("OTP is required", 400)
        validated_data = await self.validate_data(
            VerifyMobileOtpRequestSchema, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.VERIFY_MOBILE_OTP,
                validated_data,
                MobileOtpResponseSchema,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while verifying mobile OTP", exc_info=True
            )
            raise EhrApiError(
                "An unexpected error occurred while verifying mobile OTP"
            ) from e

    async def get_hpr_suggestion(self, request_data: dict[str, Any]) -> list[str]:
        """
        Retrieves a list of HPR ID suggestions appropriate for the current session/transaction.

        Args:
            request_data (HpIdSuggestionRequestSchema): Must include
                - 'txnId' (str)

        Returns:
            list[str]: Suggested unique HPR IDs for user selection.

        Raises:
            EhrApiError: On missing txnId, validation, or service error.

        Example:
            ```
            suggestions = await hpr_service.get_hpr_suggestion({"txnId": "txn_abcdef123456"})
            print(suggestions)  # ["DrJohnDoe", "JohnD123", "J.Doe_Med"]
            ```
        ### Response:
            Sample Output:
            [
                "DrJohnDoe123",
                "DrJohnDoe987",
                "JohnDae01"
            ]
        """
        if not request_data.get("txnId"):
            raise EhrApiError("Transaction ID is required", 400)

        validated_data = await self.validate_data(
            HpIdSuggestionRequestSchema, request_data
        )

        try:
            response: HprIdSuggestionResponse = await self.post(
                HPR_API_ENDPOINTS.GET_HPR_SUGGESTION,
                validated_data,
                HprIdSuggestionResponse,
            )

            # Pydantic's RootModel wraps the list. We return the underlying list.
            return response.root

        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while getting HPR suggestions",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while getting HPR suggestions"
            ) from e

    async def create_hpr_id_with_preverified(
        self, request_data: dict[str, Any]
    ) -> CreateHprIdWithPreVerifiedResponseBody:
        """
        Register a new HPR ID using pre-verified demographic and professional data.

        Args:
            request_data (CreateHprIdWithPreVerifiedRequestBody): Must include all KYC, professional and session details (see DTO for fields).

        Returns:
            CreateHprIdWithPreVerifiedResponseBody: Details of the created HPR ID, token, and participant metadata.

        Raises:
            EhrApiError: On missing input, validation or API failure.

        Example:
            ```
            resp = await hpr_service.create_hpr_id_with_preverified({
                "address": "123 Main St",
                "firstName": "John",
                "lastName": "Doe",
                "yearOfBirth": "1980",
                "monthOfBirth": "01",
                "dayOfBirth": "15",
                "email": "john.doe@example.com",
                "hpCategoryCode": "DOC",
                "hpSubCategoryCode": "GEN",
                "hprId": "JDoeDoc80",
                "password": "StrongPass123!",
                "pincode": "110001",
                "stateCode": "DL",
                "txnId": "txn_abcdef123456",
                ...
            })
            print(resp.hprIdNumber, resp.token)
            ```
        ### Response:
            Sample Output:
            {
                "token": "eyJhbGciOi...",
                "hprIdNumber": "HPR987654",
                "hprId": "HPR987654",
                "name": "John Doe",
                "gender": "M",
                "yearOfBirth": "1980",
                "monthOfBirth": "01",
                "dayOfBirth": "15",
                "firstName": "John",
                "lastName": "Doe",
                "stateCode": "DL",
                "districtCode": "DL001",
                "stateName": "Delhi",
                "districtName": "New Delhi",
                "email": "john.doe@example.com",
                "kycPhoto": "...",
                "mobile": "9876543210",
                "categoryId": 1,
                "subCategoryId": 2,
                "authMethods": ["PIN", "Biometric"],
                "new": True
            }
        """
        if not request_data:
            raise EhrApiError("Request data is required", 400)
        validated_data = await self.validate_data(
            CreateHprIdWithPreVerifiedRequestBody, request_data
        )
        try:
            response = await self.post(
                HPR_API_ENDPOINTS.CREATE_HPR_ID_WITH_PREVERIFIED,
                validated_data,
                CreateHprIdWithPreVerifiedResponseBody,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while creating hpr id with preverified data",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while creating hpr id with preverified data"
            ) from e
