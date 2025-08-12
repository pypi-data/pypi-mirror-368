from enum import Enum


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class PatientIdTypeEnum(Enum):
    ABHA = "ABHA"
    AADHAAR = "AADHAAR"
    PAN = "PAN"
    DRIVING_LICENSE = "DRIVING_LICENSE"


class PatientTypeEnum(Enum):
    OLD = "OLD"
    NEW = "NEW"


class StatesAndUnionTerritories(Enum):
    ANDHRA_PRADESH = "Andhra Pradesh"
    ARUNACHAL_PRADESH = "Arunachal Pradesh"
    ASSAM = "Assam"
    BIHAR = "Bihar"
    CHATTISGARH = "Chattisgarh"
    GOA = "Goa"
    GUJARAT = "Gujarat"
    HARYANA = "Haryana"
    HIMACHAL_PRADESH = "Himachal Pradesh"
    JHARKHAND = "Jharkhand"
    KARNATAKA = "Karnataka"
    KERALA = "Kerala"
    MADHYA_PRADESH = "Madhya Pradesh"
    MAHARASHTRA = "Maharashtra"
    MANIPUR = "Manipur"
    MEGHALAYA = "Meghalaya"
    MIZORAM = "Mizoram"
    NAGALAND = "Nagaland"
    ODISHA = "Odisha"
    PUNJAB = "Punjab"
    RAJASTHAN = "Rajasthan"
    SIKKIM = "Sikkim"
    TAMIL_NADU = "Tamil Nadu"
    TELANGANA = "Telangana"
    TRIPURA = "Tripura"
    UTTAR_PRADESH = "Uttar Pradesh"
    UTTARAKHAND = "Uttarakhand"
    WEST_BENGAL = "West Bengal"
    ANDAMAN_AND_NICOBAR = "Andaman and Nicobar"
    LAKSHADWEEP = "Lakshadweep"
    DELHI = "Delhi"
    DADRA_HAVELI = "Dadra and Nagar Haveli and Daman & Diu"
    JAMMU_AND_KASHMIR = "Jammu and Kashmir"
    CHANDIGARH = "Chandigarh"
    LADAKH = "Ladakh"
    PUDUCHERRY = "Puducherry"
    UNKNOWN = "Unknown"


class ResourceType(Enum):
    ALLERGY_INTOLERANCE = "AllergyIntolerance"
    APPOINTMENT = "Appointment"
    MEDICATION_REQUEST = "MedicationRequest"
    MEDICATION_STATEMENT = "MedicationStatement"
    DOCUMENT_REFERENCE = "DocumentReference"
    OBSERVATION = "Observation"
    PATIENT = "Patient"
    BINARY = "Binary"
    BUNDLE = "Bundle"
    CARE_PLAN = "CarePlan"
    COMPOSITION = "Composition"
    CONDITION = "Condition"
    ENCOUNTER = "Encounter"
    FAMILY_MEMBER_HISTORY = "FamilyMemberHistory"
    IMAGING_STUDY = "ImagingStudy"
    IMMUNIZATION = "Immunization"
    IMMUNIZATION_RECOMMENDATION = "ImmunizationRecommendation"
    MEDIA = "Media"
    ORGANIZATION = "Organization"
    PRACTITIONER = "Practitioner"
    PRACTITIONER_ROLE = "PractitionerRole"
    PROCEDURE = "Procedure"
    SERVICE_REQUEST = "ServiceRequest"
    SPECIMEN = "Specimen"
    STAFF = "Staff"
    CONSENT = "Consent"
    CARE_CONTEXT = "CareContext"
    HIU_HEALTH_BUNDLE = "HiuHealthBundle"
    LOCATION = "Location"
    COVERAGE = "Coverage"
    COVERAGE_ELIGIBILITY_REQUEST = "CoverageEligibilityRequest"
    COVERAGE_ELIGIBILITY_RESPONSE = "CoverageEligibilityResponse"
    CLAIM = "Claim"
    CLAIM_RESPONSE = "ClaimResponse"
    COMMUNICATION_REQUEST = "CommunicationRequest"
    COMMUNICATION = "Communication"
    PAYMENT_NOTICE = "PaymentNotice"
    PAYMENT_RECONCILIATION = "PaymentReconciliation"
    TASK = "Task"
    INSURANCE_PLAN = "InsurancePlan"


class ConsentType(Enum):
    RECEIVED = "Received"
    REQUESTED = "Requested"


