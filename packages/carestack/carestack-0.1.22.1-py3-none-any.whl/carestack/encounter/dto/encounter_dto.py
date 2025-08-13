from typing import Any, Optional, Union
from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator
from carestack.common.enums import CaseType, Gender
from carestack.common.error_validation import check_not_empty
from pydantic import ConfigDict


class VitalSign(BaseModel):
    """
    Represents a single vital sign measurement.

    Attributes:
       value (str): The value of the vital sign.
       unit (str): The unit of the vital sign.
    """

    model_config = ConfigDict(populate_by_name=True)
    value: str = Field(..., description="The value of the vital sign.")
    unit: str = Field(..., description="The unit of the vital sign.")

    @field_validator("value", "unit")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class MedicalHistoryItem(BaseModel):
    """
    Represents a single item in the patient's medical history.

    Attributes:
        condition (Optional[str]): A medical condition in the patient's history.
        procedure (Optional[str]): A medical procedure in the patient's history.
    """

    model_config = ConfigDict(populate_by_name=True)
    condition: Optional[str] = Field(
        None, description="A medical condition in the patient's history."
    )
    procedure: Optional[str] = Field(
        None, description="A medical procedure in the patient's history."
    )

    @field_validator("condition", "procedure")
    @classmethod
    def _validate_fields(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        """Validates that condition and procedure is not empty if provided."""
        if v is not None:
            return check_not_empty(v, info.field_name)
        return v


class FamilyHistoryItem(BaseModel):
    """
    Represents a single item in the patient's family history.

    Attributes:
        relation (str): The relation to the patient.
        condition (str): The medical condition of the relative.
    """

    relation: str = Field(..., description="The relation to the patient.")
    condition: str = Field(..., description="The medical condition of the relative.")

    @field_validator("relation", "condition")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class ProcedureItem(BaseModel):
    """
    Represents a single procedure performed on the patient.

    Attributes:
        description (str): Description of the procedure.
        complications (Optional[str]): Any complications during the procedure.
    """

    model_config = ConfigDict(populate_by_name=True)
    description: str = Field(..., description="Description of the procedure.")
    complications: Optional[str] = Field(
        None, description="Any complications during the procedure."
    )

    @field_validator("description", "complications")
    @classmethod
    def _validate_fields(cls, v: str, info: ValidationInfo) -> str:
        """Validates that required fields are not empty."""
        return check_not_empty(v, info.field_name)


class InvestigationItem(BaseModel):
    """
    Represents a single investigation record.

    Attributes:
        observations (list[str]): Observed vital signs.
        status (str): Status of the investigation.
        recordedDate (str): Date when the investigation was recorded.
    """

    model_config = ConfigDict(populate_by_name=True)
    observations: list[str] = Field(
        ...,
        description="List of observations in the investigation. Each observation should contain test name, value, and unit.",
    )
    status: str
    recorded_date: str = Field(..., alias="recordedDate")


class LabReportItem(BaseModel):
    """
    Represents a single lab report.

    Attributes:
        observations (list[str]): Observed vital signs.
        status (str): Status of the lab report.
        recordedDate (str): Date when the lab report was recorded.
        category (str): Category of the lab report.
        conclusion (str): Conclusion of the lab report.
    """

    model_config = ConfigDict(populate_by_name=True)
    observations: list[str] = Field(
        ...,
        description="List of observations in the lab report.each observation should contain test name, value, and unit.",
    )
    status: str
    recorded_date: str = Field(..., alias="recordedDate")
    category: str
    conclusion: str


class PatientDetails(BaseModel):
    """
    Represents patient demographic and admission details.

    Attributes:
        first_name (str): Patient's first name.
        middle_name (Optional[str]): Patient's middle name.
        last_name (str): Patient's last name.
        birth_date (str): Patient's date of birth in ISO format (YYYY-MM-DD).
        gender (Gender): Patient's gender, represented as an enum.
        mobile_number (str): Patient's mobile number.
        email_id (Optional[str]): Patient's email address.
        address (str): Patient's residential address.
        pincode (str): Patient's postal code.
        state (str): Patient's state of residence.
        wants_to_link_whatsapp (Optional[bool]): Indicates if the patient wants to link their WhatsApp number.
        photo (Optional[str]): Base64 encoded string of the patient's photo.
        id_number (str): Unique identifier for the patient (e.g., Aadhar number).
        id_type (str): Type of the ID number (e.g., "Aadhar", "PAN").
        abha_address (Optional[str]): ABHA address for the patient, if available.
        resource_id (Optional[str]): Resource ID for the patient in the system.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    first_name: str = Field(..., alias="firstName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    last_name: str = Field(..., alias="lastName")
    birth_date: str = Field(..., alias="birthDate")
    gender: Gender
    mobile_number: str = Field(..., alias="mobileNumber")
    email_id: Optional[str] = Field(None, alias="emailId")
    address: str
    pincode: str
    state: str
    wants_to_link_whatsapp: Optional[bool] = Field(None, alias="wantsToLinkWhatsapp")
    photo: Optional[str] = None
    id_number: str = Field(..., alias="idNumber")
    id_type: str = Field(..., alias="idType")
    abha_address: Optional[str] = Field(None, alias="abhaAddress")
    resource_id: Optional[str] = Field(None, alias="resourceId")


class DoctorDetails(BaseModel):
    """
    Represents doctor information.

    Attributes:
        first_name (str): Doctor's first name.
        middle_name (Optional[str]): Doctor's middle name.
        last_name (str): Doctor's last name.
        birth_date (str): Doctor's date of birth in ISO format (YYYY-MM-DD).
        gender (str): Doctor's gender, represented as an enum.
        mobile_number (str): Doctor's mobile number.
        email_id (Optional[str]): Doctor's email address.
        address (str): Doctor's residential address.
        pincode (str): Doctor's postal code.
        state (str): Doctor's state of residence.
        wants_to_link_whatsapp (Optional[bool]): Indicates if the doctor wants to link their WhatsApp number.
        photo (Optional[str]): Base64 encoded string of the doctor's photo.
        designation (str): Doctor's designation (e.g., "Cardiologist").
        joining_date (Optional[str]): Date when the doctor joined the organization in ISO format (YYYY-MM-DD).
        department (str): Department of the doctor (e.g., "Cardiology").
        registration_id (str): Doctor's registration ID.
        hpr_id (Optional[str]): HPR ID of the doctor, if available.
        resource_id (Optional[str]): Resource ID for the doctor in the system.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    first_name: str = Field(..., alias="firstName")
    middle_name: Optional[str] = Field(None, alias="middleName")
    last_name: str = Field(..., alias="lastName")
    birth_date: str = Field(..., alias="birthDate")
    gender: Gender
    mobile_number: str = Field(..., alias="mobileNumber")
    email_id: Optional[str] = Field(None, alias="emailId")
    address: str
    pincode: str
    state: str
    wants_to_link_whatsapp: Optional[bool] = Field(None, alias="wantsToLinkWhatsapp")
    photo: Optional[str] = None
    designation: str
    joining_date: Optional[str] = Field(None, alias="joiningDate")
    department: str
    registration_id: str = Field(..., alias="registrationId")
    hpr_id: Optional[str] = Field(None, alias="hprId")
    resource_id: Optional[str] = Field(None, alias="resourceId")


class CommonHealthInformationDTO(BaseModel):
    """
    Base DTO for common health information sections.

    Attributes:
        chief_complaints (str): The patient's chief complaints.
        physical_examination (str): Patient's physical examination.
        medical_history (Optional[list[MedicalHistoryItem]]): Patient's medical history.
        family_history (Optional[list[FamilyHistoryItem]]): Patient's family history.
        condtions (Optional[list[str]]): Patient's conditions.
        current_procedures (Optional[list[ProcedureItem]]): Patient's procedures.
        current_medications (Optional[list[str]]): Patient's medications.
        prescribed_medications (Optional[list[str]]): Patient's prescribed medications.
        allergies (Optional[list[str]]): Patient's allergies.
        immunizations (Optional[list[str]]): Patient's immunizations.
        advisory_notes (Optional[list[str]]): Patient's advisory notes.
        care_plan (Optional[list[str]]): Patient's care plan.
        follow_up (Optional[list[str]]): Patient's follow-up plan.
    """

    model_config = ConfigDict(populate_by_name=True)

    chief_complaints: str = Field(
        ..., alias="chiefComplaints", description="The patient's chief complaints."
    )
    physical_examination: str = Field(
        ...,
        alias="physicalExamination",
        description="The physical examination findings of the patient with the test name,value,unit.",
    )

    medical_history: Optional[list[MedicalHistoryItem]] = Field(
        None, alias="medicalHistory", description="Patient's medical history."
    )

    family_history: Optional[list[FamilyHistoryItem]] = Field(
        None, alias="familyHistory", description="Patient's family history."
    )

    condtions: Optional[list[str]] = Field(None, description="Patient's conditions.")

    current_procedures: Optional[list[ProcedureItem]] = Field(
        None, alias="currentProcedures", description="Patient's procedures."
    )
    current_medications: Optional[list[str]] = Field(
        None, alias="currentMedications", description="Patient's medications."
    )
    prescribed_medications: Optional[list[str]] = Field(
        None,
        alias="prescribedMedications",
        description="Patient's prescribed medications.",
    )
    allergies: Optional[list[str]] = Field(None, description="Patient's allergies.")
    immunizations: Optional[list[str]] = Field(
        None, alias="immunizations", description="Patient's immunizations."
    )
    advisory_notes: Optional[list[str]] = Field(
        None, alias="advisoryNotes", description="Patient's advisory notes."
    )
    care_plan: Optional[list[str]] = Field(
        None, alias="carePlan", description="Patient's care plan."
    )
    follow_up: Optional[list[str]] = Field(
        None, alias="followUp", description="Patient's follow-up plan."
    )


class OPConsultationSections(CommonHealthInformationDTO):
    """
    Represents the OP consultation section, inheriting common health information from CommonHealthInformationDTO.
    """

    pass


class DischargeSummarySections(CommonHealthInformationDTO):
    """
    Represents the discharge summary section, inheriting common health information.

    Attributes:
        investigations (InvestigationItem): Patient's investigations.
    """

    investigations: InvestigationItem = Field(
        ..., description="Patient's investigations."
    )


class PrescriptionSections(BaseModel):
    """
    Represents the prescription section.

    Attributes:
        prescribed_medications (list[str]): Patient's prescribed medications.
    """

    prescribed_medications: list[str] = Field(
        ...,
        alias="prescribedMedications",
        description="Patient's prescribed medications.",
    )


class WellnessRecordSections(BaseModel):
    """
    Represents the wellness record section.

    Attributes:
        vital_signs (Optional[list[str]]]): Patient's vital signs.
        body_measurements (Optional[list[str]]]): Patient's body measurements.
        physical_activities (Optional[list[str]]]): Patient's physical activities.
        women_health (Optional[list[str]]]): Women's health data.
        life_style (Optional[list[str]]]): Lifestyle data.
        others (Optional[list[str]]]): Other health data.
    """

    model_config = ConfigDict(populate_by_name=True)
    vital_signs: Optional[list[str]] = Field(None, alias="vitalSigns")
    body_measurements: Optional[list[str]] = Field(None, alias="bodyMeasurements")
    physical_activities: Optional[list[str]] = Field(None, alias="physicalActivities")
    women_health: Optional[list[str]] = Field(None, alias="womenHealth")
    life_style: Optional[list[str]] = Field(None, alias="lifeStyle")
    others: Optional[list[str]] = Field(None, alias="others")


class ImmunizationRecordSections(BaseModel):
    """
    Represents the immunization record section.

    Attributes:
        immunizations (list[str]): Patient's immunizations.
    """

    model_config = ConfigDict(populate_by_name=True)
    immunizations: list[str] = Field(..., description="Patient's immunizations.")


class DiagnosticReportSections(BaseModel):
    """
    Represents the diagnostic report section.

    Attributes:
        lab_reports (LabReportItem): Patient's lab reports.
    """

    model_config = ConfigDict(populate_by_name=True)
    lab_reports: LabReportItem = Field(..., description="Patient's lab reports.")


class OPConsultationDTO(BaseModel):
    """
    Data Transfer Object for OP Consultation.
    Attributes:
        case_sheets (Optional[list[str]]): List of case sheets associated with the patient.
        payload (Optional[OPConsultationSections]): The raw data for the OP consultation.
    """

    model_config = ConfigDict(populate_by_name=True)
    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[OPConsultationSections] = Field(
        None, alias="payload", description="Patient's raw data."
    )


class DischargeSummaryDTO(BaseModel):
    """
    Data Transfer Object for Discharge Summary.
    Attributes:
        case_sheets (Optional[list[str]]): List of case sheets associated with the patient.
        payload (Optional[DischargeSummarySections]): The raw data for the discharge summary.
    """

    model_config = ConfigDict(populate_by_name=True)
    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[DischargeSummarySections] = Field(
        None, alias="payload", description="Patient's raw data."
    )


class PrescriptionRecordDTO(BaseModel):
    """
    Data Transfer Object for Prescription Record.
    Attributes:
        case_sheets (Optional[list[str]]): List of case sheets associated with the patient.
        payload (Optional[PrescriptionSections]): The raw data for the prescription record.
    """

    model_config = ConfigDict(populate_by_name=True)
    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[PrescriptionSections] = Field(
        None, description="Patient's payload."
    )


class WellnessRecordDTO(BaseModel):
    """
    Data Transfer Object for Wellness Record.
    Attributes:
        case_sheets (Optional[list[str]]): List of case sheets associated with the patient.
        payload (Optional[WellnessRecordSections]): The raw data for the wellness record.
    """

    model_config = ConfigDict(populate_by_name=True)
    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[WellnessRecordSections] = Field(
        None, description="Patient's payload."
    )


class ImmunizationRecordDTO(BaseModel):
    """
    Data Transfer Object for Immunization Record.

    Attributes:
        case_sheets (Optional[list[str]]): List of case sheets associated with the patient.
        payload (Optional[ImmunizationRecordSections]): The raw data for the immunization record.
    """

    model_config = ConfigDict(populate_by_name=True)
    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[ImmunizationRecordSections] = Field(
        None, description="Patient's payload."
    )


class DiagnosticReportDTO(BaseModel):
    """
    Data Transfer Object for Diagnostic Report.
    Attributes:
        case_sheets (Optional[list[str]]): List of case sheets associated with the patient.
        payload (Optional[DiagnosticReportSections]): The raw data for the diagnostic report.
    """

    model_config = ConfigDict(populate_by_name=True)
    case_sheets: Optional[list[str]] = Field(
        None, description="Patient's case_sheets.", alias="caseSheets"
    )
    payload: Optional[DiagnosticReportSections] = Field(
        None, description="Patient's payload."
    )


class GenerateFhirFromExtractedDataDto(BaseModel):
    """
    Data Transfer Object for generating a FHIR bundle from extracted data.
    Attributes:
        case_type (str): The type of case (e.g., `OPConsultation`, `DischargeSummary`). Serialized as `caseType`.
        record_id (Optional[str]): Identifier for the record, if available. Serialized as `recordId`.
        extracted_data (dict[str, Any]): Extracted clinical data for the bundle.
        document_references (Optional[list[str]]): List of document references to be included in the bundle.
    """

    model_config = ConfigDict(populate_by_name=True)

    case_type: str = Field(..., alias="caseType")
    record_id: Optional[str] = Field(None, alias="recordId")

    extracted_data: dict[str, Any] = Field(..., alias="extractedData")
    document_references: Optional[list[str]] = Field([], alias="documentReferences")


class HealthDocumentRecordDTO(BaseModel):
    """
    Data Transfer Object for Health Document Record.
    Attributes:
        case_sheets (Optional[list[str]]): List of case sheets associated with the patient.
    """

    model_config = ConfigDict(populate_by_name=True)
    case_sheets: Optional[list[str]] = Field(None, description="Patient's case_sheets.")


HealthInformationDTOUnion = Union[
    OPConsultationDTO,
    DischargeSummaryDTO,
    PrescriptionRecordDTO,
    WellnessRecordDTO,
    ImmunizationRecordDTO,
    DiagnosticReportDTO,
    HealthDocumentRecordDTO,
]


class EncounterRequestDTO(BaseModel):
    """Data Transfer Object for Encounter Request.

    Attributes:
        case_type (str): The type of health information case (e.g., `OPConsultation`, `DischargeSummary`).
        enable_extraction (bool): Flag to enable data extraction from the provided documents.
        patient_details (PatientDetails): Patient's information.
        doctor_details (list[DoctorDetails]): List of doctors involved in the case.
        dto (HealthInformationDTOUnion): The health information data, which can be one of the specific DTOs.
        document_references (Optional[list[str]]): List of document references to be included in the request.

    """

    model_config = ConfigDict(populate_by_name=True)
    case_type: CaseType = Field(
        ..., alias="caseType", description="The type of health information case"
    )  # Changed from HealthInformationTypes

    enable_extraction: bool = Field(
        True,
        alias="enableExtraction",
        description="Enable extraction of health information.",
    )

    record_id: Optional[str] = Field(
        None,
        alias="recordId",
        description="Identifier for the record, if available.",
    )

    patient_details: Optional[PatientDetails] = Field(
        None, alias="patientDetails", description="Patient's information."
    )
    doctors_details: Optional[list[DoctorDetails]] = Field(
        None, alias="doctorsDetails", description="Doctor's information."
    )

    dto: HealthInformationDTOUnion = Field(
        ..., alias="dto", description="The health information data"
    )
    document_references: Optional[list[str]] = Field(
        None, alias="documentReferences", description="The document references"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_case_type_and_data(cls, values: Any):
        if isinstance(values, dict):
            case_type = values.get("case_type") or values.get("caseType")
            data = values.get("dto")

            if case_type and data:
                # Mapping of case types to their corresponding DTO classes
                health_information_dto_mapping = {
                    CaseType.OP_CONSULTATION.value: OPConsultationDTO,
                    CaseType.DISCHARGE_SUMMARY.value: DischargeSummaryDTO,
                    CaseType.Prescription.value: PrescriptionRecordDTO,
                    CaseType.WellnessRecord.value: WellnessRecordDTO,
                    CaseType.ImmunizationRecord.value: ImmunizationRecordDTO,
                    CaseType.DiagnosticReport.value: DiagnosticReportDTO,
                }

                expected_dto_class = health_information_dto_mapping.get(case_type)
                if expected_dto_class:
                    # Convert the data to the expected DTO class
                    try:
                        values["dto"] = expected_dto_class(**data)
                    except Exception as e:
                        raise ValueError(
                            f"Invalid data for {expected_dto_class.__name__}: {str(e)}"
                        )

            return values
