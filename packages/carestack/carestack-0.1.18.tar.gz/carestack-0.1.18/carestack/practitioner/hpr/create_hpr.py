import logging
from typing import Any

from pydantic import ValidationError

from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import HprRegistrationSteps
from carestack.practitioner.hpr.hpr_service import HPRService


class CreateHPR:
    """
    Orchestrates the multi-step Healthcare Professional Registry (HPR) registration process.

    This class streamlines the HPR registration by managing the sequence of API calls required,
    simplifying the backend workflow and enabling guided UI flows.

    It coordinates OTP generation and verification for Aadhaar and mobile, checks for existing accounts,
    performs demographic authentication, fetches HPR ID suggestions, and finally creates the HPR ID.

    Each step returns a detailed message, API response data, the next step in the flow, and hints
    specifying the payload required for subsequent steps, enabling low-code or UI-driven implementations.

    Args:
        config (ClientConfig): Configuration containing API credentials and service endpoints.

    Raises:
        EhrApiError: If any step in the registration process fails or if an unexpected error occurs.
        ValidationError: If the provided payload does not meet the expected schema.

    Returns:
        dict[str, Any]: A dictionary containing the API response data, a user-friendly message,
                        the next step in the registration flow, and hints for the next step's payload.

    Example usage:
        ```
        hpr_creator = CreateHPR(config)
        # Step 1: Generate Aadhaar OTP
        step1_result = await hpr_creator.start_registration("123456789012")

        # Step 2: Verify Aadhaar OTP using OTP and txnId from step1_result
        step2_result = await hpr_creator.registration_flow(
            HprRegistrationSteps.VERIFY_AADHAAR_OTP,
            {
                "otp": "<otp_value>",
                "txnId": step1_result["data"]["txnId"],
                "domainName": "<domain_name>",
                "idType": "aadhaar",
                "restrictions": None  # or any applicable restrictions
            }
        )

        # Proceed with subsequent steps as guided by step2_result["next_step"]
        ```
    """

    def __init__(self, config: ClientConfig):
        self.hpr_service = HPRService(config=config)
        self.logger = logging.getLogger(__name__)

    async def start_registration(self, aadhaar_number: str) -> dict[str, Any]:
        """
        Initiates the HPR registration process by generating an Aadhaar OTP.

        Sends the Aadhaar number to the backend to receive an OTP on the linked mobile number.

        Args:
            aadhaar_number (str): 12-digit Aadhaar number of the healthcare professional.

        Returns:
            dict[str, Any]: A dictionary containing:
                - message (str): Informational message about the OTP generation.
                - data (dict): API response data including txnId and masked mobileNumber.
                - next_step (str): The next registration step name ('VERIFY_AADHAAR_OTP').
                - next_step_payload_hint (dict): Guidance on required fields for next step payload.

        Raises:
            EhrApiError: When the OTP generation fails or unexpected error occurs.

        Example:
            ```
            result = await hpr_creator.start_registration("123456789012")
            print(result["message"])
            print("Transaction ID:", result["data"]["txnId"])
            print("Next step:", result["next_step"])
            ```

        ### Response:
            Sample Output:
            {
                "txnId": "3b440ecf-6cd5-4059-9fdd-12e4c14b931a",
                "mobileNumber": "9871XXXX123",
                "next_step": "VERIFY_AADHAAR_OTP",
                "next_step_payload_hint": {
                    "description": "Provide the OTP received via SMS and the transaction ID.",
                    "required_fields": ["otp", "txnId"],
                    "source_of_data": {"txnId": "from current step's data.txnId"},
                }
            }
        """
        try:
            payload = {"aadhaar": aadhaar_number}
            response = await self.hpr_service.generate_aadhaar_otp(payload)
            return {
                "message": "Aadhaar OTP generated. Please verify it in the registration flow method. Store the generated transactionId for further flow steps.",
                "data": response.model_dump(),
                "next_step": HprRegistrationSteps.VERIFY_AADHAAR_OTP.value,
                "next_step_payload_hint": {
                    "description": "Provide the OTP received via SMS and the transaction ID.",
                    "required_fields": ["otp", "txnId"],
                    "source_of_data": {"txnId": "from current step's data.txnId"},
                },
            }
        except Exception as e:
            self.logger.error(f"Error starting HPR registration: {e}", exc_info=True)
            raise EhrApiError(f"Failed to start registration: {str(e)}") from e

    async def registration_flow(
        self, step: HprRegistrationSteps, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Executes a specific step in the HPR registration workflow, providing guidance for subsequent steps.

        This method handles:
          - Aadhaar OTP verification,
          - Checking existing HPR account,
          - Demographic authentication via mobile,
          - Mobile OTP generation and verification,
          - Retrieving HPR ID suggestions,
          - Creating HPR ID with preverified data.

        Args:
            step (HprRegistrationSteps): The current registration step to execute.
            payload (dict[str, Any]): Data required to complete the current step, varying by step.

        Returns:
            dict[str, Any]: Contains
                - message (str): Informative status message relevant to the step.
                - data (dict): API response data aligned with the step’s DTO.
                - next_step (str or None): The next step identifier or None if registration completed.
                - next_step_payload_hint (dict or None): Guidance on fields required for the next step.

        Raises:
            EhrApiError: For invalid steps, validation failures, or backend errors.

        Detailed Steps and Payload Requirements:
          1. VERIFY_AADHAAR_OTP
             - Payload must include: otp, txnId, domainName, idType, restrictions (optional)
             - Returns txnId and profile data.
             - Next step: CHECK_ACCOUNT_EXIST

          2. CHECK_ACCOUNT_EXIST
             - Payload must include: txnId, preverifiedCheck (boolean indicating pre-verified lookup)
             - If account exists, registration ends.
             - Else, next step: DEMOGRAPHIC_AUTH_VIA_MOBILE

          3. DEMOGRAPHIC_AUTH_VIA_MOBILE
             - Payload must include: txnId, mobileNumber
             - If demographic auth verified (verified == True), implies failure in your flow? (as per your code)
               - Next step: GET_HPR_ID_SUGGESTION
             - Else demographic auth successful, next step: GENERATE_MOBILE_OTP

          4. GENERATE_MOBILE_OTP
             - Payload must include: mobile, txnId
             - Returns txnId for OTP verification.
             - Next step: VERIFY_MOBILE_OTP

          5. VERIFY_MOBILE_OTP
             - Payload must include: otp, txnId
             - Returns txnId.
             - Next step: GET_HPR_ID_SUGGESTION

          6. GET_HPR_ID_SUGGESTION
             - Payload must include: txnId
             - Returns a list of HPR ID suggestions.
             - Next step: CREATE_HPR_ID_WITH_PREVERIFIED

          7. CREATE_HPR_ID_WITH_PREVERIFIED
             - Payload must include: hprId, password, txnId, firstName, middleName, lastName,
               yearOfBirth, dayOfBirth, monthOfBirth, gender, email, mobile, address, etc. (from previous steps)
             - Returns final HPR ID details.
             - Next step: None (registration complete)

        Example:
            ```
            # Step: VERIFY_AADHAAR_OTP
            resp = await hpr_creator.registration_flow(
                HprRegistrationSteps.VERIFY_AADHAAR_OTP,
                {
                    "otp": "123456",
                    "txnId": "3b440ecf-6cd5-4059-9fdd-12e4c14b931a",
                    "domainName": "ndhm.gov.in",
                    "idType": "aadhaar",
                    "restrictions": None,
                }
            )
            print(resp["message"])
            print("Next step:", resp["next_step"])
            ```

        Sample Response for VERIFY_AADHAAR_OTP:
            {
                "message": "Aadhaar OTP verified. Now, check if an HPR account exists.",
                "data": {
                    "txnId": "3b440ecf-6cd5-4059-9fdd-12e4c14b931a",
                    "gender": "M",
                    "mobileNumber": "9871XXXX123",
                    "name": "Dr. John Doe",
                    "email": "john.doe@example.com",
                    ...
                },
                "next_step": "CHECK_ACCOUNT_EXIST",
                "next_step_payload_hint": {
                    "description": "Provide the transaction ID from current step's response data.",
                    "required_fields": ["txnId"],
                    "source_of_data": {"txnId": "from previous response"},
                }
            }

        Sample Response when account exists (at CHECK_ACCOUNT_EXIST):
            {
                "message": "An HPR account already exists for this user. The registration flow is complete.",
                "data": {
                    "hprIdNumber": "HPR12345678",
                    "hprId": "HPR12345678",
                    "token": "...",
                    "categoryId": 1,
                    "subCategoryId": 2,
                    "new": false,
                    "categoryName": "General Physician",
                    "categorySubName": "General Medicine",
                    ...
                },
                "next_step": None,
                "next_step_payload_hint": None
            }

        Sample Response when account does not exist (at CHECK_ACCOUNT_EXIST):
            {
                "message": "No HPR account found. Proceed to demographic authentication via mobile.",
                "data": {
                    "txnId": "3b440ecf-6cd5-4059-9fdd-12e4c14b931a",
                    "token": "some_token",
                    "new": true,
                    ...
                },
                "next_step": "DEMOGRAPHIC_AUTH_VIA_MOBILE",
                "next_step_payload_hint": {
                    "description": "Provide mobileNumber and txnId for demographic auth",
                    "required_fields": ["mobileNumber", "txnId"]
                }
            }
        """
        try:
            self.logger.info(f"Executing HPR registration flow step: {step.value}")

            if step == HprRegistrationSteps.VERIFY_AADHAAR_OTP:
                response = await self.hpr_service.verify_aadhaar_otp(payload)
                return {
                    "message": "Aadhaar OTP verified. Now, check if an HPR account exists.",
                    "data": response.model_dump(),
                    "next_step": HprRegistrationSteps.CHECK_ACCOUNT_EXIST.value,
                    "next_step_payload_hint": {
                        "description": "Provide the transaction ID from the current step's response data to check for an existing account.",
                        "required_fields": [
                            "txnId",
                        ],
                        "source_of_data": {"txnId": "from current step's data.txnId"},
                    },
                }

            elif step == HprRegistrationSteps.CHECK_ACCOUNT_EXIST:
                response = await self.hpr_service.check_account_exist(payload)
                if response.hprIdNumber:
                    return {
                        "message": "An HPR account already exists for this user. The registration flow is complete.",
                        "data": response.model_dump(),
                        "next_step": None,
                        "next_step_payload_hint": None,
                    }
                else:
                    return {
                        "message": "No HPR account found. Proceed to check whether mobile number is aadhaar authenticated or not. Store the response data for creating HPR ID.",
                        "data": response.model_dump(),
                        "next_step": HprRegistrationSteps.DEMOGRAPHIC_AUTH_VIA_MOBILE.value,
                        "next_step_payload_hint": {
                            "description": "Provide the mobile number for verification.",
                            "required_fields": ["mobileNumber", "txnId"],
                            "source_of_data": {
                                "txnId": "from current step's data.txnId"
                            },
                        },
                    }

            elif step == HprRegistrationSteps.DEMOGRAPHIC_AUTH_VIA_MOBILE:
                response = await self.hpr_service.demographic_auth_via_mobile(payload)
                if response.verified:
                    return {
                        "message": "Demographic auth failed. Proceed to get HPR ID suggestions.",
                        "data": response.model_dump(),
                        "next_step": HprRegistrationSteps.GET_HPR_ID_SUGGESTION.value,
                    }
                else:
                    return {
                        "message": "Demographic auth successful. Proceed to generate mobile OTP.",
                        "data": response.model_dump(),
                        "next_step": HprRegistrationSteps.GENERATE_MOBILE_OTP.value,
                        "next_step_payload_hint": {
                            "description": "Provide the mobile number for OTP generation.",
                            "required_fields": ["mobile", "txnId"],
                            "source_of_data": {
                                "txnId": "from current step's data.txnId"
                            },
                        },
                    }

            elif step == HprRegistrationSteps.GENERATE_MOBILE_OTP:
                response = await self.hpr_service.generate_mobile_otp(payload)
                return {
                    "message": "Mobile OTP generated. Please verify it in the next step.",
                    "data": response.model_dump(),
                    "next_step": HprRegistrationSteps.VERIFY_MOBILE_OTP.value,
                    "next_step_payload_hint": {
                        "description": "Provide the OTP value for verification.",
                        "required_fields": ["otp", "txnId"],
                        "source_of_data": {"txnId": "from current step's data.txnId"},
                    },
                }

            elif step == HprRegistrationSteps.VERIFY_MOBILE_OTP:
                response = await self.hpr_service.verify_mobile_otp(payload)
                return {
                    "message": "Mobile OTP verified.",
                    "data": response.model_dump(),
                    "next_step": HprRegistrationSteps.GET_HPR_ID_SUGGESTION.value,
                    "next_step_payload_hint": {
                        "description": "Provide the transaction ID from the current step's response data to select one hprId name in list of options",
                        "required_fields": ["txnId"],
                        "source_of_data": {"txnId": "from current step's data.txnId"},
                    },
                }

            elif step == HprRegistrationSteps.GET_HPR_ID_SUGGESTION:
                response = await self.hpr_service.get_hpr_suggestion(payload)
                return {
                    "message": "HPR ID suggestions retrieved. Proceed to create the HPR ID.",
                    "data": response,
                    "next_step": HprRegistrationSteps.CREATE_HPR_ID_WITH_PREVERIFIED.value,
                    "next_step_payload_hint": {
                        "description": "Provide a chosen hprId, a password, and all user demographic data from previous steps.",
                        "required_fields": [
                            "hprId",
                            "password",
                            "txnId",
                            "firstName",
                            "middleName",
                            "lastName",
                            "yearOfBirth",
                            "dayOfBirth",
                            "monthOfBirth",
                            "gender",
                            "email",
                            "mobile",
                            "address",
                        ],
                        "source_of_data": {
                            "hprId": "user choice from current step's data.suggestions",
                            "password": "user input",
                            "txnId": "from previous steps",
                            "other_fields": "from CHECK_ACCOUNT_EXIST step's data",
                        },
                    },
                }

            elif step == HprRegistrationSteps.CREATE_HPR_ID_WITH_PREVERIFIED:
                response = await self.hpr_service.create_hpr_id_with_preverified(
                    payload
                )
                return {
                    "next_step": None,
                    "message": "HPR ID created successfully. Registration complete.",
                    "data": response.model_dump(),
                }

            else:
                raise EhrApiError(
                    f"Invalid or out-of-sequence step in HPR registration flow: {step}"
                )

        except (EhrApiError, ValidationError) as e:
            self.logger.error(f"Error in HPR flow at step {step}: {e}", exc_info=True)
            raise e
        except Exception as e:
            self.logger.error(
                f"Unexpected error in HPR flow at step {step}", exc_info=True
            )
            raise EhrApiError(
                f"An unexpected error occurred during step {step}: {str(e)}"
            ) from e
