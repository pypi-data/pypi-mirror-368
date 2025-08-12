import json
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from carestack.base.errors import EhrApiError
from carestack.common.enums import (
    Gender,
    PatientEndpoints,
    PatientIdTypeEnum,
    PatientTypeEnum,
    ResourceType,
    StatesAndUnionTerritories,
)
from carestack.patient.patient_dto import (
    CreateUpdatePatientResponse,
    GetPatientResponse,
    PatientDTO,  # noqa: F401
    PatientFilterResponse,
    UpdatePatientDTO,
    UpdatePatientDTO,
)
from carestack.patient.patient_service import Patient
from carestack.base.base_types import ClientConfig
from carestack.common.config_test import client_config


@pytest.fixture
def mock_patient_service(client_config: ClientConfig) -> Patient:
    return Patient(client_config)


@pytest.fixture
def valid_create_patient_data() -> dict[str, Any]:
    """Fixture for valid patient creation data."""
    return {
        "idNumber": "ID12345",
        "idType": PatientIdTypeEnum.AADHAAR.value,
        "patientType": PatientTypeEnum.NEW.value,
        "firstName": "John",
        "lastName": "Doe",
        "birthDate": "1990-01-01",
        "gender": Gender.MALE.value,
        "mobileNumber": "+919876543210",
        "emailId": "john.doe@example.com",
        "address": "123 Health St, Med-city",
        "pincode": "123456",
        "state": StatesAndUnionTerritories.KERALA.value,
        "resourceType": ResourceType.PATIENT.value,
    }


@pytest.fixture
def valid_update_patient_data() -> dict[str, Any]:
    """Fixture for valid patient update data."""
    return {
        "resourceId": "patient-123",
        "emailId": "john.doe.new@example.com",
        "mobileNumber": "+919999988888",
        "resourceType": ResourceType.PATIENT.value,
    }


@pytest.fixture
def valid_patient_filters() -> dict[str, Any]:
    """Fixture for valid patient filter data."""
    return {"first_name": "John", "last_name": "Doe", "state": "Kerala", "count": 10}


# --- get_all Tests ---
@pytest.mark.asyncio
async def test_get_all_patients_success(mock_patient_service: Patient) -> None:
    """Test successful retrieval of all patients."""
    service = mock_patient_service
    mock_response = GetPatientResponse(
        type="success",
        message="Patients Fetched",
        requestResource=[],
        totalNumberOfRecords=0,
        nextPageLink=None,
    )
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await service.find_all()

        mock_get.assert_called_once_with(
            PatientEndpoints.GET_ALL_PATIENTS,
            response_model=GetPatientResponse,
            query_params=None,
        )
        assert result == mock_response
        assert result.message == "Patients Fetched"


@pytest.mark.asyncio
async def test_get_all_patients_with_next_page(mock_patient_service: Patient) -> None:
    """Test successful retrieval of all patients with next page."""
    service = mock_patient_service
    next_page_token = "next_page_token"
    mock_response = GetPatientResponse(
        type="success",
        message="Patients Fetched",
        requestResource=[],
        totalNumberOfRecords=0,
        nextPageLink=next_page_token,
    )
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await service.find_all(next_page=next_page_token)

        mock_get.assert_called_once_with(
            PatientEndpoints.GET_ALL_PATIENTS,
            response_model=GetPatientResponse,
            query_params={"nextPage": next_page_token},
        )
        assert result == mock_response
        assert result.next_page_link == next_page_token


@pytest.mark.asyncio
async def test_get_all_patients_ehr_api_error(mock_patient_service: Patient) -> None:
    """Test get_all_patients when get raises EhrApiError."""
    service = mock_patient_service
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = EhrApiError("API error", 400)

        with pytest.raises(EhrApiError) as exc_info:
            await service.find_all()

        mock_get.assert_called_once_with(
            PatientEndpoints.GET_ALL_PATIENTS,
            response_model=GetPatientResponse,
            query_params=None,
        )
        assert "API error" in str(exc_info.value)
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_all_patients_general_exception(
    mock_patient_service: Patient,
) -> None:
    """Test get_all_patients when __make_request raises a general Exception."""
    service = mock_patient_service
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("General error")

        with pytest.raises(EhrApiError) as exc_info:
            await service.find_all()
        mock_get.assert_called_once_with(
            PatientEndpoints.GET_ALL_PATIENTS,
            response_model=GetPatientResponse,
            query_params=None,
        )
        assert (
            "An unexpected error occurred while fetching all patients: General error"
            in str(exc_info.value)
        )
        assert exc_info.value.status_code == 500


# --- create Tests ---