class Departments(Enum):
    UROLOGY = "urology"
    NEUROLOGY = "neurology"
    RADIOLOGY = "radiology"
    CARDIOLOGY = "cardiology"
    GENERAL_SURGERY = "general surgery"
    ENDOCRINOLOGY = "endocrinology"
    PEDIATRICS = "pediatrics"
    PATHOLOGY = "pathology"
    NEPHROLOGY = "nephrology"
    DERMATOLOGY = "dermatology"
    OTORHINOLARYNGOLOGY = "otorhinolaryngology"
    OPHTHALMOLOGY = "ophthalmology"
    EMERGENCY_MEDICINE = "emergency medicine"
    ORTHOPEDICS = "orthopedics"
    PSYCHIATRY = "psychiatry"
    ANESTHESIOLOGY = "anesthesiology"
    GASTROENTEROLOGY = "gastroenterology"
    INTENSIVE_CARE_MEDICINE = "intensive care medicine"
    FAMILY_MEDICINE = "family medicine"
    GYNAECOLOGY = "gynaecology"
    HEMATOLOGY = "hematology"


class Country(Enum):
    INDIA = "India"


class HealthFacilityType(Enum):
    HIP = "HIP"
    HIU = "HIU"


class OrganizationsIdType(Enum):
    ACCOUNT_ID = "accountId"
    ORGANIZATION_ID = "facilityId"
    ID = "id"


class AbhaLoginHint(str, Enum):
    ABHA_NUMBER = "abha-number"
    MOBILE = "mobile"
    EMAIL = "email"
    AADHAAR = "aadhaar"
    PASSWORD = "password"
    INDEX = "index"


class AuthMethodV2(str, Enum):
    AADHAAR_OTP = "AADHAAR_OTP"
    MOBILE_OTP = "MOBILE_OTP"
    PASSWORD = "PASSWORD"
    DEMOGRAPHICS = "DEMOGRAPHICS"
    AADHAAR_BIO = "AADHAAR_BIO"
    EMAIL_OTP = "EMAIL_OTP"


class VerifyAbhaLoginAuthResult(str, Enum):
    FAILED = "failed"
    SUCCESS = "success"


class PatientEndpoints:
    GET_ALL_PATIENTS = "/get/Patient"
    GET_PATIENT_BY_ID = "/get/Patient/{patient_id}"
    PATIENT_EXISTS = "/get/Patient/{patient_id}"
    CREATE_PATIENT = "/add/Patient"
    UPDATE_PATIENT = "/update/Patient"
    GET_PATIENT_BY_FILTERS = "/health-lake/get-profiles/Patient"
    DELETE_PATIENT = "/health-lake/delete/Patient/{patient_id}"


class PractitionerEndPoints:
    GET_ALL_PRACTITIONERS = "/get/Practitioner"
    GET_PRACTITIONER_BY_ID = "/get/Practitioner/{practitioner_id}"
    PRACTITIONER_EXISTS = "/get/Practitioner/{practitioner_id}"
    CREATE_PRACTITIONER = "/add/Practitioner"
    UPDATE_PRACTITIONER = "/update/Practitioner"
    GET_PRACTITIONER_BY_FILTERS = "/health-lake/get-profiles/Practitioner"
    DELETE_PRACTITIONER = "/health-lake/delete/Practitioner/{practitioner_id}"


class OrganizationEndPoints:
    GET_ALL_ORGANIZATIONS = "/facilities/"
    GET_ORGANIZATION_BY_ID = "/facilities/{search_param}/{search_term}"
    ORGANIZATION_EXISTS = "/facilities/{search_param}/{search_term}"
    REGISTER_ORGANIZATION = "/register-facility"
    UPDATE_ORGANIZATION = "/update-facility"
    SEARCH_ORGANIZATION = "/search-facility"
    DELETE_ORGANIZATION = "/facility/{organization_id}"


class AppointmentEndpoints:
    ADD_APPOINTMENT = "/add/Appointment"
    GET_ALL_APPOINTMENTS = "/get/Appointment"
    GET_APPOINTMENT_BY_ID = "/get/Appointment/{reference}"
    APPOINTMENT_EXISTS = "/get/Appointment/{reference}"
    UPDATE_APPOINTMENT = "/update/Appointment"
    DELETE_APPOINTMENT = "/delete/Appointment/{reference}"
    GET_APPOINTMENT_BY_FILTERS = "/health-lake/get-profiles/Appointment"


class API_ENDPOINTS:
    ADD_APPOINTMENT = "/add/Appointment"
    CREATE_CARE_CONTEXT = "/abdm-flows/create-carecontext"
    UPDATE_VISIT_RECORDS = "/abdm-flows/update-visit-records"
    LINK_CARE_CONTEXT = "/abdm-flows/link-carecontext"


