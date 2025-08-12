import logging
from carestack.patient.abha.abha_service import ABHAService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError, ValidationError
from carestack.common.enums import AbhaSteps
from carestack.patient.abha.abha_dto import (
    CreateAbhaAddressRequest,
    EnrollWithAadhaar,
    GenerateAadhaarOtpRequest,
    UpdateMobileNumberRequest,
    VerifyMobileOtpRequest,
)


class CreateABHA:
    """
    Orchestrated ABHA (Ayushman Bharat Health Account) Registration Workflow

    The `CreateABHA` class provides an end-to-end, asynchronous workflow manager for the multi-step creation
    of an ABHA ID under India's National Digital Health Mission (NDHM).

    !!! note "Key Features"
        - This class abstracts away the low-level calls to individual APIs by sequencing the steps involved.
        - Initiating Aadhaar-based OTP (One-Time Password) for user identity validation.
        - Completing Aadhaar OTP / mobile verification and linking user’s phone.
        - Generating and verifying mobile OTP as required.
        - Retrieving and confirming an ABHA address (user’s health account “username”).
        - Completing the registration process and collecting final ABHA credentials.

    All steps return [clear next-step instructions and payload hints](#registration_flow) so you can
    drive both back-end workflows and complex UI wizards easily.

    Typical user journey:
        - Step 1: Call `start_registration` with an Aadhaar number.
        - Steps 2+: Pass the recommended next step and collected fields to `registration_flow`.
        - Process the returned "next_step" and "next_step_payload_hint" at each stage to guide the next user input.

    Args:
        config (ClientConfig): Configuration object for the ABHA service client.

    Methods:
        start_registration : Initiates the ABHA registration process by generating an OTP for the provided Aadhaar number.
        registration_flow : Advances the ABHA registration workflow by executing a specific step with the required data.

    Returns:
            response[dict]: A dictionary containing the next step and its payload hint.

    Raises:
        EhrApiError, ValidationError: On service or data validation failures.
        Exception: For business logic errors or workflow step violations.

    Example Usage:
        ```
        config = ClientConfig(
            api_base_url="https://api.example.com",
            api_key="your_api_key",
            api_secret="your_api_secret"
        )
        abha_creator = CreateABHA(config)

        # Step 1: Aadhaar OTP
        step1 = await abha_creator.start_registration("123412341234")
        # Step 2: Enroll with Aadhaar OTP
        step2 = await abha_creator.registration_flow(
            AbhaSteps.ENROLL_WITH_AADHAAR,
            {"otp": "123456", "txnId": step1["data"]["txnId"], "mobile": "9123456780"}
        )
        # Follow step2["next_step"] for further steps as guided
        ```
    """

    def __init__(self, config: ClientConfig):
        self.abha_service = ABHAService(config=config)
        self.logger = logging.getLogger(__name__)

    async def start_registration(self, aadhaar_number: str) -> dict:
        """
        Initiates Aadhaar-based OTP flow to begin ABHA registration.

        ### Description:
            - Securely encrypts the provided Aadhaar number.
            - Requests the ABHA service to send an OTP to the mobile number linked with Aadhaar.
            - The returned transaction ID (txnId) is essential for verifying OTP and continuing the workflow.

        Args:
            aadhaar_number (str): 12-digit Aadhaar number (as a string, numbers only).

        Returns:
            dict:
                - "message": Human-readable description of result.
                - "data": The raw VerifyOtpResponse as a dict with txnId and message.
                - "next_step": Recommended next step as AbhaSteps value ("ENROLL_WITH_AADHAAR").
                - "next_step_payload_hint": Details the expected payload for next registration_flow step.

        Raises:
            Exception: For encryption, networking, or service errors (with context in logs).

        Example:
            ```
            result = await abha_creator.start_registration("123412341234")
            # Use result["data"]["txnId"] for the next step
            ```

        ### Response:
            Sample Output:
            -----------
            {
                "message": "Aadhaar OTP generated. Please enroll with aadhaar by passing transactionId in next step",
                "data": {
                    "txnId": "3b440ecf-6cd5-4059-9fdd-12e4c14b931a",
                    "message": "OTP sent successfully to your Aadhaar-linked mobile"
                },
                "next_step": "ENROLL_WITH_AADHAAR",
                "next_step_payload_hint": {
                    "description": "Provide the OTP received via SMS and the transaction ID.",
                    "required_fields": ["otp", "txnId"],
                    "source_of_data": {"txnId": "from current step's data.txnId"}
                }
            }
        """

        try:
            request_body = GenerateAadhaarOtpRequest(aadhaar=aadhaar_number)
            response = await self.abha_service.generate_aadhaar_otp(request_body)
            return {
                "message": "Aadhaar OTP generated. Please enroll with aadhaar by passing transactionId in next step",
                "data": response.model_dump(),
                "next_step": AbhaSteps.ENROLL_WITH_AADHAAR.value,
                "next_step_payload_hint": {
                    "description": "Provide the OTP received via SMS and the transaction ID.",
                    "required_fields": ["otp", "txnId", "mobile"],
                    "source_of_data": {"txnId": "from current step's data.txnId"},
                },
            }
        except Exception as e:
            self.logger.error(f"Error starting ABHA registration: {e}", exc_info=True)
            raise e

    async def registration_flow(self, step: AbhaSteps, payload: dict) -> dict:
        """
        Advance the ABHA registration workflow by executing a specific registration step.

        This method allows you to move through the sequential steps needed to create an ABHA ID,
        including enrollment with Aadhaar OTP, mobile OTP generation/verification,
        address suggestions, and final address creation.

        You pass in the current step and the required data for that step. The method
        executes the step, returns the result, and provides guidance for the next step.

        Args:
            step (AbhaSteps): The current ABHA registration step to execute. Possible values:
                - ENROLL_WITH_AADHAAR
                - GENERATE_MOBILE_OTP
                - VERIFY_MOBILE_OTP
                - ABHA_ADDRESS_SUGGESTION
                - CREATE_ABHA_ADDRESS

            payload (dict): Required data fields for the step:
                - ENROLL_WITH_AADHAAR: {'otp', 'txnId', 'mobile'}
                - GENERATE_MOBILE_OTP: {'updateValue', 'txnId'}  # updateValue = mobile number
                - VERIFY_MOBILE_OTP: {'otp', 'txnId'}
                - ABHA_ADDRESS_SUGGESTION: {'txnId'}
                - CREATE_ABHA_ADDRESS: {'abhaAddress', 'txnId'}

        Returns:
            dict: Contains the following keys:
                - 'message' (str): status message.
                - 'data' (dict): Response data from the ABHA API for the current step.
                - 'next_step' (str or None): Next step in the flow, or None if registration is complete.
                - 'next_step_payload_hint' (dict or None): Specifies what fields are needed for the next step.

        Raises:
            EhrApiError, ValidationError: If API returns an error or validation fails.
            Exception: For invalid steps or unexpected errors.

        Example usage:
            ```
            # After obtaining txnId from start_registration:
            result = await abha_creator.registration_flow(
                AbhaSteps.ENROLL_WITH_AADHAAR,
                {'otp': '123456', 'txnId': '<txnId>', 'mobile': '9876543210'}
            )
            print(result['message'])
            if result['next_step']:
                print(f"Next step: {result['next_step']}")
                print(f"Payload needed: {result['next_step_payload_hint']}")
            ```

        ### Example output when mobile is already verified (EnrollWithAadhaarResponse):

            {
                "message": "Aadhaar OTP verified. Mobile already verified. Proceed to address suggestion.",
                "data": {
                    "message": "Enrollment successful",
                    "txnId": "d309dc12-3cf6-4127-9bd9-8d184d8eb45b",
                    "ABHAProfile": {
                        "preferredAddress": "ashaverma.abdm@sbx",
                        "firstName": "Asha",
                        "lastName": "Verma",
                        "middleName": "K",
                        "dob": "1980-07-15",
                        "gender": "F",
                        "profilePhoto": null,
                        "mobile": "9123456789",
                        ...
                        "yearOfBirth": "1980"
                    },
                    "tokens": {
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "expiresIn": 3600,
                        "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9_refresh...",
                        "refreshExpiresIn": 86400
                    },
                    "isNew": true
                },
                "next_step": "ABHA_ADDRESS_SUGGESTION",
                "next_step_payload_hint": {
                    "description": "Provide 'txnId' from this step's data for address suggestion.",
                    "required_fields": ["txnId"],
                    "source_of_data": {"txnId": "from current step's data.txnId"}
                }
            }

        ### Example output when mobile OTP verification is needed (after GENERATE_MOBILE_OTP and VERIFY_MOBILE_OTP steps):

            {
                "message": "Mobile OTP verified.",
                "data": {
                    "message": "Mobile verified successfully",
                    "txnId": "a1e4b8e7-bc7f-4cc3-ac8b-03b4d4826e86",
                    "authResult": "VERIFIED"
                },
                "next_step": "ABHA_ADDRESS_SUGGESTION",
                "next_step_payload_hint": {
                    "description": "Provide 'txnId' to fetch address suggestions.",
                    "required_fields": ["txnId"],
                    "source_of_data": {"txnId": "from current step's data.txnId"}
                }
            }

        ### Example output of ABHA address suggestions (AbhaAddressSuggestionsResponse):

            {
                "message": "ABHA ID suggestions retrieved. Proceed to create the ABHA ID.",
                "data": {
                    "abhaAddressList": [
                        "ashaverma.abdm@sbx",
                        "ashaverma1.abdm@sbx",
                        "ashaverma1978.abdm@sbx"
                    ],
                    "txnId": "txn1234"
                },
                "next_step": "CREATE_ABHA_ADDRESS",
                "next_step_payload_hint": {
                    "description": "Choose one abhaAddress and provide it with txnId for registration.",
                    "required_fields": ["abhaAddress", "txnId"],
                    "source_of_data": {
                        "abhaAddress": "from data.abhaAddressList above",
                        "txnId": "from previous step"
                    }
                }
            }

        ### Example output of final creation success (CreateAbhaAddressResponse):

            {
                "message": "ABHA ID created successfully. Registration complete.",
                "data": {
                    "txnId": "2ab3d0a7-fb55-4627-9dff-ef780ead3e8f",
                    "healthIdNumber": "1234-5678-9012",
                    "preferredAbhaAddress": "ashaverma1978.abdm@sbx"
                },
                "next_step": null
            }
        """

        try:
            self.logger.info(f"Executing ABHA registration flow step: {step.value}")
            if step == AbhaSteps.ENROLL_WITH_AADHAAR:
                request_body = EnrollWithAadhaar(**payload)
                response = await self.abha_service.enroll_with_aadhaar(request_body)

                if response.ABHAProfile.mobile == payload.get("mobile"):
                    # Same mobile → already verified mobile, skip mobile OTP step
                    return {
                        "message": "Aadhaar OTP verified. Mobile already verified. Proceed to address suggestion.",
                        "data": response.model_dump(),
                        "next_step": AbhaSteps.ABHA_ADDRESS_SUGGESTION.value,
                        "next_step_payload_hint": {
                            "description": "Provide the transaction ID to select ABHA address.",
                            "required_fields": ["txnId"],
                            "source_of_data": {
                                "txnId": "from current step's data.txnId"
                            },
                        },
                    }
                else:
                    # Different mobile → need to verify mobile OTP
                    return {
                        "message": "Aadhaar OTP verified. Mobile not matching. Proceed to generate mobile OTP.",
                        "data": response.model_dump(),
                        "next_step": AbhaSteps.GENERATE_MOBILE_OTP.value,
                        "next_step_payload_hint": {
                            "description": "Provide the mobile number in the updateValue field to generate OTP, and txnId from this step.",
                            "required_fields": ["updateValue", "txnId"],
                            "source_of_data": {
                                "txnId": "from current step's data.txnId"
                            },
                        },
                    }

            elif step == AbhaSteps.GENERATE_MOBILE_OTP:
                request_body = UpdateMobileNumberRequest(**payload)
                response = await self.abha_service.generate_mobile_otp(request_body)
                return {
                    "message": "Mobile OTP generated. Please verify it in the next step.",
                    "data": response.model_dump(),
                    "next_step": AbhaSteps.VERIFY_MOBILE_OTP.value,
                    "next_step_payload_hint": {
                        "description": "Provide the OTP value for verification.",
                        "required_fields": ["otp", "txnId"],
                        "source_of_data": {"txnId": "from current step's data.txnId"},
                    },
                }
            elif step == AbhaSteps.VERIFY_MOBILE_OTP:
                request_body = VerifyMobileOtpRequest(**payload)
                response = await self.abha_service.verify_mobile_otp(request_body)
                return {
                    "message": "Mobile OTP verified.",
                    "data": response.model_dump(),
                    "next_step": AbhaSteps.ABHA_ADDRESS_SUGGESTION.value,
                    "next_step_payload_hint": {
                        "description": "Provide the transaction ID from the current step's response data to select one abhaId name in list of options",
                        "required_fields": ["txnId"],
                        "source_of_data": {"txnId": "from current step's data.txnId"},
                    },
                }
            elif step == AbhaSteps.ABHA_ADDRESS_SUGGESTION:
                response = await self.abha_service.abha_address_suggestion(
                    payload["txnId"]
                )
                return {
                    "message": "ABHA ID suggestions retrieved. Proceed to create the ABHA ID.",
                    "data": response.model_dump(),
                    "next_step": AbhaSteps.CREATE_ABHA_ADDRESS.value,
                    "next_step_payload_hint": {
                        "description": "Provide a chosen abhaAddress and txnId from current step.",
                        "required_fields": ["abhaAddress", "txnId"],
                        "source_of_data": {
                            "abhaAddress": "user choice from current step's data.suggestions",
                            "txnId": "from previous steps",
                        },
                    },
                }

            elif step == AbhaSteps.CREATE_ABHA_ADDRESS:
                request_body = CreateAbhaAddressRequest(**payload)
                response = await self.abha_service.create_abha_address(request_body)
                return {
                    "message": "ABHA ID created successfully. Registration complete.",
                    "data": response.model_dump(),
                    "next_step": None,
                }

            else:
                raise Exception(
                    f"Invalid or out-of-sequence step in ABHA registration flow: {step}"
                )
        except (EhrApiError, ValidationError) as e:
            self.logger.error(
                f"Error in the ABHA flow at step {step}: {e}", exc_info=True
            )
            raise e
        except Exception as e:
            self.logger.error(f"Error in ABHA flow at step {step}: {e}", exc_info=True)
            raise e