@pytest.mark.asyncio
async def test_create_patient_success(
    mock_patient_service: Patient, valid_create_patient_data: dict[str, Any]
) -> None:
    """Test successful creation of a patient."""
    service = mock_patient_service
    mock_response = CreateUpdatePatientResponse(
        resourceId="new-patient-id", validationErrors=None
    )
    with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await service.create(valid_create_patient_data)

        validated_data = PatientDTO(**valid_create_patient_data).model_dump(
            by_alias=True
        )
        mock_post.assert_called_once_with(
            PatientEndpoints.CREATE_PATIENT,
            validated_data,
            response_model=CreateUpdatePatientResponse,
        )
        assert result == mock_response
        assert result.resource_id == "new-patient-id"


@pytest.mark.asyncio
async def test_create_patient_empty_data(mock_patient_service: Patient) -> None:
    """Test create_patient with empty data."""
    service = mock_patient_service
    with pytest.raises(EhrApiError) as exc_info:
        await service.create({})
    assert "Patient data cannot be null." in str(exc_info.value)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_create_patient_validation_error(mock_patient_service: Patient) -> None:
    """Test create_patient with invalid data."""
    service = mock_patient_service
    invalid_data = {"firstName": "J"}  # Too short
    with pytest.raises(EhrApiError) as exc_info:
        await service.create(invalid_data)
    assert "Patient data validation error." in str(exc_info.value)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_create_patient_api_error(
    mock_patient_service: Patient, valid_create_patient_data: dict[str, Any]
) -> None:
    """Test create_patient when post raises EhrApiError."""
    service = mock_patient_service
    with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = EhrApiError("API error", 400)
        with pytest.raises(EhrApiError) as exc_info:
            await service.create(valid_create_patient_data)
        assert "API error" in str(exc_info.value)
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_create_patient_general_exception(
    mock_patient_service: Patient, valid_create_patient_data: dict[str, Any]
) -> None:
    """Test create_patient when post raises a general Exception."""
    service = mock_patient_service
    with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("General error")
        with pytest.raises(EhrApiError) as exc_info:
            await service.create(valid_create_patient_data)
        assert (
            "An unexpected error occurred while creating patient: General error"
            in str(exc_info.value)
        )
        assert exc_info.value.status_code == 500


# --- update Tests ---


@pytest.mark.asyncio
async def test_update_patient_success(
    mock_patient_service: Patient, valid_update_patient_data: dict[str, Any]
) -> None:
    """Test successful update of a patient."""
    service = mock_patient_service
    mock_response = CreateUpdatePatientResponse(
        resourceId="patient-123",
        message="Patient updated successfully",
        validationErrors=None,
    )
    with patch.object(service, "put", new_callable=AsyncMock) as mock_put:
        mock_put.return_value = mock_response
        result = await service.update(valid_update_patient_data)

        validated_data = UpdatePatientDTO(**valid_update_patient_data).model_dump(
            by_alias=True
        )
        mock_put.assert_called_once_with(
            PatientEndpoints.UPDATE_PATIENT,
            validated_data,
            CreateUpdatePatientResponse,
        )
        assert result == mock_response
        assert result.message == "Patient updated successfully"


@pytest.mark.asyncio
async def test_update_patient_empty_data(mock_patient_service: Patient) -> None:
    """Test update_patient with empty data."""
    service = mock_patient_service
    with pytest.raises(EhrApiError) as exc_info:
        await service.update({})
    assert "Update patient data cannot be null." in str(exc_info.value)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_update_patient_validation_error(mock_patient_service: Patient) -> None:
    """Test update_patient with invalid data."""
    service = mock_patient_service
    invalid_data = {"resourceId": "123", "mobileNumber": "12345"}  # Invalid mobile
    with pytest.raises(EhrApiError) as exc_info:
        await service.update(invalid_data)
    assert "Patient data validation error." in str(exc_info.value)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_update_patient_api_error(
    mock_patient_service: Patient, valid_update_patient_data: dict[str, Any]
) -> None:
    """Test update_patient when put raises EhrApiError."""
    service = mock_patient_service
    with patch.object(service, "put", new_callable=AsyncMock) as mock_put:
        mock_put.side_effect = EhrApiError("API error", 404)
        with pytest.raises(EhrApiError) as exc_info:
            await service.update(valid_update_patient_data)
        assert "API error" in str(exc_info.value)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_patient_general_exception(
    mock_patient_service: Patient, valid_update_patient_data: dict[str, Any]
) -> None:
    """Test update_patient when put raises a general Exception."""
    service = mock_patient_service
    with patch.object(service, "put", new_callable=AsyncMock) as mock_put:
        mock_put.side_effect = Exception("General error")
        with pytest.raises(EhrApiError) as exc_info:
            await service.update(valid_update_patient_data)
        assert (
            "An unexpected error occurred while updating patient: General error"
            in str(exc_info.value)
        )
        assert exc_info.value.status_code == 500


