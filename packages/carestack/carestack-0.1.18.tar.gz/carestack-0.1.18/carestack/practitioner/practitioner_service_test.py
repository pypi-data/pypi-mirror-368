import json
from typing import Any
from unittest.mock import AsyncMock, patch
import pytest
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import (
    Departments,
    Gender,
    PractitionerEndPoints,
    ResourceType,
    StatesAndUnionTerritories,
)
from carestack.practitioner.practitioner_dto import (
    CreatePractitionerDTO,
    CreateUpdatePractitionerResponse,
    GetPractitionerResponse,
    PractitionerFilterResponse,
    UpdatePractitionerDTO,
)
from carestack.practitioner.practitioner_service import Practitioner
from carestack.common.config_test import client_config


@pytest.fixture
def mock_practitioner_service(client_config: ClientConfig) -> Practitioner:
    """Fixture to create a Practitioner service instance."""
    return Practitioner(client_config)


@pytest.fixture
def valid_create_practitioner_data() -> dict[str, Any]:
    """Fixture for valid practitioner creation data."""
    return {
        "registrationId": "REG12345",
        "department": Departments.DERMATOLOGY.value,
        "designation": "Senior Doctor",
        "status": "Active",
        "joiningDate": "2023-01-15",
        "staffType": "Permanent",
        "firstName": "John",
        "lastName": "Doe",
        "birthDate": "1985-05-20",
        "gender": Gender.MALE.value,
        "mobileNumber": "+919876543210",
        "emailId": "john.doe@example.com",
        "address": "123 Health St, Med-city",
        "pincode": "123456",
        "state": StatesAndUnionTerritories.KERALA.value,
        "resourceType": ResourceType.PRACTITIONER.value,
    }


@pytest.fixture
def valid_update_practitioner_data() -> dict[str, Any]:
    """Fixture for valid practitioner update data."""
    return {
        "resourceId": "practitioner-123",
        "registrationId": "REG12345",
        "department": Departments.DERMATOLOGY.value,
        "designation": "Consultant",
        "status": "Inactive",
        "joiningDate": "2023-01-15",
        "staffType": "Contract",
        "firstName": "John",
        "lastName": "Doe",
        "birthDate": "1985-05-20",
        "gender": Gender.MALE.value,
        "mobileNumber": "+919876543211",
        "emailId": "john.doe.new@example.com",
        "address": "456 Wellness Ave, Med-city",
        "pincode": "654321",
        "state": StatesAndUnionTerritories.KARNATAKA.value,
        "resourceType": ResourceType.PRACTITIONER.value,
    }


@pytest.fixture
def valid_practitioner_filters() -> dict[str, Any]:
    """Fixture for valid practitioner filter data."""
    return {
        "firstName": "John",
        "lastName": "Doe",
        "state": StatesAndUnionTerritories.KERALA.value,
        "count": 10,
    }


# --- Test Cases ---


# get_all
@pytest.mark.asyncio
async def test_get_all_success(mock_practitioner_service: Practitioner) -> None:
    service = mock_practitioner_service
    mock_response_data = {
        "type": "success",
        "message": "Practitioners Fetched",
        "requestResource": [],
        "totalNumberOfRecords": 0,
        "nextPageLink": None,
    }
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = GetPractitionerResponse(**mock_response_data)
        result = await service.find_all()

        mock_get.assert_called_once_with(
            PractitionerEndPoints.GET_ALL_PRACTITIONERS,
            response_model=GetPractitionerResponse,
            query_params=None,
        )
        assert isinstance(result, GetPractitionerResponse)
        assert result.message == "Practitioners Fetched"
        assert result.total_number_of_records == 0


@pytest.mark.asyncio
async def test_get_all_with_next_page(mock_practitioner_service: Practitioner) -> None:
    service = mock_practitioner_service
    next_page_token = "some_token"
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = GetPractitionerResponse(
            type="success",
            message="Practitioners Fetched",
            requestResource=[],
            totalNumberOfRecords=1,
            nextPageLink=next_page_token,
        )
        result = await service.find_all(next_page=next_page_token)

        mock_get.assert_called_once_with(
            PractitionerEndPoints.GET_ALL_PRACTITIONERS,
            response_model=GetPractitionerResponse,
            query_params={"nextPage": next_page_token},
        )
        assert result.next_page_link == next_page_token


@pytest.mark.asyncio
async def test_get_all_ehr_api_error(mock_practitioner_service: Practitioner) -> None:
    service = mock_practitioner_service
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = EhrApiError("API error", 400)
        with pytest.raises(EhrApiError) as exc_info:
            await service.find_all()
        assert "API error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_all_general_exception(
    mock_practitioner_service: Practitioner,
) -> None:
    service = mock_practitioner_service
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = Exception("General error")
        with pytest.raises(EhrApiError) as exc_info:
            await service.find_all()
        assert "An unexpected error occurred" in str(exc_info.value)


# get_by_id
@pytest.mark.asyncio
async def test_get_by_id_success(mock_practitioner_service: Practitioner) -> None:
    service = mock_practitioner_service
    practitioner_id = "practitioner-123"
    mock_response_data = {
        "type": "success",
        "message": "Practitioner Found",
        "totalNumberOfRecords": 1,
        "requestResource": [],
        "nextPageLink": None,
    }
    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = GetPractitionerResponse(**mock_response_data)
        result = await service.find_by_id(practitioner_id)

        mock_get.assert_called_once_with(
            PractitionerEndPoints.GET_PRACTITIONER_BY_ID.format(
                practitioner_id=practitioner_id
            ),
            response_model=GetPractitionerResponse,
        )
        assert isinstance(result, GetPractitionerResponse)


