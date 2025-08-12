# Carestack Python SDK

A comprehensive Python SDK for integrating with Carestack's healthcare APIs, providing seamless access to electronic health records (EHR), AI-powered document generation, and healthcare professional registry services.

## Features

- **EHR Resource Management**: Patient, Practitioner, Organization, and Appointment operations
- **AI-Powered Healthcare**: Generate discharge summaries and FHIR bundles using AI
- **Document Linking**: Seamlessly link health documents and care contexts to the Patient's ABHA
- **FHIR Bundle Generation**: HL7 FHIR-compliant clinical documents
- **ABHA & HPR Workflows**: Streamlined healthcare identity management
- **Type Safety**: Built with Pydantic for robust data validation
- **Async Support**: Fully asynchronous operations for high performance

## Installation

Install the Carestack SDK using pip:

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install Carestack SDK
pip install carestack
```
## Configuration

The SDK requires a `ClientConfig` object with your API credentials:

```python
from carestack import ClientConfig

config = ClientConfig(
    api_key="your_api_key",                    # Your API key
    x_hpr_id="your_hpr_id" # Required for Organization operations
)
```

### Environment Variables (Recommended)

For security, store your credentials as environment variables:

```bash
export CARESTACK_API_KEY="your_api_key"
export CARESTACK_HPRID_AUTH="your_hpr_id"  # For HPR operations
```

Then load them in your code:

```python
import os
from carestack import ClientConfig

config = ClientConfig(
    api_key=os.getenv("CARESTACK_API_KEY"),
    x_hpr_id=os.getenv("CARESTACK_HPRID_AUTH")  # Required for Organization operations
)
```

## Quick Start

Here's a complete example to get you started:

```python
import asyncio
from carestack import ClientConfig, Patient

