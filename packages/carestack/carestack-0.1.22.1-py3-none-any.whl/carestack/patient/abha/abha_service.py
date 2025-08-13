import logging

from carestack.default_config import DEFAULT_ABHA_PUBLIC_KEY
from carestack.patient.abha.encrypt_data import EncryptData
from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import CREATE_ABHA_ENDPOINTS
from carestack.patient.abha.abha_dto import (
    AbhaAddressSuggestionsResponse,
    CreateAbhaAddressRequest,
    CreateAbhaAddressResponse,
    EnrollWithAadhaar,
    EnrollWithAadhaarResponse,
    GenerateAadhaarOtpRequest,
    UpdateMobileNumberRequest,
    VerifyMobileOtpRequest,
    VerifyMobileOtpResponse,
    VerifyOtpResponse,
)


class ABHAService(BaseService):
    """
    High-level service for managing ABHA (Ayushman Bharat Health Account) creation and verification workflows.

    !!! note "Key Features"
        - Securely handles all ABHA account creation and verification steps.
        - Encrypts sensitive data (Aadhaar, OTP, mobile) using a public key from the environment.
        - Robust error handling and logging for all ABHA-related operations.
        - Designed for easy SDK and application integration.

    Methods:
        generate_aadhaar_otp(request_body): Initiates the ABHA creation flow by generating an OTP for Aadhaar verification.
        enroll_with_aadhaar(request_body): Completes ABHA enrollment using the OTP received on the Aadhaar-linked mobile number.
        generate_mobile_otp(request_body): Generates an OTP for mobile number verification or update.
        verify_mobile_otp(request_body): Verifies the OTP sent to the user's mobile number for ABHA workflows.
        abha_address_suggestion(txnId): Fetches a list of available ABHA address (username) suggestions for the user.
        create_abha_address(request_body): Registers the chosen ABHA address, finalizing the ABHA creation process.


    Args:
        config (ClientConfig): API credentials and settings for service initialization.

    Raises:
        EhrApiError: For validation, API, or unexpected errors during operations.

    Example usage:
        ```
        config = ClientConfig(
            api_key="your_api_key",

        )
        service = ABHAService(config)
        otp_resp = await service.generate_aadhaar_otp(GenerateAadhaarOtpRequest(aadhaar="xxxx"))
        enroll_resp = await service.enroll_with_aadhaar(EnrollWithAadhaar(...))
        ```

    """

    def __init__(self, config: ClientConfig):

        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.encryptData = EncryptData()
        abha_public_key_str = DEFAULT_ABHA_PUBLIC_KEY
        self.abha_public_key = (
            abha_public_key_str.replace("\\n", "\n") if abha_public_key_str else None
        )
        if not self.abha_public_key:
            self.logger.warning(
                "ABHA_PUBLIC_KEY environment variable is not set. Encryption will fail."
            )

    async def generate_aadhaar_otp(
        self, request_body: GenerateAadhaarOtpRequest
    ) -> VerifyOtpResponse:
        """
        Initiates Aadhaar-based OTP generation.

        This method securely encrypts the Aadhaar number using the ABHA public key and requests the ABHA service
        to generate and send an OTP to the user's Aadhaar-linked mobile. The response includes a transaction ID (txnId)
        required for the next step of the ABHA enrollment process.

        Args:
            request_body (GenerateAadhaarOtpRequest): User's 12-digit Aadhaar number (unmasked).

        Returns:
            VerifyOtpResponse:
                - txnId (str): Transaction/session ID for subsequent requests (OTP verification).
                - message (str): Status of OTP generation request.

        Raises:
            EhrApiError: If Aadhaar is invalid, encryption fails, network/API issues, or OTP dispatch fails.

        Example:
            ```
            req = GenerateAadhaarOtpRequest(aadhaar="123412341234")
            resp = await abha_service.generate_aadhaar_otp(req)
            print(resp.txnId, resp.message)
            ```

        ### Response:
            Sample Output :
            {
                "txnId": "3b440ecf-6cd5-4059-9fdd-12e4c14b931a",
                "message": "OTP sent successfully to your Aadhaar-linked mobile"
            }
        """

        try:
            encrypted_aadhaar = await self.encryptData.encrypt_data_for_abha(
                data_to_encrypt=request_body.aadhaar,
                certificate_pem=self.abha_public_key,
            )

            payload = {"aadhaar": encrypted_aadhaar}

            response = await self.post(
                CREATE_ABHA_ENDPOINTS.GENERATE_AADHAAR_OTP,
                payload,
                response_model=VerifyOtpResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while generating aadhaar based otp",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while generating aadhaar based otp"
            ) from e

    async def enroll_with_aadhaar(
        self, request_body: EnrollWithAadhaar
    ) -> EnrollWithAadhaarResponse:
        """
        Completes ABHA enrollment using Aadhaar OTP.

        Encrypts the OTP received on the Aadhaar-linked mobile and submits it with the transaction ID and user's mobile
        number. This finalizes ABHA onboarding, returning a profile, tokens, and session info. Use after successfully verifying the OTP.

        Args:
            request_body (EnrollWithAadhaar): User's OTP, transaction ID, and mobile number.

        Returns:
            EnrollWithAadhaarResponse:
                - message (str): Server reply about enrollment result.
                - txnId (str): Enrollment transaction/session ID.
                - ABHAProfile (AbhaProfile): User’s KYC/demographic info.
                - tokens (AbhaTokens): Short-lived access/refresh authentication tokens.
                - isNew (bool): True if account was newly created.

        Raises:
            EhrApiError: On OTP errors (expired/invalid), encryption failure, or network/server issues.

        Example:
            ```
            req = EnrollWithAadhaar(otp="123456", txnId="d309dc12...", mobile="9123456789")
            resp = await abha_service.enroll_with_aadhaar(req)
            print(resp.ABHAProfile.firstName, resp.isNew)
            ```

        ### Response:
            Sample Output:
            {
                "message": "ABHA enrollment successful.",
                "txnId": "d309dc12-3cf6-4127-9bd9-8d184d8eb45b",
                "ABHAProfile": {
                    "firstName": "Asha",
                    "lastName": "Verma",
                    "mobile": "9123456789",
                    "...": "..."
                },
                "tokens": {
                    "token": "eyJhbGc...",
                    "expiresIn": 1800,
                    "refreshToken": "dGhpcy...",
                    "refreshExpiresIn": 86400
                },
                "isNew": true
            }
        """

        try:
            encrypted_otp = await self.encryptData.encrypt_data_for_abha(
                data_to_encrypt=request_body.otp,
                certificate_pem=self.abha_public_key,
            )

            payload = {
                "otp": encrypted_otp,
                "txnId": request_body.txnId,
                "mobile": request_body.mobile,
            }

            response = await self.post(
                CREATE_ABHA_ENDPOINTS.ENROLL_WITH_AADHAAR,
                payload,
                response_model=EnrollWithAadhaarResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while enrolling with aadhaar",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while enrolling with aadhaar"
            ) from e

    async def generate_mobile_otp(
        self, request_body: UpdateMobileNumberRequest
    ) -> VerifyOtpResponse:
        """
        Initiates mobile OTP generation for verification or update.

        Securely encrypts the provided mobile number and requests the ABHA service to generate/send an OTP for that number.
        Useful for onboarding, mobile update, or mobile verification.

        Args:
            request_body (UpdateMobileNumberRequest): User's new mobile number (unmasked).

        Returns:
            VerifyOtpResponse:
                - txnId (str): Transaction ID to be used for OTP verification.
                - message (str): Status/result of the OTP send request.

        Raises:
            EhrApiError: For invalid numbers, encryption failure, or network/server/dispatch errors.

        Example:
            ```
            req = UpdateMobileNumberRequest(updateValue="9123456789", txnId="txn2456")
            resp = await abha_service.generate_mobile_otp(req)
            print(resp.txnId, resp.message)
            ```

        ### Response:
            Sample Output:
            {
                "txnId": "f4b7057c-8374-46df-ad65-c6a18aa6a326",
                "message": "OTP sent to the new mobile number."
            }
        """

        try:
            encrypted_mobile = await self.encryptData.encrypt_data_for_abha(
                data_to_encrypt=request_body.updateValue,
                certificate_pem=self.abha_public_key,
            )
            payload = {"updateValue": encrypted_mobile, "txnId": request_body.txnId}

            response = await self.post(
                CREATE_ABHA_ENDPOINTS.GENERATE_MOBILE_OTP,
                payload,
                response_model=VerifyOtpResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while generating mobile otp",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while generating mobile otp"
            ) from e

    async def verify_mobile_otp(
        self, request_body: VerifyMobileOtpRequest
    ) -> VerifyMobileOtpResponse:
        """
        Verifies the OTP sent to the user's mobile.

        Securely encrypts and submits the OTP received by the user to the ABHA service, completing mobile verification or update.
        Use after `generate_mobile_otp`.

        Args:
            request_body (VerifyMobileOtpRequest): User's OTP and transaction ID.

        Returns:
            VerifyMobileOtpResponse:
                - message (str): Status or outcome of OTP verification.
                - txnId (str): Verification session ID.
                - authResult (str): Result (e.g., "VERIFIED" or "FAILED").

        Raises:
            EhrApiError: On OTP invalid/expired/failure, encryption issues, server errors.

        Example:
            ```
            req = VerifyMobileOtpRequest(otp="456789", txnId="txn6677")
            resp = await abha_service.verify_mobile_otp(req)
            print(resp.message, resp.authResult)
            ```

        ### Response:
            Sample Output :
            {
                "message": "Mobile verified and updated successfully.",
                "txnId": "a1e4b8e7-bc7f-4cc3-ac8b-03b4d4826e86",
                "authResult": "VERIFIED"
            }
        """

        try:
            encrypted_otp = await self.encryptData.encrypt_data_for_abha(
                data_to_encrypt=request_body.otp, certificate_pem=self.abha_public_key
            )
            payload = {"otp": encrypted_otp, "txnId": request_body.txnId}

            response = await self.post(
                CREATE_ABHA_ENDPOINTS.VERIFY_MOBILE_OTP,
                payload,
                response_model=VerifyMobileOtpResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while verifying mobile otp",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while verifying mobile otp"
            ) from e

    async def abha_address_suggestion(
        self, txnId: str
    ) -> AbhaAddressSuggestionsResponse:
        """
        Provides a list of available ABHA address (username) suggestions.

        Fetches unique, available PHR address (username) suggestions for the user for the current session,
        aiding user choice for ABHA registration.

        Args:
            txnId (str): Transaction ID obtained from a previous successful OTP/auth step.

        Returns:
            AbhaAddressSuggestionsResponse:
                - abhaAddressList (list[str]): List of suggested unique ABHA addresses.
                - txnId (str): Session/transaction ID.

        Raises:
            EhrApiError: If session invalid/expired or on server/network issues.

        Example:
            ```
            resp = await abha_service.abha_address_suggestion(txnId="txn1234")
            print(resp.abhaAddressList)
            ```

        ### Response:
            Sample Output :
            {
                "abhaAddressList": [
                    "ashaverma.abdm@sbx",
                    "ashaverma1.abdm@sbx",
                    "ashaverma1978.abdm@sbx"
                ],
                "txnId": "txn1234"
            }
        """

        try:
            response = await self.get(
                CREATE_ABHA_ENDPOINTS.ABHA_ADDRESS_SUGGESTION,
                query_params={"txnId": txnId},
                response_model=AbhaAddressSuggestionsResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while getting abha address suggestions",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while getting abha address suggestions"
            ) from e

    async def create_abha_address(
        self, request_body: CreateAbhaAddressRequest
    ) -> CreateAbhaAddressResponse:
        """
        Registers and activates a user's chosen ABHA address.

        Registers the specified ABHA address (selected from suggestions) for the user with the ABHA system, assigning
        a unique ABHA number. Use only addresses suggested as available.

        Args:
            request_body (CreateAbhaAddressRequest): User's chosen ABHA address and transaction ID.

        Returns:
            CreateAbhaAddressResponse:
                - txnId (str): Session/transaction ID of this operation.
                - healthIdNumber (str): Issued ABHA number (e.g., "1234-5678-9012").
                - preferredAbhaAddress (str): Successfully registered and activated ABHA address.

        Raises:
            EhrApiError: If chosen address is unavailable, registration fails, session expired, or server issues.

        Example:
            ```
            req = CreateAbhaAddressRequest(abhaAddress="ashaverma1978.abdm@sbx", txnId="txn6789")
            resp = await abha_service.create_abha_address(req)
            print(resp.healthIdNumber, resp.preferredAbhaAddress)
            ```

        ### Response:
            Sample Output :
            {
                "txnId": "2ab3d0a7-fb55-4627-9dff-ef780ead3e8f",
                "healthIdNumber": "1234-5678-9012",
                "preferredAbhaAddress": "ashaverma1978.abdm@sbx"
            }
        """

        try:
            payload = {
                "abhaAddress": request_body.abhaAddress,
                "txnId": request_body.txnId,
            }

            response = await self.post(
                CREATE_ABHA_ENDPOINTS.CREATE_ABHA,
                payload,
                response_model=CreateAbhaAddressResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "An unexpected error occurred while creating abha address",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while creating abha address"
            ) from e