# --- delete Tests ---


@pytest.mark.asyncio
async def test_delete_patient_success(mock_patient_service: Patient) -> None:
    """Test successful deletion of a patient."""
    service = mock_patient_service
    patient_id = "patient-to-delete"
    with patch(
        "carestack.base.base_service.BaseService.delete", new_callable=AsyncMock
    ) as mock_base_delete:
        await service.delete(patient_id)
        mock_base_delete.assert_called_once_with(
            PatientEndpoints.DELETE_PATIENT.format(patient_id=patient_id),
        )


@pytest.mark.asyncio
async def test_delete_patient_empty_id(mock_patient_service: Patient) -> None:
    """Test delete_patient with an empty ID."""
    service = mock_patient_service
    with pytest.raises(EhrApiError) as exc_info:
        await service.delete("")
    assert "Patient ID cannot be null or empty." in str(exc_info.value)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_delete_patient_api_error(mock_patient_service: Patient) -> None:
    """Test delete_patient when delete raises EhrApiError."""
    service = mock_patient_service
    patient_id = "patient-123"
    with patch(
        "carestack.base.base_service.BaseService.delete", new_callable=AsyncMock
    ) as mock_base_delete:
        mock_base_delete.side_effect = EhrApiError("API error", 404)
        with pytest.raises(EhrApiError) as exc_info:
            await service.delete(patient_id)
        assert "API error" in str(exc_info.value)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_patient_general_exception(mock_patient_service: Patient) -> None:
    """Test delete_patient when delete raises a general Exception."""
    service = mock_patient_service
    patient_id = "patient-123"
    with patch(
        "carestack.base.base_service.BaseService.delete", new_callable=AsyncMock
    ) as mock_base_delete:
        mock_base_delete.side_effect = Exception("General error")
        with pytest.raises(EhrApiError) as exc_info:
            await service.delete(patient_id)
        assert (
            "An unexpected error occurred while deleting patient: General error"
            in str(exc_info.value)
        )
        assert exc_info.value.status_code == 500


# --- find_by_filters Tests ---


@pytest.mark.asyncio
async def test_find_by_filters_success(
    mock_patient_service: Patient, valid_patient_filters: dict[str, Any]
) -> None:
    """Test successful retrieval of patients by filters."""
    service = mock_patient_service
    mock_response = PatientFilterResponse(entry=[], total=0)
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await service.find_by_filters(valid_patient_filters)

        transformed_filters = {
            "firstName": "John",
            "lastName": "Doe",
            "address-state": "Kerala",
            "_count": 10,
        }
        expected_params = {"filters": json.dumps(transformed_filters)}

        mock_get.assert_called_once_with(
            PatientEndpoints.GET_PATIENT_BY_FILTERS,
            PatientFilterResponse,
            expected_params,
        )
        assert result == mock_response


@pytest.mark.asyncio
async def test_find_by_filters_with_next_page(
    mock_patient_service: Patient, valid_patient_filters: dict[str, Any]
) -> None:
    """Test find_by_filters with next page token."""
    service = mock_patient_service
    next_page_token = "next_page_token"
    mock_response = PatientFilterResponse(entry=[], total=0)
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        await service.find_by_filters(valid_patient_filters, next_page=next_page_token)

        transformed_filters = {
            "firstName": "John",
            "lastName": "Doe",
            "address-state": "Kerala",
            "_count": 10,
        }
        expected_params = {
            "filters": json.dumps(transformed_filters),
            "nextPage": next_page_token,
        }

        mock_get.assert_called_once_with(
            PatientEndpoints.GET_PATIENT_BY_FILTERS,
            PatientFilterResponse,
            expected_params,
        )


@pytest.mark.asyncio
async def test_find_by_filters_validation_error(mock_patient_service: Patient) -> None:
    """Test find_by_filters with invalid filter data."""
    service = mock_patient_service
    invalid_filters = {"first_name": "J"}  # Too short
    with pytest.raises(EhrApiError) as exc_info:
        await service.find_by_filters(invalid_filters)
    assert "An unexpected error occurred while fetching patients by filters" in str(
        exc_info.value
    )
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_find_by_filters_api_error(
    mock_patient_service: Patient, valid_patient_filters: dict[str, Any]
) -> None:
    """Test find_by_filters when get raises EhrApiError."""
    service = mock_patient_service
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = EhrApiError("API error", 400)
        with pytest.raises(EhrApiError) as exc_info:
            await service.find_by_filters(valid_patient_filters)
        assert "API error" in str(exc_info.value)
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_find_by_filters_general_exception(
    mock_patient_service: Patient, valid_patient_filters: dict[str, Any]
) -> None:
    """Test find_by_filters when get raises a general Exception."""
    service = mock_patient_service
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("General error")
        with pytest.raises(EhrApiError) as exc_info:
            await service.find_by_filters(valid_patient_filters)
        assert (
            "An unexpected error occurred while fetching patients by filters: General error"
            in str(exc_info.value)
        )
        assert exc_info.value.status_code == 500