class UTILITY_API_ENDPOINTS:
    STATES_AND_DISTRICTS = "/lgd-states"
    SUBDISTRICTS = "/lgd-subdistricts?districtCode={district_code}"
    LOCATION = "https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={api_key}"
    OWNER_SUBTYPE = "/owner-subtype"
    SPECIALITIES = "/specialities"
    ORGANIZATION_TYPE = "/facility-type"
    ORGANIZATION_SUBTYPE = "/facility-subtypes"
    MASTER_TYPES = "/master-types"
    MASTER_DATA_BY_TYPE = "/master-data/{type}"


class HPR_API_ENDPOINTS:
    GENERATE_AADHAAR_OTP = "/aadhaar/generateOtp"
    VERIFY_AADHAAR_OTP = "/aadhaar/verifyOtp"
    CHECK_ACCOUNT_EXIST = "/check/account-exist"
    DEMOGRAPHIC_AUTH_MOBILE = "/demographic-auth/mobile"
    GENERATE_MOBILE_OTP = "/generate/mobileOtp"
    VERIFY_MOBILE_OTP = "/verify/mobileOtp"
    GET_HPR_SUGGESTION = "/hpId/suggestion"
    CREATE_HPR_ID_WITH_PREVERIFIED = "/hprId/create"


class HprRegistrationSteps(str, Enum):
    GENERATE_AADHAAR_OTP = "generate_aadhaar_otp"
    VERIFY_AADHAAR_OTP = "verify_aadhaar_otp"
    CHECK_ACCOUNT_EXIST = "check_account_exist"
    DEMOGRAPHIC_AUTH_VIA_MOBILE = "demographic_auth_via_mobile"
    GENERATE_MOBILE_OTP = "generate_mobile_otp"
    VERIFY_MOBILE_OTP = "verify_mobile_otp"
    GET_HPR_ID_SUGGESTION = "get_hpr_id_suggestion"
    CREATE_HPR_ID_WITH_PREVERIFIED = "create_hpr_id_with_preverified"


class CREATE_ABHA_ENDPOINTS:
    GENERATE_AADHAAR_OTP = "/patient/registration/abha/aadhaar/request-otp"
    ENROLL_WITH_AADHAAR = "/patient/registration/abha/aadhaar/enroll"
    GENERATE_MOBILE_OTP = "/patient/registration/abha/update/mobile/request-otp"
    VERIFY_MOBILE_OTP = "/patient/registration/abha/update/mobile/verify-otp"
    ABHA_ADDRESS_SUGGESTION = "/patient/registration/abha/address-suggestions"
    CREATE_ABHA = "/patient/registration/abha/abha-address"


class AbhaSteps(str, Enum):
    GENERATE_AADHAAR_OTP = "generate_aadhaar_otp"
    ENROLL_WITH_AADHAAR = "enroll_with_aadhaar"
    GENERATE_MOBILE_OTP = "generate_mobile_otp"
    VERIFY_MOBILE_OTP = "verify_mobile_otp"
    ABHA_ADDRESS_SUGGESTION = "abha_address_suggestion"
    CREATE_ABHA_ADDRESS = "create_abha_address"


class DOCUMENT_LINKING_ENDPOINTS:
    ENTITY_EXTRACTION = "/entity/extraction"
    CREATE_CARE_CONTEXT = "/abdm-flows/create-carecontext"
    UPDATE_VISIT_RECORDS = "/abdm-flows/update-visit-records"
    LINK_CARE_CONTEXT = "/abdm-flows/link-carecontext"


class AI_ENDPOINTS:
    GENERATE_FHIR_BUNDLE = "/demo/generate-fhir-bundle"
    GENERATE_DISCHARGE_SUMMARY = "/demo/generate-discharge-summary"


class GeneralInfoOptions(Enum):
    HAS_DIALYSIS_CENTER = "hasDialysisCenter"
    HAS_PHARMACY = "hasPharmacy"
    HAS_BLOOD_BANK = "hasBloodBank"
    HAS_CATH_LAB = "hasCathLab"
    HAS_DIAGNOSTIC_LAB = "hasDiagnosticLab"
    HAS_IMAGING_CENTER = "hasImagingCenter"


class AppointmentPriority(Enum):
    EMERGENCY = "Emergency"
    FOLLOW_UP_VISIT = "Follow-up visit"
    NEW = "New"


