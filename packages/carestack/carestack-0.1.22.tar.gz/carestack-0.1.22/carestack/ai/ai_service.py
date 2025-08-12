import logging
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

from carestack.ai.ai_utils import AiUtilities
from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import AI_ENDPOINTS
from carestack.ai.ai_dto import (
    DischargeSummaryResponse,
    FhirBundleResponse,
    GenerateFhirBundleDto,
    ProcessDSDto,
)

_DTO_T = TypeVar("_DTO_T", bound=BaseModel)


class AiService(BaseService):
    """
    AiService provides a high-level interface for AI-powered healthcare document generation.

    ### This service enables SDK users to interact with CareStack AI endpoints for:
      - Generating discharge summaries (`generate_discharge_summary`)
      - Generating FHIR bundles (`generate_fhir_bundle`)

    !!! note "Key Features"
        - Validates input data using Pydantic models (`ProcessDSDto`, `GenerateFhirBundleDto`)
        - Handles encryption of sensitive data before transmission
        - Provides robust error handling and logging for all operations

    Methods:
        generate_discharge_summary(process_ds_data) : Generates a discharge summary from provided case data.
        generate_fhir_bundle(generate_fhir_bundle_data) : Generates a FHIR-compliant bundle from provided case data.

    Args:
        config (ClientConfig): API credentials and settings for service initialization.

    Raises:
        EhrApiError: For validation, API, or unexpected errors during operations.

    Example Usage:
        ```
        config = ClientConfig(
            api_base_url="https://api.example.com",
            api_key="your_api_key",
            api_secret="your_api_secret"
        )
        service = AiService(config)
        summary = await service.generate_discharge_summary({...})
        bundle = await service.generate_fhir_bundle({...})
        ```


    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.utilities = AiUtilities()

    async def _validate_data(
        self, dto_type: Type[_DTO_T], request_data: dict[str, Any]
    ) -> _DTO_T:
        """
        Validate dictionary data against a Pydantic model.

        This internal utility ensures that the provided dictionary matches the expected schema for the AI API.
        Raises an EhrApiError if validation fails.

        Args:
            dto_type (Type[_DTO_T]): The Pydantic model class to validate against.
            request_data (dict): The data to validate.

        Returns:
            _DTO_T: An instance of the validated Pydantic model.

        ### Raises:
            EhrApiError: If validation fails.
        """
        try:
            validated_instance: _DTO_T = dto_type(**request_data)
            return validated_instance
        except ValidationError as err:
            self.logger.error(
                f"Pydantic validation failed: {err.errors()}", exc_info=True
            )
            raise EhrApiError(f"Validation failed: {err.errors()}", 400) from err

    async def generate_discharge_summary(
        self, process_ds_data: dict[str, Any]
    ) -> DischargeSummaryResponse:
        """
        Generate a discharge summary using AI based on the provided case data.

        This method validates and processes the input data, encrypts it if necessary, and calls the AI API
        to generate a discharge summary. Use this to automate the creation of discharge summaries from clinical data.

        Attributes:
            process_ds_data (ProcessDSDto): ProcessDSDto containing required inputs for processing the discharge summary.

        Args:
            caseType (str): Type of the case `CaseType`. Must be a value of (eg: `CaseType.DISCHARGE_SUMMARY` or `CaseType.PRESCRIPTION`).
            files (Optional[list[str]]): List of file identifiers. Used only if `encryptedData` is not provided.
            encryptedData (Optional[str]): Encrypted string payload to send directly to the AI.
            publicKey (Optional[str]): Public key used for encryption, required if `files` are provided.

        ### Returns:
            DischargeSummaryResponse: Contains:
                - dischargeSummary (Optional[dict]): AI-generated summary content
                - extractedData (dict): Extracted clinical content from input
                - fhirBundle (dict): FHIR-compliant bundle based on extracted data

        Raises:
            ValueError: If both 'files' and 'encryptedData' are missing
            ValidationError: If input fails Pydantic schema validation
            EhrApiError: Raised with status codes 400, 422, or 500 depending on the failure

        Example (Success):
            ```
            response = await service.generate_discharge_summary({
                "caseType": "inpatient",
                "files": ["file123.pdf"],
                "publicKey": "-----BEGIN PUBLIC KEY-----..."
            })

            print(response)
            ```
        ### Response:

            Output will looks like :

            DischargeSummaryResponse(
                id='summary-abc-123',
                dischargeSummary={
                    "patientName": "John Doe",
                    "diagnosis": "Hypertension",
                    "treatment": "Medication and lifestyle changes"
                },
                extractedData={
                    "encounterDate": "2025-07-30",
                    "doctor": "Dr. Smith"
                },
                fhirBundle={
                    "resourceType": "Bundle",
                    "entry": [...]
                }
            )

        Example (Validation Failure):
            ```
            await service.generate_discharge_summary({
                "caseType": "DischargeSummary"
            })
            # Raises EhrApiError: No files or encrypted data provided (422)
            ```
        """

        self.logger.info(
            f"Starting generation of discharge summary with data: {process_ds_data}"
        )
        try:
            process_ds_dto: ProcessDSDto = await self._validate_data(
                ProcessDSDto, process_ds_data
            )
            # Throw an error if there is no encrypted_data and no files are provided.
            if not process_ds_dto.encrypted_data and not process_ds_dto.files:
                raise ValueError("No files or encrypted data provided.")

            # If encrypted_data is provided, use it. Otherwise, encrypt the files.
            if process_ds_dto.encrypted_data:
                encrypted_data = process_ds_dto.encrypted_data
            else:
                payload_to_encrypt = {"files": process_ds_dto.files}
                encrypted_data = await self.utilities.encryption(
                    payload=payload_to_encrypt
                )

            payload = {
                "caseType": process_ds_dto.case_type,
                "encryptedData": encrypted_data,
                "publicKey": process_ds_dto.public_key,
            }

            if process_ds_dto.public_key:
                payload["publicKey"] = process_ds_dto.public_key

            discharge_summary: DischargeSummaryResponse = await self.post(
                AI_ENDPOINTS.GENERATE_DISCHARGE_SUMMARY,
                payload,
                response_model=DischargeSummaryResponse,
            )

            return discharge_summary

        except EhrApiError as e:
            self.logger.error(
                f"EHR API Error during discharge summary generation: {e.message}",
                exc_info=True,
            )
            raise
        except ValueError as e:
            self.logger.error(
                f"Validation error in discharge summary generation: {e}", exc_info=True
            )
            raise EhrApiError(str(e), 422) from e
        except Exception as error:
            error_message = str(error)
            self.logger.error(
                f"Unexpected error in generate_discharge_summary: {error_message}",
                exc_info=True,
            )
            raise EhrApiError(
                f"An unexpected error occurred while generating discharge summary: {error_message}",
                500,
            ) from error

    async def generate_fhir_bundle(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Generates a FHIR bundle based on the provided data.

        This method validates and processes the input, encrypts extracted data if necessary, and sends it to the AI API
        to generate a FHIR-compliant bundle. Use this method to automate generation of interoperable FHIR bundles from structured clinical data.

        Attributes:
            generate_fhir_bundle_data (GenerateFhirBundleDto): GenerateFhirBundleDto containing required inputs for generating the bundle.

        ### Args:
            generate_fhir_bundle_data (dict): Dictionary containing:
                - caseType (str): Type of the case (`inpatient`, `outpatient`, etc.)
                - enableExtraction (bool): Flag to enable data extraction from provided documents.
                - documentReferences (list[str]): List of document references to include in the bundle.
                - recordId (Optional[str]): Unique identifier for the record.
                - extractedData (Optional[dict]): Structured clinical data to generate the bundle.
                - encryptedData (Optional[str]): If provided, skips encryption and uses this encrypted payload.
                - publicKey (Optional[str]): Required if using `extractedData` without pre-encryption.

        ### Returns:
            dict[str, Any]: The generated FHIR-compliant bundle.
                Example:
                {
                    "resourceType": "Bundle",
                    "type": "document",
                    "entry": [
                        {
                            "resource": {
                                "resourceType": "Patient",
                                "id": "123",
                                ...
                            }
                        },
                        ...
                    ]
                }

        Raises:
            ValidationError: If input fails Pydantic model validation.
            EhrApiError: Raised on API failure (status 400/422/500).
            ValueError: If both `extractedData` and `encryptedData` are missing.

        ### Example (Success):

            response = await service.generate_fhir_bundle({
                "caseType": "DischargeSummary",
                "enableExtraction": True,
                "documentReferences": ["doc123", "doc456"],
                "recordId": "rec-789",
                "extractedData": {
                    "patientName": "John Doe",
                    "diagnosis": "Hypertension",
                    "treatment": "Medication and lifestyle changes"
                },
                "publicKey": "-----BEGIN PUBLIC KEY-----...",
            })

            print(response)

            Output will look like:

            {
                "resourceType": "Bundle",
                "entry": [
                    {"resource": {"resourceType": "Patient", "id": "123", ...}},
                    ...
                ]
            }

        ### Example (Validation Failure):

            await service.generate_fhir_bundle({
                "caseType": "DischargeSummary"
            })
            # Raises EhrApiError: No extracted data or encrypted data provided (422)
        """
        self.logger.info(f"Starting generation of FHIR bundle with data: {data}")
        try:
            validated_data: GenerateFhirBundleDto = await self._validate_data(
                GenerateFhirBundleDto, data
            )
            encryption_payload: dict[str, Any] = {}
            if validated_data.enable_extraction:
                if not validated_data.extracted_data:
                    raise ValueError("No extracted data is provided.")
                else:
                    encryption_payload["extractedData"] = validated_data.extracted_data
            else:
                if validated_data.patient_details and validated_data.doctors_details:
                    encryption_payload["patientDetails"] = (
                        validated_data.patient_details.model_dump(by_alias=True)
                    )
                    encryption_payload["practitionersDetails"] = [
                        doc.model_dump(by_alias=True)
                        for doc in validated_data.doctors_details
                    ]
                else:
                    raise ValueError("patient and practitioner details are required.")

            encryption_payload["documentReferences"] = (
                validated_data.document_references
            )
            encryptedData = await self.utilities.encryption(payload=encryption_payload)

            payload = {
                "caseType": validated_data.case_type,
                "enableExtraction": validated_data.enable_extraction,
                "encryptedData": encryptedData,
            }

            if validated_data.record_id:
                payload["recordId"] = validated_data.record_id

            if validated_data.public_key:
                payload["publicKey"] = validated_data.public_key

            fhir_bundle_response: FhirBundleResponse = await self.post(
                AI_ENDPOINTS.GENERATE_FHIR_BUNDLE,
                payload,
                response_model=FhirBundleResponse,
            )

            return fhir_bundle_response.root

        except EhrApiError as e:
            self.logger.error(
                f"EHR API Error during FHIR bundle generation: {e.message}",
                exc_info=True,
            )
            raise
        except ValueError as e:
            self.logger.error(
                f"Validation error in FHIR bundle generation: {e}", exc_info=True
            )
            raise EhrApiError(str(e), 422) from e
        except Exception as error:
            error_message = str(error)
            self.logger.error(
                f"Unexpected error in generate_fhir_bundle: {error_message}",
                exc_info=True,
            )
            raise EhrApiError(
                "An unexpected error occurred while generating FHIR bundle: "
                f"{error_message}",
                500,
            ) from error