@pytest.mark.asyncio
async def test_get_by_id_empty_id(mock_practitioner_service: Practitioner) -> None:
    with pytest.raises(EhrApiError, match="Practitioner ID cannot be null or empty."):
        await mock_practitioner_service.find_by_id("")


# exists
@pytest.mark.asyncio
async def test_exists_true(mock_practitioner_service: Practitioner) -> None:
    service = mock_practitioner_service
    practitioner_id = "practitioner-123"
    mock_response = GetPractitionerResponse(
        type="success",
        message="Practitioner Found !!!",
        requestResource=[],
        totalNumberOfRecords=1,
        nextPageLink=None,
    )
    with patch.object(service, "get", return_value=mock_response) as mock_get:
        result = await service.exists(practitioner_id)
        mock_get.assert_called_once()
        assert result is True


@pytest.mark.asyncio
async def test_exists_false(mock_practitioner_service: Practitioner) -> None:
    service = mock_practitioner_service
    mock_response = GetPractitionerResponse(
        type="error",
        message="Practitioner Not Found",
        requestResource=[],
        totalNumberOfRecords=0,
        nextPageLink=None,
    )
    with patch.object(service, "get", return_value=mock_response):
        assert await service.exists("non-existent-id") is False


@pytest.mark.asyncio
async def test_exists_on_api_error(mock_practitioner_service: Practitioner) -> None:
    service = mock_practitioner_service
    with patch.object(service, "get", side_effect=EhrApiError("API error", 404)):
        assert await service.exists("any-id") is False


@pytest.mark.asyncio
async def test_exists_empty_id(mock_practitioner_service: Practitioner) -> None:
    assert await mock_practitioner_service.exists("") is False


# create
@pytest.mark.asyncio
async def test_create_success(
    mock_practitioner_service: Practitioner,
    valid_create_practitioner_data: dict[str, Any],
) -> None:
    service = mock_practitioner_service
    mock_response = CreateUpdatePractitionerResponse(
        type="success",
        message="Practitioner created successfully",
        resourceId="new-practitioner-id",
    )
    with patch.object(service, "post", return_value=mock_response) as mock_post:
        result = await service.create(valid_create_practitioner_data)
        validated_data = CreatePractitionerDTO(
            **valid_create_practitioner_data
        ).model_dump(by_alias=True)
        mock_post.assert_called_once_with(
            PractitionerEndPoints.CREATE_PRACTITIONER,
            validated_data,
            response_model=CreateUpdatePractitionerResponse,
        )
        assert result.resource_id == "new-practitioner-id"


@pytest.mark.asyncio
async def test_create_already_exists_error(
    mock_practitioner_service: Practitioner,
    valid_create_practitioner_data: dict[str, Any],
) -> None:
    service = mock_practitioner_service
    with patch.object(service, "post", side_effect=EhrApiError("Conflict", 409)):
        with pytest.raises(EhrApiError, match="Practitioner already exists"):
            await service.create(valid_create_practitioner_data)


# update
@pytest.mark.asyncio
async def test_update_success(
    mock_practitioner_service: Practitioner,
    valid_update_practitioner_data: dict[str, Any],
) -> None:
    service = mock_practitioner_service
    mock_response = CreateUpdatePractitionerResponse(
        type="success",
        resourceId="updated-practitioner-id",
        message="Practitioner updated successfully",
    )
    with patch.object(service, "put", return_value=mock_response) as mock_put:
        result = await service.update(valid_update_practitioner_data)
        validated_data = UpdatePractitionerDTO(
            **valid_update_practitioner_data
        ).model_dump(by_alias=True)
        mock_put.assert_called_once_with(
            PractitionerEndPoints.UPDATE_PRACTITIONER,
            validated_data,
            response_model=CreateUpdatePractitionerResponse,
        )
        assert result.message == "Practitioner updated successfully"


# get_by_filters
@pytest.mark.asyncio
async def test_get_by_filters_success(
    mock_practitioner_service: Practitioner,
    valid_practitioner_filters: dict[str, Any],
) -> None:
    service = mock_practitioner_service
    with patch.object(
        service,
        "get",
        return_value=PractitionerFilterResponse(entry=[], total=0, link=None),
    ) as mock_get:
        await service.find_by_filters(valid_practitioner_filters)

        expected_transformed_filters = {
            "name": "John",
            "family": "Doe",
            "_count": 10,
            "address-state": "Kerala",
        }
        expected_params = {"filters": json.dumps(expected_transformed_filters)}

        mock_get.assert_called_once_with(
            PractitionerEndPoints.GET_PRACTITIONER_BY_FILTERS,
            PractitionerFilterResponse,
            expected_params,
        )


# delete
@pytest.mark.asyncio
async def test_delete_success(mock_practitioner_service: Practitioner) -> None:
    service = mock_practitioner_service
    practitioner_id = "practitioner-to-delete"
    with patch(
        "carestack.base.base_service.BaseService.delete", new_callable=AsyncMock
    ) as mock_base_delete:
        await service.delete(practitioner_id)
        mock_base_delete.assert_called_once_with(
            PractitionerEndPoints.DELETE_PRACTITIONER.format(
                practitioner_id=practitioner_id
            )
        )


@pytest.mark.asyncio
async def test_delete_general_exception(
    mock_practitioner_service: Practitioner,
) -> None:
    service = mock_practitioner_service
    with patch(
        "carestack.base.base_service.BaseService.delete",
        side_effect=Exception("Unexpected error"),
    ):
        with pytest.raises(EhrApiError, match="Failed to delete practitioner"):
            await service.delete("any-id")