async def main():
    # Configure the SDK
    config = ClientConfig(
        api_key="your_api_key",
        x_hpr_id="your_hpr_id" # Required for Organization operations
    )
    
    # Initialize patient service
    patient_service = Patient(config)
    
    # Create a new patient
    patient_data = {
        "idNumber": "123456789012",
        "idType": "Aadhaar",
        "patientType": "OPD",
        "firstName": "John",
        "lastName": "Doe",
        "birthDate": "1980-01-01",
        "gender": "M",
        "address": "123 Main Street",
        "mobileNumber": "+919876543210",
        "emailId": "john.doe@example.com",
        "resourceType": "PATIENT"
    }
    
    try:
        # Create patient
        created_patient = await patient_service.create(patient_data)
        print(f"Patient created successfully: {created_patient.message}")
        
        # Fetch all patients
        patients = await patient_service.find_all()
        
        # Find specific patient
        if patients.patients:
            patient_id = patients.patients[0].id
            patient = await patient_service.find_by_id(patient_id)
            
    except Exception as e:
        print(f"Error: {e}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
```


## Services Overview

The SDK provides the following main services:

### Core EHR Services
| Service | Description | Key Operations |
|---------|-------------|----------------|
| **Patient** | Manage patient records and demographics | Create, Read, Update, Delete, Search |
| **Practitioner** | Handle healthcare provider information | CRUD operations, HPR integration |
| **Organization** | Manage healthcare facilities | Organization registry, master data |
| **Appointment** | Schedule and manage appointments | Booking, updates, availability |

### AI & Document Services
| Service | Description | Key Operations |
|---------|-------------|----------------|
| **AiService** | AI-powered document generation | Discharge summaries, FHIR bundles |
| **DocumentLinking** | Link health documents with care contexts | Multi-step workflow orchestration |
| **Encounter** | Healthcare encounter workflows | FHIR generation, discharge processing |

### Healthcare Identity Workflows 
| Service | Description | Key Operations |
|---------|-------------|----------------|
| **CreateABHA** | ABHA registration workflows | Multi-step OTP verification |
| **CreateHPR** | HPR registration processes | Professional registry enrollment |

## Detailed Service Guide

## Patient Service

The Patient service provides comprehensive patient record management with full CRUD operations and advanced search capabilities.

### Basic Operations

```python
from carestack import ClientConfig, Patient
import asyncio

async def patient_operations():
    config = ClientConfig(
        api_key="your_api_key",
    )
    
    patient_service = Patient(config)
    
    # 1. Create a new patient
    new_patient_data = {
        "idNumber": "123456789012",
        "idType": "Aadhaar",
        "patientType": "OPD",
        "firstName": "Alice",
        "lastName": "Johnson",
        "birthDate": "1985-03-15",
        "gender": "F",
        "address": "456 Health Street, Medical City",
        "mobileNumber": "+919876543210",
        "emailId": "alice.johnson@example.com",
        "emergencyContact": "+919876543211",
        "bloodGroup": "B+",
        "maritalStatus": "Married",
        "occupation": "Teacher",
        "resourceType": "PATIENT"
    }
    
    created = await patient_service.create(new_patient_data)
    print(f" Created patient: {created.message}")
    
    # 2. Find all patients (with pagination)
    all_patients = await patient_service.find_all()
    print(f"Total patients: {all_patients.total}")
    print(f"Current page: {all_patients.page}")
    
    # Get next page if available
    if all_patients.next_page:
        next_page_patients = await patient_service.find_all(next_page=all_patients.next_page)
    
    # 3. Find patient by ID
    if all_patients.patients:
        patient_id = all_patients.patients[0].id
        patient = await patient_service.find_by_id(patient_id)
    
    # 4. Check if patient exists
    exists = await patient_service.exists(patient_id)
    
    # 5. Update patient
    update_data = {
        "address": "789 New Address, Updated City",
        "mobileNumber": "+919876543299"
    }
    updated = await patient_service.update(patient_id, update_data)
    
    # 6. Search patients with filters
    search_filters = {
        "firstName": "Alice",
        "gender": "F",
        "patientType": "OPD"
    }
    filtered_patients = await patient_service.find_by_filters(search_filters)
    
    # 7. Delete patient (if needed)
    # await patient_service.delete(patient_id)
    # print(f"Patient deleted")

asyncio.run(patient_operations())
```

### Expected Response Structure

```python
# Create Patient Response
{
    "message": "Patient created successfully",
    "patient_id": "pat_123456789",
    "status": "success"
}

# Find All Patients Response
{
    "patients": [
        {
            "id": "pat_123456789",
            "firstName": "Alice",
            "lastName": "Johnson",
            "birthDate": "1985-03-15",
            "gender": "F",
            "mobileNumber": "+919876543210",
            "emailId": "alice.johnson@example.com",
            "address": "456 Health Street, Medical City",
            "patientType": "OPD",
            "resourceType": "PATIENT",
            "createdAt": "2025-01-15T10:30:00Z",
            "updatedAt": "2025-01-15T10:30:00Z"
        }
    ],
    "total": 150,
    "page": 1,
    "per_page": 10,
    "next_page": "eyJpZCI6InBhdF8xMjM0NTY3ODkifQ=="
}
```

## Practitioner Service

Manage healthcare provider information with full lifecycle support and HPR integration.

### Complete Practitioner Workflow

```python
from carestack import ClientConfig, Practitioner
import asyncio
from datetime import datetime

async def practitioner_operations():
    config = ClientConfig(
        api_key="your_api_key",
    )
    
    practitioner_service = Practitioner(config)
    
    # 1. Create a new practitioner
    new_practitioner = {
        "registrationId": "REG12345",
        "department": "Cardiology",
        "designation": "Senior Consultant",
        "specialization": ["Interventional Cardiology", "Cardiac Surgery"],
        "status": "Active",
        "joiningDate": "2020-01-15",
        "staffType": "Doctor",
        "firstName": "Dr. Sarah",
        "lastName": "Wilson",
        "birthDate": "1975-08-20",
        "gender": "F",
        "mobileNumber": "+919876543210",
        "emailId": "dr.sarah.wilson@hospital.com",
        "address": "123 Medical Complex, Healthcare City",
        "pincode": "110001",
        "state": "Delhi",
        "qualifications": [
            {
                "degree": "MBBS",
                "university": "AIIMS Delhi",
                "year": "1998"
            },
            {
                "degree": "MD Cardiology",
                "university": "AIIMS Delhi", 
                "year": "2002"
            }
        ],
        "experience": 23,
        "languages": ["English", "Hindi", "Telugu"],
        "consultationFee": 1500,
        "resourceType": "Practitioner"
    }
    
    created = await practitioner_service.create(new_practitioner)
    
    # 2. Find all practitioners
    all_practitioners = await practitioner_service.find_all()
    
    # 3. Find practitioner by ID
    if all_practitioners.practitioners:
        practitioner_id = all_practitioners.practitioners[0].id
        practitioner = await practitioner_service.find_by_id(practitioner_id)

        # 4. Update practitioner
        update_data = {
            "consultationFee": 1800,
            "status": "Active",
            "address": "Updated Medical Complex Address"
        }
        updated = await practitioner_service.update(practitioner_id, update_data)
        
        # 5. Search practitioners by filters
        search_filters = {
            "department": "Cardiology",
            "status": "Active",
            "specialization": "Interventional Cardiology"
        }
        filtered = await practitioner_service.find_by_filters(search_filters)

asyncio.run(practitioner_operations())
```

### Expected Response Structure

```python
# Create Practitioner Response
{
    "message": "Practitioner created successfully",
    "practitioner_id": "pract_789012345",
	...,
    "status": "success"
}

# Find Practitioner Response
{
    "id": "pract_789012345",
    "registrationId": "REG12345",
    "firstName": "Dr. Sarah",
    "lastName": "Wilson",
    "department": "Cardiology",
    "designation": "Senior Consultant",
    "specialization": ["Interventional Cardiology", "Cardiac Surgery"],
    "qualifications": [
        {
            "degree": "MBBS",
            "university": "AIIMS Delhi",
            "year": "1998"
        }
    ],
    "experience": 23,
    "consultationFee": 1500,
    "status": "Active",
    "mobileNumber": "+919876543210",
    "emailId": "dr.sarah.wilson@hospital.com",
    "resourceType": "Practitioner"
}
```

## Organization Service

Comprehensive healthcare facility management with master data support.

### Organization Management

```python
from carestack import ClientConfig, Organization
import asyncio

async def organization_operations():
    config = ClientConfig(
        api_key="your_api_key",
        x_hpr_id="your_hpr_id" # Required for Organization operations
    )
    
    org_service = Organization(config)
    
    # 1. Get master data first (helpful for creating organizations)
    states = await org_service.get_lgd_states()
    
    # Get districts for a specific state
    if states:
        state_code = states[0]["stateCode"]
        districts = await org_service.get_lgd_sub_districts(state_code)
    
    # Get organization types
    org_types = await org_service.get_organization_type(ownership_code="PVT")
    
    # 2. Create new organization
    new_organization = {
        "basicInformation": {
            "facilityName": "Advanced Care Medical Center",
            "facilityType": "Hospital",
            ...
        },
        "organizationDetails": {
            "organizationType": "HOSP",
            "ownership": "PVT",
            ...
        },
        ...
    }
    
    created_org = await org_service.create(new_organization)

    # 3. Find all organizations
    organizations = await org_service.find_all()
    
    # 4. Find organization by ID
    if organizations.organizations:
        org_id = organizations.organizations[0].id
        organization = await org_service.find_by_id("facility_id", org_id)
        
        # 5. Update organization
        update_data = {
            "basicInformation": {
                "contactNumber": "+911234567899",
                "bedStrength": 250
            }
        }
        updated = await org_service.update(org_id, update_data)
        
        # 6. Search organizations
        search_criteria = {
            "state": "Delhi",
            "organizationType": "HOSP",
            "specialty": "Cardiology"
        }
        search_results = await org_service.search(search_criteria)
        print(f"Search results: {len(search_results.organizations)}")

asyncio.run(organization_operations())
```

### Expected Response Structure

```python
# Organization Response
{
    "id": "org_456789012",
    "basicInformation": {
        "facilityName": "Advanced Care Medical Center",
        "facilityType": "Hospital",
        ...
    },
    "organizationDetails": {
        "organizationType": "HOSP",
        "ownership": "PVT",
        ...
    },
    ...
    "registrationDate": "2025-01-15T10:30:00Z",
    "status": "Active"
}
```

## Appointment Service

Complete appointment lifecycle management with scheduling and availability.

### Appointment Operations

```python
from carestack import ClientConfig, Appointment, AppointmentDTO, AppointmentPriority, AppointmentType
from datetime import datetime, timedelta
import asyncio

async def appointment_operations():
    config = ClientConfig(
        api_key="your_api_key",
    )
    
    appointment_service = Appointment(config)
    
    # 1. Create a new appointment
    appointment_start = datetime.now() + timedelta(days=3)
    appointment_end = appointment_start + timedelta(minutes=30)
    
    new_appointment = AppointmentDTO(
        practitioner_reference="pract_789012345",
        patient_reference="pat_123456789",
        appointment_start_time=appointment_start,
        appointment_end_time=appointment_end,
        ...
    )
    
    created_appointment = await appointment_service.create(new_appointment)
    print(f"Appointment created: {created_appointment}")
    
    # 2. Get all appointments
    all_appointments = await appointment_service.find_all()
    print(f"Total appointments: {len(all_appointments.appointments)}")
    
    # 3. Find appointment by reference
    if all_appointments.appointments:
        appointment_ref = all_appointments.appointments[0].reference
        appointment = await appointment_service.find_by_id(appointment_ref)
        
        # 4. Update appointment
        from carestack import UpdateAppointmentDTO
        
        update_data = UpdateAppointmentDTO(
            reference=appointment_ref,
            status="CONFIRMED",
            notes="Patient confirmed attendance",
            priority=AppointmentPriority.HIGH
        )
        
        updated = await appointment_service.update(update_data)
        print(f" Updated appointment: {updated}")
        
        # 5. Check if appointment exists
        exists = await appointment_service.exists(appointment_ref)
        print(f" Appointment exists: {exists}")
        
        # 6. Cancel/Delete appointment (if needed)
        # await appointment_service.delete(appointment_ref)
        # print(f"Appointment cancelled")

```

### Expected Response Structure

```python
# Appointment Response
{
    "reference": "appt_abc123def456",
    "patient_reference": "pat_123456789",
    "practitioner_reference": "pract_789012345",
    "organization_id": "org_456789012",
    ...
}

# Appointments List Response
{
    "appointments": [...],  # Array of appointment objects
    "total": 45,
    "page": 1,
    "per_page": 20,
    "has_next": true
}
```

## DIscharge Summary Generation

Leverage AI for automated healthcare document generation.

### AI-Powered Document Generation

```python
from carestack import ClientConfig, AiService
import asyncio

async def ai_service_operations():
    config = ClientConfig(
        api_key="your_api_key",
    )
    
    ai_service = AiService(config)
    
    # 1. Generate Discharge Summary
    discharge_data = {
        "caseType": "inpatient",
        "files": ["file123.pdf"],
        "publicKey": "-----BEGIN PUBLIC KEY-----..."
    }
    
    try:
        discharge_summary = await ai_service.generate_discharge_summary(discharge_data)
        print("Generated Discharge Summary:")
        print(f"Summary: {discharge_summary['summary'][:200]}...")
        print(f" Medications: {len(discharge_summary['medications'])} prescribed")
        print(f"Follow-up: {discharge_summary['follow_up_instructions']}")
        
    except Exception as e:
        print(f" Error generating discharge summary: {e}")
    
    # 2. Generate FHIR Bundle
    fhir_bundle_data = {
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
    }
    
    try:
        fhir_bundle = await ai_service.generate_fhir_bundle(fhir_bundle_data)
        print("Generated FHIR Bundle:")
        print(f"Resource Type: {fhir_bundle['resourceType']}")
        print(f" Bundle ID: {fhir_bundle['id']}")
        print(f" Entries: {len(fhir_bundle['entry'])} resources")
        
        # Display summary of included resources
        resource_types = {}
        for entry in fhir_bundle['entry']:
            resource_type = entry['resource']['resourceType']
            resource_types[resource_type] = resource_types.get(resource_type, 0) + 1
        
        print(" Bundle Contents:")
        for resource_type, count in resource_types.items():
            print(f"   - {resource_type}: {count}")
            
    except Exception as e:
        print(f"Error generating FHIR bundle: {e}")

asyncio.run(ai_service_operations())
```

### Expected Response Structure

```python
# Discharge Summary Response
{
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
}

# FHIR Bundle Response
{
    "resourceType": "Bundle",
    "id": "bundle_discharge_123456",
    "type": "document",
    "timestamp": "2025-01-15T14:30:00Z",
    "entry": [
        {
            "resource": {
                "resourceType": "Patient",
                "id": "pat_123456789",
                "name": [{"family": "Doe", "given": ["John"]}]
            }
        },
        {
            "resource": {
                "resourceType": "Condition",
                "id": "condition_123",
                "code": {
                    "coding": [{"code": "I21.9", "display": "Acute myocardial infarction"}]
                }
            }
        }
    ]
}
```

## Health Document Linking

Orchestrate complex healthcare document workflows with multi-step processes.

### Document Linking Workflow

```python
from carestack import ClientConfig, DocumentLinking, HealthDocumentLinkingDTO, HealthInformationDTO, HealthInformationTypes, AppointmentPriority, AppointmentType
import asyncio

async def document_linking_operations():
    config = ClientConfig(
        api_key="your_api_key",
    )
    
    doc_service = DocumentLinking(config)
    
    # Create comprehensive linking DTO
    linking_dto = HealthDocumentLinkingDTO(
        patientReference="123e4567-e89b-12d3-a456-426614174000",
        practitionerReference="321e4567-e89b-12d3-a456-426614174000",
        patientAddress="123 Cedar Street",
        patientName="Jane Doe",
        appointmentStartDate="2025-08-15T14:00:00Z",
        appointmentEndDate="2025-08-15T14:30:00Z",
        appointmentPriority="ROUTINE",
        organizationId="Org987",
        mobileNumber="9998887776",
        hiType="OPConsultation",
        healthRecords=[rawFhir=True, fhirDocument={"key": "value"}, informationType=HealthInformationTypes.OPConsultation]
    )
    
    try:
        # Execute the complete linking workflow
        print(" Starting health document linking process...")
        
        # This orchestrates the entire workflow:
        # 1. Creates care context
        # 2. Updates visit records (if health records exist)
        # 3. Links care context with health document
        success = await doc_service.link_health_document(linking_dto)
        
        if success:
            print("Health document linking completed successfully!")
            print("Workflow completed:")
            print("Care context created")
            print(" Visit records updated")
            print(" Care context linked to health document")
        else:
            print(" Document linking completed but no health records were processed")
            
    except Exception as e:
        print(f" Error in document linking workflow: {e}")

# Individual workflow step examples
async def individual_workflow_steps():
    config = ClientConfig(
        api_key="your_api_key",
    )
    
    doc_service = DocumentLinking(config)
    
    # Step 1: Create Care Context (internal method example)
    print("Step 1: Creating care context...")
    # This is handled internally by link_health_document method
    
    # Step 2: Update Visit Records (internal method example)
    print("Step 2: Updating visit records...")
    # This is also handled internally
    
    # Step 3: Link Care Context (internal method example)
    print("Step 3: Linking care context...")
    # Final step handled internally
    
    print("All workflow steps would be orchestrated automatically")

asyncio.run(document_linking_operations())
```

### Expected Response Structure

```python
# Document Linking Response
{
    "success": True,
    "care_context_id": "cc_789012345",
    "visit_record_updated": True,
    "health_document_linked": True,
    "transaction_state": {
        "care_context_created": True,
        "visit_records_updated": True,
        "care_context_linked": True,
        "completed_at": "2025-01-15T14:30:00Z"
    },
    "message": "Health document linking completed successfully"
}

# Error Response (if failure occurs)
{
    "success": False,
    "error": "Care context creation failed",
    "transaction_state": {
        "care_context_created": False,
        "visit_records_updated": False,
        "care_context_linked": False,
        "failed_at": "care_context_creation",
        "error_details": "Patient reference not found"
    }
}
```

## FHIR Bundle Generation

Orchestrate healthcare encounters with FHIR generation and discharge processing.

```python
from carestack import ClientConfig, Encounter, EncounterRequestDTO, CaseType, OPConsultationDTO, OPConsultationSections
import asyncio

async def encounter_operations():
    config = ClientConfig(
        api_key="your_api_key",
    )
    
    encounter_service = Encounter(config)
    
    # Create encounter request for payload-based FHIR generation
    payload_request = EncounterRequestDTO(
        case_type=CaseType.OP_CONSULTATION,
        patient_details=PatientDetails(name="John Doe", ...),
        doctor_details=[DoctorDetails(name="Dr. Smith", ...)],
        document_references=["lab_report_1.pdf", "lab_report_2.pdf"],
        enable_extraction=True,
        dto=OPConsultationDTO(
            payload=OPConsultationSections(
              chief_complaints="Fever and cough",
              physical_examination=PhysicalExamination(...),
              ...)
        ),
    )
    
    try:
        # Generate FHIR bundle from sections
        print("Generating FHIR bundle from clinical sections...")
        fhir_bundle = await encounter_service.create(payload_request)
        
        print("FHIR Bundle generated successfully!")
        print(f"Resource Type: {fhir_bundle['resourceType']}")
        print(f"Bundle ID: {fhir_bundle['id']}")
        print(f"Total Resources: {len(fhir_bundle['entry'])}")
        
        # Analyze bundle contents
        resource_summary = {}
        for entry in fhir_bundle['entry']:
            resource_type = entry['resource']['resourceType']
            resource_summary[resource_type] = resource_summary.get(resource_type, 0) + 1
        
        print("Bundle Resource Summary:")
        for resource_type, count in resource_summary.items():
            print(f"- {resource_type}: {count}")
            
    except Exception as e:
        print(f"Error generating FHIR from sections: {e}")
    
    # 2. Generate FHIR Bundle from Files
    print("\n" + "="*50)
    print("Generating FHIR bundle from case sheet files...")
    
    # File-based encounter request
    file_based_request = EncounterRequestDTO(
        case_type=CaseType.OP_CONSULTATION,
        patient_details=PatientDetails(name="John Doe", ...),
        doctor_details=[DoctorDetails(name="Dr. Smith", ...)],
        document_references=["lab_report_1.pdf", "lab_report_2.pdf"],
        enable_extraction=True,
        dto=OPConsultationDTO(   
            caseSheets=["case_sheet_1.pdf", "case_sheet_2.pdf"],
        ),
    )
    
    try:
        fhir_from_files = await encounter_service.create(file_based_request)
        print("FHIR Bundle generated from files!")
        print(f"Processed files: Case sheets + Lab reports")
        print(f"Bundle ID: {fhir_from_files['id']}")
        
    except Exception as e:
        print(f"Error generating FHIR from files: {e}")
    
```

### Expected Response Structure

```python
# FHIR Bundle from Sections Response
{
    "resourceType": "Bundle",
    "id": "encounter_bundle_123456",
    "type": "document",
    "timestamp": "2025-01-15T14:30:00Z",
    "entry": [
        {
            "fullUrl": "Patient/pat_123456789",
            "resource": {
                "resourceType": "Patient",
                "id": "pat_123456789",
                "name": [{"family": "Doe", "given": ["John"]}]
            }
        },
        {
            "fullUrl": "Encounter/enc_789012345",
            "resource": {
                "resourceType": "Encounter",
                "id": "enc_789012345",
                "status": "finished",
                "class": {"code": "AMB"},
                "subject": {"reference": "Patient/pat_123456789"}
            }
        },
        ...
    ],
}
```

## Healthcare Identity Workflows

Complete Ayushman Bharat Health Account registration with step-by-step workflow.

### ABHA Registration Workflow

```python
from carestack import ClientConfig, CreateABHA, AbhaSteps
import asyncio

async def abha_registration_workflow():
    config = ClientConfig(
        api_key="your_api_key",
    )
    
    abha_service = CreateABHA(config)
    
    # Complete ABHA registration workflow
    print("Starting ABHA Registration Process")
    
    try:
        # Step 1: Start registration with Aadhaar number
        print("Step 1: Initiating Aadhaar OTP...")
        aadhaar_number = "123456789012"  # Replace with actual Aadhaar
        
        step1_result = await abha_service.start_registration(aadhaar_number)
        
        txn_id = step1_result['data']['txnId']
        print(f"Transaction ID: {txn_id}")
        
        # Step 2: Enroll with Aadhaar OTP
        print("\nStep 2: Verifying Aadhaar OTP...")
        
        # In real implementation, you would collect OTP from user
        aadhaar_otp = "123456"  # Get from user input
        mobile_number = "9876543210"  # User's mobile number
        
        step2_result = await abha_service.registration_flow(
            AbhaSteps.ENROLL_WITH_AADHAAR,
            {
                "otp": aadhaar_otp,
                "txnId": txn_id,
                "mobile": mobile_number
            }
        )
        
        new_txn_id = step2_result['data']['txnId']
        
        # Step 3: Generate Mobile OTP
        print("\nStep 3: Generating Mobile OTP...")
        
        step3_result = await abha_service.registration_flow(
            AbhaSteps.GENERATE_MOBILE_OTP,
            {
                "txnId": new_txn_id,
                "mobile": mobile_number
            }
        )
        
        mobile_txn_id = step3_result['data']['txnId']
        
        # Step 4: Verify Mobile OTP
        print("\nStep 4: Verifying Mobile OTP...")
        
        mobile_otp = "654321"  # Get from user input
        
        step4_result = await abha_service.registration_flow(
            AbhaSteps.VERIFY_MOBILE_OTP,
            {
                "otp": mobile_otp,
                "txnId": mobile_txn_id
            }
        )
        
        print(f"{step4_result['message']}")
        print(f"Next step: {step4_result['next_step']}")
        
        verified_txn_id = step4_result['data']['txnId']
        
        # Step 5: Get ABHA Address Suggestions
        print("\nStep 5: Getting ABHA Address suggestions...")
        
        step5_result = await abha_service.registration_flow(
            AbhaSteps.GET_ABHA_ADDRESS_SUGGESTION,
            {
                "txnId": verified_txn_id
            }
        )
        
        for i, suggestion in enumerate(abha_suggestions[:3], 1):
            print(f"   {i}. {suggestion}")
        
        # Step 6: Create ABHA Address
        print("\n Step 6: Creating ABHA Address...")
        
        selected_abha_address = abha_suggestions[0]  # User selects first suggestion
        password = "SecurePass@123"  # User sets password
        
        step6_result = await abha_service.registration_flow(
            AbhaSteps.CREATE_ABHA_ADDRESS,
            {
                "txnId": verified_txn_id,
                "abhaAddress": selected_abha_address,
                "password": password
            }
        )
        
        print(f" {step6_result['message']}")
        print(f" Next step: {step6_result['next_step']}")
        
        # Step 7: Complete Registration
        print("\n Step 7: Completing ABHA registration...")
        
        final_result = await abha_service.registration_flow(
            AbhaSteps.CREATE_ABHA_ID,
            {
                "txnId": step6_result['data']['txnId']
            }
        )
        
        print(" ABHA Registration Completed Successfully!")
        
        return final_result['data']['ABHAProfile']
        
    except Exception as e:
        print(f"ABHA Registration failed: {e}")
        return None

# Run the workflows
if __name__ == "__main__":
    asyncio.run(abha_registration_workflow())
```

### Expected Response Structure

```python
# Step 1: Start Registration Response
{
    "message": "OTP sent to registered mobile number ending with XXX7890",
    "data": {
        "txnId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    },
    "next_step": "ENROLL_WITH_AADHAAR",
    "next_step_payload_hint": {
        "required_fields": ["otp", "txnId", "mobile"],
        "otp": "6-digit OTP received on mobile",
        "txnId": "Transaction ID from previous step",
        "mobile": "10-digit mobile number"
    }
}

# Final Registration Response
{
    "message": "ABHA registration completed successfully",
    "data": {
        "ABHAProfile": {
            "ABHANumber": "12-3456-7890-1234",
            "ABHAAddress": "john.doe@abha",
            "name": "John Doe",
            "dateOfBirth": "01-01-1980",
            "gender": "M",
            "mobile": "9876543210",
            "email": "john.doe@email.com",
            "status": "ACTIVE",
            "createdAt": "2025-01-15T14:30:00Z"
        }
    },
    "next_step": "REGISTRATION_COMPLETE",
    "next_step_payload_hint": null
}
```



### HPR Registration Workflow

Healthcare Professional Registry registration with multi-step verification.

```python
from carestack import ClientConfig, CreateHPR, HprRegistrationSteps
import asyncio

async def hpr_registration_workflow():
    config = ClientConfig(
        api_key="your_api_key",
        x_hpr_id="your_hpr_id" # Required for Organization operations
    )
    
    hpr_service = CreateHPR(config)
    
    # Complete HPR registration workflow
    print("Starting HPR Registration Process")
    print("=" * 50)
    
    try:
        # Step 1: Generate Aadhaar OTP
        print(" Step 1: Initiating Aadhaar OTP for HPR...")
        aadhaar_number = "123456789012"  # Replace with actual Aadhaar
        
        step1_result = await hpr_service.start_registration(aadhaar_number)
        
        txn_id = step1_result['data']['txnId']
        
        # Step 2: Verify Aadhaar OTP
        print("\n Step 2: Verifying Aadhaar OTP...")
        
        aadhaar_otp = "123456"  # Get from user input
        domain_name = "allopathy"  # Medical domain
        
        step2_result = await hpr_service.registration_flow(
            HprRegistrationSteps.VERIFY_AADHAAR_OTP,
            {
                "otp": aadhaar_otp,
                "txnId": txn_id,
                "domainName": domain_name,
                "idType": "aadhaar",
                "restrictions": None
            }
        )
        
        verified_txn_id = step2_result['data']['txnId']
        
        # Step 3: Check Existing Account
        print("\n📋 Step 3: Checking for existing HPR account...")
        
        step3_result = await hpr_service.registration_flow(
            HprRegistrationSteps.CHECK_EXISTING_ACCOUNT,
            {
                "txnId": verified_txn_id
            }
        )
        
        print(f"{step3_result['message']}")
        
        if step3_result['data'].get('accountExists', False):
            print(" Existing HPR account found")
            existing_hpr_id = step3_result['data']['hprId']
            print(f"Existing HPR ID: {existing_hpr_id}")
            return step3_result
        
        # Step 4: Demographic Authentication
        print("\n📋 Step 4: Performing demographic authentication...")
        
        step4_result = await hpr_service.registration_flow(
            HprRegistrationSteps.DEMOGRAPHIC_AUTH,
            {
                "txnId": verified_txn_id,
                "demographic_data": {
                    "name": "Dr. Sarah Wilson",
                    "gender": "F",
                    "yearOfBirth": "1975",
                    "dayOfBirth": "15",
                    "monthOfBirth": "08"
                }
            }
        )
        
        auth_txn_id = step4_result['data']['txnId']
        
        # Step 5: Get HPR ID Suggestions
        print("\n Step 5: Getting HPR ID suggestions...")
        
        step5_result = await hpr_service.registration_flow(
            HprRegistrationSteps.GET_HPR_ID_SUGGESTION,
            {
                "txnId": auth_txn_id
            }
        )
        
        hpr_suggestions = step5_result['data']['hprIdSuggestions']
        print(f"Available HPR ID suggestions:")
        for i, suggestion in enumerate(hpr_suggestions[:3], 1):
            print(f"   {i}. {suggestion}")
        
        # Step 6: Create HPR ID with Professional Details
        print("\n Step 6: Creating HPR ID with professional details...")
        
        selected_hpr_id = hpr_suggestions[0]  # User selects first suggestion
        
        step6_result = await hpr_service.registration_flow(
            HprRegistrationSteps.CREATE_HPR_ID,
            {
                "txnId": auth_txn_id,
                "hprId": selected_hpr_id,
                "password": password,
                ...
            }
        )
        
        print(" HPR Registration Completed Successfully!")
        
        return step6_result['data']['hprProfile']
        
    except Exception as e:
        print(f" HPR Registration failed: {e}")
        return None


# Run the workflows
if __name__ == "__main__":
    asyncio.run(hpr_registration_workflow())
```

### Expected Response Structure

```python
# Step 1: Start HPR Registration Response
{
    "message": "Aadhaar OTP generated for HPR registration",
    "data": {
        "txnId": "hpr_a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    },
    "next_step": "VERIFY_AADHAAR_OTP",
    "next_step_payload_hint": {
        "required_fields": ["otp", "txnId", "domainName", "idType"],
        "otp": "6-digit OTP received on mobile",
        "domainName": "Medical domain (e.g., allopathy, ayurveda)",
        "idType": "aadhaar"
    }
}

# Final HPR Registration Response
{
    "message": "HPR ID created successfully",
    "data": {
        "hprProfile": {
            "hprId": "HPR123456789",
            "fullName": "Dr. Sarah Wilson",
            "dateOfBirth": "15-08-1975",
            "gender": "F",
            "mobile": "9876543210",
            "email": "dr.sarah@hospital.com",
            ...,
            "status": "ACTIVE",
            "createdAt": "2025-01-15T14:30:00Z"
        }
    },
    "next_step": "None",
    "next_step_payload_hint": null
}
```

## Response Examples

### Common Response Patterns

All services follow consistent response patterns for better predictability:

#### Success Response Format
```python
{
    "status": "success",
    "message": "Operation completed successfully",
    "data": { /* relevant data */ },
    "timestamp": "2025-01-15T14:30:00Z",
    "request_id": "req_123456789"
}
```

#### Error Response Format
```python
{
    "status": "error",
    "error_code": "VALIDATION_ERROR",
    "message": "Invalid input data provided",
    "details": {
        "field": "email",
        "reason": "Invalid email format"
    },
    "timestamp": "2025-01-15T14:30:00Z",
    "request_id": "req_123456789"
}
```

#### Paginated Response Format
```python
{
    "items": [ /* array of items */ ],
    "pagination": {
        "total": 150,
        "page": 1,
        "per_page": 20,
        "total_pages": 8,
        "has_next": true,
        "has_previous": false,
        "next_page": "eyJpZCI6InBhdF8xMjM0NTY3ODkifQ==",
        "previous_page": null
    }
}
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Errors

```python
# Problem: 401 Unauthorized
# Solution: Check API credentials

async def diagnose_auth_issues():
    config = SDKConfig.from_environment()
    
    # Test configuration
    if not config.api_key:
        print("API key is missing")
        return
        
    print("Credentials are configured")
    
    # Test API connectivity
    try:
        sdk = CarestackSDK(config)
        patients = await sdk.patients.find_all()
        print("Authentication successful")
    except EhrApiError as e:
        if e.status_code == 401:
            print("Invalid credentials")
        elif e.status_code == 403:
            print("Insufficient permissions")
        else:
            print(f"API error: {e.message}")
```

#### 2. Data Validation Issues

```python
def validate_patient_data(patient_data):
    """Validate patient data before API call"""
    errors = []
    
    # Required fields
    required_fields = ["firstName", "lastName", "resourceType"]
    for field in required_fields:
        if not patient_data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Format validations
    if patient_data.get("gender") and patient_data["gender"] not in ["M", "F", "O"]:
        errors.append("Gender must be M, F, or O")
    
    if patient_data.get("birthDate"):
        try:
            datetime.strptime(patient_data["birthDate"], "%Y-%m-%d")
        except ValueError:
            errors.append("birthDate must be in YYYY-MM-DD format")
    
    return errors

# Usage
patient_data = {"firstName": "John", "lastName": "Doe"}
errors = validate_patient_data(patient_data)

if errors:
    print("Validation errors:")
    for error in errors:
        print(f"   - {error}")
else:
    print("Data validation passed")
```

## Support

### Documentation and Resources

- **Python-3.10 SDK Documentation**: [http://python-mkdocs-bucket.s3-website.ap-south-1.amazonaws.com/]
  
### Getting Help

1. **SDK Version**: `pip show carestack`
2. **Python Version**: `python --version`
3. **Error Messages**: Full traceback if applicable

## System Requirements

### Minimum Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+, CentOS 7+)
- **Network**: HTTPS connectivity to Carestack APIs

### Dependencies

```
httpx>=0.25.0
pydantic>=2.0.0
typing_extensions
pytest
pytest-asyncio
pydantic[email]>=2.0.0
python-dotenv>=1.0.1
cryptography>=3.0
python-jose[cryptography]>=3.3.0
```