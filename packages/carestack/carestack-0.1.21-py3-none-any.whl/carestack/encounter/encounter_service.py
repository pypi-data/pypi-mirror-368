import logging
from typing import Any, Optional

from dotenv import load_dotenv

from carestack.ai.ai_dto import DischargeSummaryResponse, FhirBundleResponse
from carestack.ai.ai_utils import AiUtilities
from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import AI_ENDPOINTS, CaseType
from carestack.encounter.dto.encounter_dto import (
    DoctorDetails,
    EncounterRequestDTO,
    PatientDetails,
)

load_dotenv()


class Encounter(BaseService):
    """
    Service for orchestrating healthcare encounter workflows, FHIR bundle and discharge summary generation.

    This service provides a unified interface to create FHIR bundles or discharge summaries based on provided encounter data.
    It handles validation, encryption, and orchestrates AI-powered healthcare processing endpoints.

    !!! note "Key Features"
        - Validates incoming encounter request data thoroughly.
        - Supports both file-based and payload-based FHIR bundle generation workflows.
        - Handles discharge summary generation from encrypted data.
        - Encrypts sensitive patient data and associated files before transmission.
        - Robust error handling with clear logging for diagnosis.

    Methods:
        create: Creates a FHIR bundle or discharge summary based on encounter data.
        generate_fhir_from_sections: Generates FHIR bundle from provided clinical sections (payload).
        generate_fhir_from_files: Generates FHIR bundle from case sheet files and optional lab reports.
        generate_discharge_summary: Calls AI endpoint to generate discharge summary.
        generate_fhir_bundle: Calls AI endpoint to generate FHIR bundle from extracted data and files.

    Args:
        config (ClientConfig): API credentials and settings for service initialization.

    Example:
        ```
        config = ClientConfig(
            api_base_url="https://api.example.com",
            api_key="your_api_key",
            api_secret="your_api_secret"
        )
        encounter_service = Encounter(config)
        request = EncounterRequestDTO(
            case_type=CaseType.OP_CONSULTATION,
            dto=OPConsultationDTO(payload=OPConsultationSections(...))
        )
        bundle = await encounter_service.create(request)
        print(bundle["resourceType"])
        ```
    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.utilities = AiUtilities()

    async def create(self, request_body: EncounterRequestDTO) -> dict[str, Any]:
        """
        Main entrypoint: creates a FHIR bundle or discharge summary for the given encounter data.

        Determines workflow: file-based (case sheets), section-based (payload), and manages
        FHIR bundle and summary extraction/encryption as required.

        Args:
            request_body (EncounterRequestDTO): All data for FHIR/document generation,
                including case type, files, payload, patient/practitioner info, etc.

        Returns:
            dict[str, Any]: Serialized FHIR-compliant bundle or discharge summary document.

        Raises:
            EhrApiError: On validation or any underlying process failure.

        Example:
            ```
            encounter_request = EncounterRequestDTO(
                caseType=CaseType.OP_CONSULTATION,
                dto=OPConsultationDTO(
                    caseSheets=None,
                    payload=OPConsultationSections(
                        patient_details=PatientDetails(name="John Doe", ...),
                        doctor_details=[DoctorDetails(name="Dr. Smith", ...)],
                        chief_complaints="Fever and cough",
                        physical_examination=PhysicalExamination(...),
                        ...
                    )
                ),
                lab_reports=None
            )

            or

            encounter_request = EncounterRequestDTO(
                caseType=CaseType.OP_CONSULTATION,
                lab_reports=["lab_report_1.pdf", "lab_report_2.pdf"],
                dto=InpatientDTO(
                    caseType=InpatientCaseType.SURGERY,
                    caseSheets=["case_sheet_1.pdf", "case_sheet_2.pdf"],
                ),
                lab_reports=["lab_report_1.pdf"]
            )

            response = await encounter_service.create(encounter_request)
            print(response)
            ```

        ### Response:
            Sample Output for the given example:
            {
                "resourceType": "Bundle",
                "type": "document",
                "entry": [ ...FHIR resources... ]
            }
        """
        try:
            case_type = request_body.case_type.value
            dto = request_body.dto.model_dump(by_alias=True, exclude_none=True)
            document_references = request_body.document_references or []
            enable_extraction = request_body.enable_extraction

            self._validate_request_data(
                dto, case_type, document_references, enable_extraction
            )

            if "payload" in dto and dto["payload"] is not None:
                return await self.generate_fhir_from_sections(
                    case_type,
                    enable_extraction,
                    dto["payload"],
                    document_references,
                    request_body.record_id,
                    request_body.patient_details,
                    request_body.doctors_details,
                )

            if dto.get("caseSheets"):
                return await self.generate_fhir_from_files(
                    case_type,
                    enable_extraction,
                    dto["caseSheets"],
                    document_references,
                    request_body.record_id,
                    request_body.patient_details,
                    request_body.doctors_details,
                )

            raise ValueError("Unexpected state in encounter creation.")

        except EhrApiError as e:
            self.logger.error(
                f"EHR API error in FHIR bundle generation: {e.message}", exc_info=True
            )
            raise
        except ValueError as e:
            self.logger.error(
                f"Validation error in FHIR bundle generation: {e}", exc_info=True
            )
            raise EhrApiError(str(e), 422) from e
        except Exception as error:
            self.logger.error(
                f"Unexpected error in generate_fhir_bundle: {error}", exc_info=True
            )
            raise EhrApiError(
                f"An unexpected error occurred while generating FHIR bundle: {error}",
                500,
            ) from error

    def _validate_document_references(
        self,
        case_type: str,
        document_references: Optional[list[str]],
        enable_extraction: bool,
    ) -> None:
        doc_count = len(document_references or [])
        print(
            f"DEBUG: case_type={case_type}, ref_count={doc_count}, enable_extraction={enable_extraction}"
        )

        # Set max limits (same for both true/false)
        max_limits: dict[str, Optional[int]] = {
            "Prescription": 1,
            "Diagnostic Report": 2,
            "Discharge Summary": None,
            "OP Consultation": None,
            "Immunization Record": None,
            "Wellness Record": None,
            "Health Document Record": None,
        }

        # Set min limits based on extraction
        if enable_extraction:
            min_limits: dict[str, int] = {
                "Prescription": 0,
                "Diagnostic Report": 1,
                "Discharge Summary": 0,
                "OP Consultation": 0,
                "Immunization Record": 0,
                "Wellness Record": 0,
                "Health Document Record": 1,
            }

        else:
            min_limits = {key: 1 for key in max_limits.keys()}

        min_required = min_limits.get(case_type, 0)
        max_allowed = max_limits.get(case_type, None)

        # Validate min
        if doc_count < min_required:
            raise ValueError(
                f"{case_type} requires at least {min_required} document reference(s) when extraction is {'disabled' if not enable_extraction else 'enabled'}."
            )

        # Validate max (if specified)
        if max_allowed is not None and doc_count > max_allowed:
            raise ValueError(
                f"{case_type} allows at most {max_allowed} document reference(s). Provided: {doc_count}."
            )

    def _validate_request_data(
        self,
        dto: dict[str, Any],
        case_type: str,
        document_references: Optional[list[str]],
        enable_extraction: bool,
    ) -> None:
        """
        Validates that the request contains the necessary data.

        Args:
            dto (dict[str, Any]): The DTO dictionary to validate.

        Raises:
            ValueError: If both caseSheets and payload are missing or empty.

        Example:
            _validate_request_data({"payload": ..., "caseSheets": ...})
        """
        has_case_sheets = bool(dto.get("caseSheets"))
        has_payload = "payload" in dto and dto["payload"] is not None

        if not has_case_sheets and not has_payload:
            raise ValueError("No case_sheets or payload provided for the encounter.")
        self._validate_document_references(
            case_type, document_references, enable_extraction
        )

    async def generate_discharge_summary(
        self, case_type: str, encrypted_data: str
    ) -> DischargeSummaryResponse:
        """
        Generates a discharge summary from encrypted case sheet data.

        Args:
            case_type (str): The caseType for AI endpoint (e.g., 'inpatient').
            encrypted_data (str): Encryption result for case sheets.

        Returns:
            DischargeSummaryResponse: Extracted summary with meta data.

        Raises:
            EhrApiError: On API or process failures.

        Example:
            summary = await encounter_service._generate_discharge_summary("inpatient", encrypted_files)
            print(summary.dischargeSummary)
        """
        try:
            discharge_payload = {
                "caseType": case_type,
                "encryptedData": encrypted_data,
            }
            return await self.post(
                AI_ENDPOINTS.GENERATE_DISCHARGE_SUMMARY,
                discharge_payload,
                response_model=DischargeSummaryResponse,
            )
        except EhrApiError:
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error generating discharge summary: {e}", exc_info=True
            )
            raise EhrApiError(
                f"An unexpected error occurred while generating discharge summary: {e}",
                500,
            ) from e

    async def generate_fhir_from_files(
        self,
        case_type: str,
        enable_extraction: bool,
        case_sheets: list[str],
        document_references: list[str],
        record_id: Optional[str] = None,
        patient_details: Optional[PatientDetails] = None,
        doctor_details: Optional[list[DoctorDetails]] = None,
    ) -> dict[str, Any]:
        """
        Generates a FHIR bundle from provided case sheet files and any document references.

        Workflow:
        1. Optionally encrypts document references (lab reports, scans, etc)
        2. If extraction enabled:
            a. Encrypts case sheets.
            b. Extracts discharge summary & data.
            c. Encrypts extracted summary data for FHIR.
        3. If extraction disabled: requires patient and practitioner details.

        Args:
            case_type (str): Case type code.
            enable_extraction (bool): Whether to extract summary from the files.
            case_sheets (list[str]): Source case files (URLs, filenames, etc).
            document_references (list[str]): Any supporting doc refs (base64-encoded files).
            patient_details (Optional[PatientDetails]): Demographic data, if used.
            doctor_details (Optional[list[DoctorDetails]]): Provider/practitioner data, if used.

        Returns:
            dict[str, Any]: The parsed FHIR-compliant document.

        Raises:
            EhrApiError: On API/encryption/validation failure.

        Example:
            ```
            bundle = await encounter_service._generate_fhir_from_files(
                case_type="SURGERY",
                enable_extraction=True,
                case_sheets=["cs1.pdf", "cs2.pdf"],
                document_references=["lab1.pdf"],
                patient_details=details,
                doctor_details=[doctor],
            )
            print(bundle["resourceType"])

        ### Response:
            {
                "resourceType": "Bundle",
                "type": "document",
                "entry": [ ...FHIR resources... ]
            }
            ```
        """
        try:
            # Step 1: if enable_extraction is true encrypt the case sheets and call the _generate_discharge_summary method to extract data
            fhir_payload: Any = {"caseType": case_type}
            encryption_payload: dict[str, Any] = {}
            fhir_payload["enableExtraction"] = enable_extraction

            if document_references:
                encryption_payload["documentReferences"] = document_references

            if enable_extraction:
                encrypted_case_sheets_resp = await self.utilities.encryption(
                    payload={"files": case_sheets}
                )
                casesheet_info = await self.generate_discharge_summary(
                    case_type, encrypted_case_sheets_resp
                )
                encryption_payload["extractedData"] = casesheet_info.extracted_data
                fhir_payload["recordId"] = casesheet_info.id
            else:
                if patient_details and doctor_details:

                    encryption_payload["patientDetails"] = patient_details.model_dump(
                        by_alias=True
                    )
                    encryption_payload["practitionersDetails"] = [
                        doc.model_dump(by_alias=True) for doc in doctor_details
                    ]
                    fhir_payload["recordId"] = record_id
                else:
                    raise ValueError(
                        "Invalid patient or practitioner details provided."
                    )

            encrypted_data = await self.utilities.encryption(payload=encryption_payload)
            fhir_payload["encryptedData"] = encrypted_data

            fhir_response = await self.post(
                AI_ENDPOINTS.GENERATE_FHIR_BUNDLE,
                fhir_payload,
                response_model=FhirBundleResponse,
            )
            return fhir_response.root
        except EhrApiError:
            raise
        except ValueError as e:
            self.logger.error(
                f"Validation error while generating FHIR from files: {e}", exc_info=True
            )
            raise EhrApiError(
                f"Invalid data for generating FHIR from files: {e}", 422
            ) from e
        except Exception as e:
            self.logger.error(
                f"Unexpected error generating FHIR from files: {e}", exc_info=True
            )
            raise EhrApiError(
                f"An unexpected error occurred while generating FHIR from files: {e}",
                500,
            ) from e

    async def generate_fhir_from_sections(
        self,
        case_type: str,
        enabled_extraction: bool,
        sections: dict[str, Any],
        document_references: list[str] = [],
        record_id: Optional[str] = None,
        patient_details: Optional[PatientDetails] = None,
        doctor_details: Optional[list[DoctorDetails]] = None,
    ) -> dict[str, Any]:
        """
        Generates a FHIR-compliant bundle using provided section (payload) data and optional supporting docs.

        When extraction is enabled, the entire sections/payload dict is encrypted and included in the FHIR call.
        When disabled, requires explicit patient and practitioner metadata.

        Args:
            case_type (str): Encounter/case type.
            enabled_extraction (bool): Whether to encrypt/process sections for extraction.
            sections (dict): Clinical sections, e.g. consultation notes, as dict.
            document_references (list[str]): Doc references (e.g. lab reports).
            patient_details (Optional[PatientDetails]): Patient metadata, required if extraction is off.
            doctor_details (Optional[list[DoctorDetails]]): Provider metadata, required if extraction is off.

        Returns:
            dict: FHIR-compliant bundle resource.

        Raises:
            EhrApiError: On validation or API failure.

        Example:
            ```
            bundle = await encounter_service._generate_fhir_from_sections(
                case_type="OP_CONSULTATION",
                enabled_extraction=True,
                sections=payload,
                document_references=[],
                patient_details=details,
                doctor_details=[doctor],
            )
        ### Response:
            {
                "resourceType": "Bundle",
                "type": "document",
                "entry": [ ...FHIR resources... ]
            }
            ```
        """
        try:
            fhir_payload = {
                "caseType": case_type,
                "enableExtraction": enabled_extraction,
                "recordId": record_id,
            }
            encryption_payload: dict[str, Any] = {}

            if document_references:
                encryption_payload["documentReferences"] = document_references

            if patient_details and doctor_details:
                encryption_payload["patientDetails"] = patient_details.model_dump(
                    by_alias=True
                )
                encryption_payload["practitionersDetails"] = [
                    doc.model_dump(by_alias=True) for doc in doctor_details
                ]
            else:
                raise ValueError("patient and practitioners details are required.")

            if enabled_extraction:
                encryption_payload["extractedData"] = sections.copy()

            fhir_payload["encryptedData"] = await self.utilities.encryption(
                payload=encryption_payload
            )
            fhir_response = await self.post(
                AI_ENDPOINTS.GENERATE_FHIR_BUNDLE,
                fhir_payload,
                response_model=FhirBundleResponse,
            )
            return fhir_response.root
        except EhrApiError:
            raise
        except ValueError as e:
            self.logger.error(
                f"Validation error while generating FHIR from sections: {e}",
                exc_info=True,
            )
            raise EhrApiError(
                f"Invalid data for generating FHIR from sections: {e}", 422
            ) from e
        except Exception as e:
            self.logger.error(
                f"Unexpected error generating FHIR from sections: {e}", exc_info=True
            )
            raise EhrApiError(
                f"An unexpected error occurred while generating FHIR from sections: {e}",
                500,
            ) from e