# # --- get_by_id Tests ---


@pytest.mark.asyncio
async def test_get_patient_by_id_success(mock_patient_service: Patient) -> None:
    """Test successful retrieval of a patient by ID."""
    service = mock_patient_service
    mock_response = GetPatientResponse(
        type="success",
        message="Patient Found",
        requestResource=[],
        totalNumberOfRecords=1,
        nextPageLink=None,
    )
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await service.find_by_id("123")

        mock_get.assert_called_once_with(
            PatientEndpoints.GET_PATIENT_BY_ID.format(patient_id="123"),
            response_model=GetPatientResponse,
        )
        assert result.message == "Patient Found"


@pytest.mark.asyncio
async def test_get_patient_by_id_empty_id(mock_patient_service: Patient) -> None:
    """Test get_patient_by_id with an empty ID."""
    service = mock_patient_service
    with pytest.raises(EhrApiError) as exc_info:
        await service.find_by_id("")
    assert "Patient ID cannot be null or empty." in str(exc_info.value)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_patient_by_id_ehr_api_error(mock_patient_service: Patient) -> None:
    """Test get_patient_by_id when get raises EhrApiError."""
    service = mock_patient_service
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = EhrApiError("API error", 400)

        with pytest.raises(EhrApiError) as exc_info:
            await service.find_by_id("123")
        assert "API error" in str(exc_info.value)
        assert exc_info.value.status_code == 400
        mock_get.assert_called_once_with(
            PatientEndpoints.GET_PATIENT_BY_ID.format(patient_id="123"),
            response_model=GetPatientResponse,
        )


@pytest.mark.asyncio
async def test_get_patient_by_id_general_exception(
    mock_patient_service: Patient,
) -> None:
    """Test get_patient_by_id when get raises a general Exception."""
    service = mock_patient_service
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("General error")
        with pytest.raises(EhrApiError) as exc_info:
            await service.find_by_id("123")
        mock_get.assert_called_once_with(
            PatientEndpoints.GET_PATIENT_BY_ID.format(patient_id="123"),
            response_model=GetPatientResponse,
        )
        assert "General error" in str(exc_info.value)
        assert exc_info.value.status_code == 500


# # --- exists Tests ---


@pytest.mark.asyncio
async def test_patient_exists_true(mock_patient_service: Patient) -> None:
    """Test patient_exists returns True when patient is found."""
    service = mock_patient_service
    mock_response = GetPatientResponse(
        type="success",
        message="Patient Found !!!",
        requestResource=[],
        totalNumberOfRecords=1,
        nextPageLink=None,
    )
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await service.exists("123")
        mock_get.assert_called_once_with(
            PatientEndpoints.PATIENT_EXISTS.format(patient_id="123"),
            GetPatientResponse,
        )
        assert result is True


@pytest.mark.asyncio
async def test_patient_exists_false(mock_patient_service: Patient) -> None:
    """Test patient_exists returns False when patient is not found."""
    service = mock_patient_service
    mock_response = GetPatientResponse(
        type="error",
        message="Patient Not Found",
        requestResource=[],
        totalNumberOfRecords=0,
        nextPageLink=None,
    )
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        result = await service.exists("123")
        mock_get.assert_called_once()
        assert result is False


@pytest.mark.asyncio
async def test_patient_exists_empty_id(mock_patient_service: Patient) -> None:
    """Test patient_exists returns False when given an empty ID."""
    service = mock_patient_service
    result = await service.exists("")
    assert result is False


@pytest.mark.asyncio
async def test_patient_exists_ehr_api_error(mock_patient_service: Patient) -> None:
    """Test patient_exists returns False when get raises EhrApiError."""
    service = mock_patient_service
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = EhrApiError("API error", 400)
        result = await service.exists("123")
        mock_get.assert_called_once_with(
            PatientEndpoints.PATIENT_EXISTS.format(patient_id="123"), GetPatientResponse
        )
        assert result is False


@pytest.mark.asyncio
async def test_patient_exists_general_exception(mock_patient_service: Patient) -> None:
    """Test patient_exists raise EhrApiError when __make_request raises a general Exception."""
    service = mock_patient_service
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("General error")

        with pytest.raises(EhrApiError) as exc_info:
            await service.exists("123")
        assert (
            "An unexpected error occurred while fetching patient by Id: General error"
            in str(exc_info.value)
        )
        assert exc_info.value.status_code == 500