class AuthMode(Enum):
    MOBILE_OTP = "MOBILE_OTP"
    AADHAAR_OTP = "AADHAAR_OTP"
    DEMOGRAPHICS = "DEMOGRAPHICS"
    DIRECT = "DIRECT"


class CarePlanIntent(Enum):
    PROPOSAL = "proposal"
    PLAN = "plan"
    ORDER = "order"
    OPTION = "option"


class CarePlanStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    REVOKED = "revoked"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ClinicalStatus(Enum):
    ACTIVE = "active"
    RECURRENCE = "recurrence"
    RELAPSE = "relapse"
    INACTIVE = "inactive"
    REMISSION = "remission"
    RESOLVED = "resolved"


class DiagnosticReportStatus(Enum):
    REGISTERED = "registered"
    PARTIAL = "partial"
    PRELIMINARY = "preliminary"
    FINAL = "final"


class DosageFrequency(Enum):
    ONCE = "Once"
    TWICE = "Twice"
    THRICE = "Thrice"
    QUADTUPLE = "Quadtuple"


class MedicationRoute(Enum):
    ORAL = "Oral"
    TOPICAL = "Topical"
    INTRAVENOUS = "Intravenous"
    INTRAMUSCULAR = "IntraMuscular"
    SUBCUTANEOUS = "Subcutaneous"
    INHALATION = "Inhalation"
    INTRANASAL = "Intranasal"
    RECTAL = "Rectal"
    SUBLINGUAL = "Sublingual"
    BUCCAL = "Buccal"
    IV = "IntraVenal"


class MedicationMethod(Enum):
    SWALLOW = "Swallow"


class HealthInformationTypes(Enum):
    OPCONSULTATION = "OPConsultation"
    PRESCRIPTION = "Prescription"
    DISCHARGE_SUMMARY = "DischargeSummary"
    DIAGNOSTIC_REPORT = "DiagnosticReport"
    IMMUNIZATION_RECORD = "ImmunizationRecord"
    HEALTHDOCUMENT_RECORD = "HealthDocumentRecord"
    WELLNESS_RECORD = "WellnessRecord"


class CaseType(Enum):
    DISCHARGE_SUMMARY = "Discharge Summary"
    RADIOLOGY_REPORT = "Radiology Report"
    OP_CONSULTATION = "OP Consultation"
    Prescription = "Prescription"
    DiagnosticReport = "Diagnostic Report"
    ImmunizationRecord = "Immunization Record"
    HealthDocumentRecord = "Health Document Record"
    WellnessRecord = "Wellness Record"


class ImmunizationStatusEnum(Enum):
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    NOT_DONE = "not-done"


class MedicationRequestStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    REVOKED = "revoked"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"
    CANCELLED = "cancelled"


class MedicationStatementStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    INTENDED = "intended"
    STOPPED = "stopped"
    ON_HOLD = "on-hold"
    UNKNOWN = "unknown"
    NOT_TAKEN = "not-taken"


class ObservationStatus(Enum):
    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ProcedureStatus(Enum):
    PREPARATION = "preparation"
    IN_PROGRESS = "in-progress"
    NOT_DONE = "not-done"
    ON_HOLD = "on-hold"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ServiceRequestStatus(Enum):
    PROPOSAL = "proposal"
    PLAN = "plan"
    DIRECTIVE = "directive"
    ORDER = "order"
    ORIGINAL_ORDER = "original-order"
    REFLEX_ORDER = "reflex-order"
    FILLER_ORDER = "filler-order"
    INSTANCE_ORDER = "instance-order"
    OPTION = "option"


class ServiceRequestIntent(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    REVOKED = "revoked"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class VerificationStatus(Enum):
    UNCONFIRMED = "unconfirmed"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"
    ENTERED_IN_ERROR = "entered-in-error"


VITALS_REFERENCE_RANGES = {
    "bloodPressure": {
        "mmHg": {
            "systolic": {"low": 90, "high": 120},
            "diastolic": {"low": 60, "high": 80},
        }
    },
    "heartRate": {"bpm": {"low": 60, "high": 100}},
    "respiratoryRate": {"breaths/min": {"low": 12, "high": 20}},
    "temperature": {
        "°F": {"low": 97.0, "high": 99.5},
        "°C": {"low": 36.1, "high": 37.5},
    },
    "oxygenSaturation": {"%": {"low": 95, "high": 100}},
    "height": {
        "cm": {"low": 140, "high": 200},
        "m": {"low": 1.4, "high": 2.0},
        "in": {"low": 55, "high": 79},
    },
    "weight": {"kg": {"low": 40, "high": 120}, "lb": {"low": 88, "high": 265}},
}
