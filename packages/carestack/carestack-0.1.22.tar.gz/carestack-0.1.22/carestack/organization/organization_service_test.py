from unittest.mock import AsyncMock, patch

from pydantic import ValidationError
import pytest
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import (
    UTILITY_API_ENDPOINTS,
    Country,
    OrganizationsIdType,
    OrganizationEndPoints,
)
from carestack.organization.organization_dto import (
    AddOrganizationDTO,
    GetOrganizationsResponse,
    LGDStatesListResponse,
    LGDDistrictsListResponse,
    LGDDistrictsResponse,
    LGDStatesResponse,
    MasterDataResponse,
    MasterTypeResponse,
    OrganizationSubTypeRequest,
    OrganizationTypeRequest,
    OwnershipSubTypeRequest,
    SearchOrganizationDTO,
    SearchOrganizationResponse,
    SpecialitiesRequest,
    UpdateOrganizationDTO,
)
from carestack.organization.organization_service import (
    GetJsonFromTextResponse,
    Organization,
)
from carestack.common.config_test import client_config


@pytest.fixture
def organization_service(client_config: ClientConfig) -> Organization:
    return Organization(client_config)


@pytest.fixture
def valid_add_organization_data() -> dict:
    """Fixture providing a valid dictionary for AddOrganizationDTO."""
    return {
        "basicInformation": {
            "facilityName": "Valid Test Facility",
            "region": "North",
            "addressLine1": "123 Valid St",
            "addressLine2": "Suite 100",
            "district": "Valid District",
            "subDistrict": "Valid SubDistrict",
            "city": "Valid City",
            "state": "Valid State",
            "country": Country.INDIA.value,
            "pincode": "123456",
            "latLongs": ["12.9716, 77.5946"],
        },
        "contactInformation": {
            "mobileNumber": "+919876543210",
            "email": "valid@example.com",
            "landline": "0801234567",
            "stdcode": "080",
            "websiteLink": "http://valid.example.com",
        },
        "uploadDocuments": {
            "boardPhoto": {"value": "valid_base64_1", "name": "valid_board.jpg"},
            "buildingPhoto": {"value": "valid_base64_2", "name": "valid_building.png"},
        },
        "addAddressProof": [
            {
                "addressProofType": "Electricity Bill",
                "addressProofAttachment": {
                    "value": "valid_base64_3",
                    "name": "valid_proof.pdf",
                },
            }
        ],
        "facilityTimings": [
            {"timings": "Mon-Fri", "shifts": [{"start": "09:00", "end": "17:00"}]}
        ],
        "facilityDetails": {
            "ownershipType": "Private",
            "ownershipSubType": "Individual",
            "status": "Active",
        },
        "systemOfMedicine": {
            "specialities": [
                {
                    "systemofMedicineCode": "MODERN",
                    "specialities": ["Cardiology", "Neurology"],
                }
            ],
            "facilityType": "Hospital",
            "facilitySubType": "Super Speciality",
            "serviceType": "IPD/OPD",
        },
        "facilityInventory": {
            "totalNumberOfVentilators": 10,
            "totalNumberOfBeds": 200,
            "hasDialysisCenter": "Yes",
            "hasPharmacy": "Yes",
            "hasBloodBank": "Yes",
            "hasCathLab": "Yes",
            "hasDiagnosticLab": "Yes",
            "hasImagingCenter": "Yes",
            "servicesByImagingCenter": [
                {"service": "MRI", "count": 1},
                {"service": "CT", "count": 1},
            ],
            "nhrrid": "VALID_NHRRID",
            "nin": "VALID_NIN",
            "abpmjayid": "VALID_ABPMJAY",
            "rohiniId": "VALID_ROHINI",
            "echsId": "VALID_ECHS",
            "cghsId": "VALID_CGHS",
            "ceaRegistration": "VALID_CEA",
            "stateInsuranceSchemeId": "VALID_STATEINS",
        },
        "accountId": "valid_account_123",
    }


@pytest.mark.asyncio
async def test_get_all_success(organization_service):
    mock_response_data = {
        "message": None,
        "data": [{"id": "1"}],
        "nextPageLink": "2",
        "totalNumberOfRecords": None,
    }
    mock_response_obj = GetOrganizationsResponse(**mock_response_data)
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    response = await organization_service.find_all()  # Call without next_page
    assert isinstance(response, GetOrganizationsResponse)
    assert response.model_dump(by_alias=True) == mock_response_data

    organization_service.get.assert_called_with(
        OrganizationEndPoints.GET_ALL_ORGANIZATIONS,
        GetOrganizationsResponse,
        None,
    )


@pytest.mark.asyncio
async def test_get_all_with_next_page_success(organization_service):
    # Ensure mock_response matches GetOrganizationsResponse structure
    mock_response_data = {
        "message": None,
        "data": [{"id": "1"}],
        "nextPageLink": "3",  # Matches the expected next page
        "totalNumberOfRecords": 10,  # Example value
    }
    mock_response_obj = GetOrganizationsResponse(**mock_response_data)
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    response = await organization_service.find_all(next_page="2")

    # Assert the response object structure
    assert isinstance(response, GetOrganizationsResponse)
    assert response.model_dump(by_alias=True) == mock_response_data

    # Assert the underlying call with correct params
    organization_service.get.assert_called_with(
        OrganizationEndPoints.GET_ALL_ORGANIZATIONS,
        GetOrganizationsResponse,
        {"nextPage": "2"},
    )


@pytest.mark.asyncio
async def test_get_all_invalid_response_type(organization_service):
    """Tests that get_all raises an error for an invalid response format."""
    organization_service.get = AsyncMock(return_value={"invalid": "response"})
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.find_all()
    assert "Invalid response format" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_all_api_error(organization_service):
    organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.find_all()
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_all_unexpected_error(organization_service):
    organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.find_all()
    assert "Failed to fetch facilities" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_by_id_success(organization_service):
    mock_response_data = {
        "message": "Organization found",
        "data": [{"id": "1", "name": "Test organization"}],
        "nextPageLink": None,
        "totalNumberOfRecords": 1,
    }
    mock_response_obj = GetOrganizationsResponse(**mock_response_data)
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    response = await organization_service.find_by_id(
        OrganizationsIdType.ORGANIZATION_ID, "1"
    )
    assert isinstance(response, GetOrganizationsResponse)
    assert response.model_dump(by_alias=True) == mock_response_data
    organization_service.get.assert_called_with(
        OrganizationEndPoints.GET_ORGANIZATION_BY_ID.format(
            search_param=OrganizationsIdType.ORGANIZATION_ID.value, search_term="1"
        ),
        GetOrganizationsResponse,
    )


@pytest.mark.asyncio
async def test_get_by_id_with_account_id_success(organization_service):
    mock_response_data = {
        "message": "Organization found",
        "data": [{"id": "acc_123", "name": "Test organization by Account"}],
        "nextPageLink": None,
        "totalNumberOfRecords": 1,
    }
    mock_response_obj = GetOrganizationsResponse(**mock_response_data)
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    response = await organization_service.find_by_id(
        OrganizationsIdType.ACCOUNT_ID, "acc_123"
    )
    assert isinstance(response, GetOrganizationsResponse)
    assert response.model_dump(by_alias=True) == mock_response_data
    organization_service.get.assert_called_with(
        OrganizationEndPoints.GET_ORGANIZATION_BY_ID.format(
            search_param=OrganizationsIdType.ACCOUNT_ID.value, search_term="acc_123"
        ),
        GetOrganizationsResponse,
    )


@pytest.mark.asyncio
async def test_get_by_id_api_error(organization_service):
    organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.find_by_id(OrganizationsIdType.ORGANIZATION_ID, "1")
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_by_id_unexpected_error(organization_service):
    organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.find_by_id(OrganizationsIdType.ORGANIZATION_ID, "1")
    assert "Failed to fetch organization with ID" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_exists_success_organization_id(organization_service):
    mock_response_obj = GetOrganizationsResponse(
        message="Facility Found !!!",
        data=[],
        nextPageLink=None,
        totalNumberOfRecords=None,
    )
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    exists = await organization_service.exists(OrganizationsIdType.ORGANIZATION_ID, "1")
    assert exists is True
    organization_service.get.assert_called_with(
        OrganizationEndPoints.ORGANIZATION_EXISTS.format(
            search_param=OrganizationsIdType.ORGANIZATION_ID.value, search_term="1"
        ),
        GetOrganizationsResponse,
    )


@pytest.mark.asyncio
async def test_exists_success_account_id(organization_service):
    mock_response_obj = GetOrganizationsResponse(
        message="Records Found!!",
        data=[],
        nextPageLink=None,
        totalNumberOfRecords=None,
    )
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    exists = await organization_service.exists(
        OrganizationsIdType.ACCOUNT_ID, "acc_123"
    )
    assert exists is True
    organization_service.get.assert_called_with(
        OrganizationEndPoints.ORGANIZATION_EXISTS.format(
            search_param=OrganizationsIdType.ACCOUNT_ID.value, search_term="acc_123"
        ),
        GetOrganizationsResponse,
    )


@pytest.mark.asyncio
async def test_exists_false_message_mismatch_org_id(organization_service):
    """Test that exists returns False if the message for org ID doesn't match."""
    mock_response_obj = GetOrganizationsResponse(
        message="Wrong Message",
        data=[],
        nextPageLink=None,
        totalNumberOfRecords=None,
    )
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    exists = await organization_service.exists(OrganizationsIdType.ORGANIZATION_ID, "1")
    assert exists is False


@pytest.mark.asyncio
async def test_exists_false_message_mismatch_account_id(organization_service):
    """Test that exists returns False if the message for account ID doesn't match."""
    mock_response_obj = GetOrganizationsResponse(
        message="Wrong Message",
        data=[],
        nextPageLink=None,
        totalNumberOfRecords=None,
    )
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    exists = await organization_service.exists(
        OrganizationsIdType.ACCOUNT_ID, "acc_123"
    )
    assert exists is False


@pytest.mark.asyncio
async def test_exists_not_found(organization_service):
    organization_service.get = AsyncMock(side_effect=EhrApiError("Not Found", 404))
    exists = await organization_service.exists(OrganizationsIdType.ORGANIZATION_ID, "1")
    assert exists is False


@pytest.mark.asyncio
async def test_exists_api_error(organization_service):
    organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.exists(OrganizationsIdType.ORGANIZATION_ID, "1")
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_exists_unexpected_error(organization_service):
    organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.exists(OrganizationsIdType.ORGANIZATION_ID, "1")
    assert "Error while checking organization" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_create_success(organization_service, valid_add_organization_data):
    """Tests successful organization creation."""
    mock_response_message = "organization created successfully"
    mock_api_response_obj = GetJsonFromTextResponse(response=mock_response_message)
    organization_service.post = AsyncMock(return_value=mock_api_response_obj)

    organization_data_dict = valid_add_organization_data
    organization_dto = AddOrganizationDTO(**organization_data_dict)

    response = await organization_service.create(organization_data_dict)

    assert response == mock_response_message

    organization_service.post.assert_called_once_with(
        OrganizationEndPoints.REGISTER_ORGANIZATION,
        organization_dto.model_dump(by_alias=True),
        response_model=GetJsonFromTextResponse,
    )


@pytest.mark.asyncio
async def test_create_validation_error(organization_service):
    organization_data = {"name": 123}  # Invalid type for name
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.create(organization_data)
    assert "Validation failed" in str(exc_info.value)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_create_api_error(organization_service, valid_add_organization_data):
    organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))

    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.create(valid_add_organization_data)
    assert "API Error" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_create_unexpected_error(
    organization_service, valid_add_organization_data
):
    organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))

    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.create(valid_add_organization_data)

    assert "Failed to register organization" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_update_success(organization_service):
    mock_response_message = "organization updated successfully"
    mock_response_obj = GetJsonFromTextResponse(response=mock_response_message)
    organization_service.put = AsyncMock(return_value=mock_response_obj)
    update_data = {
        "id": "1",
        "spoc_name": "Updated Spoc",
        "spoc_id": "spoc123",
        "consent_manager_name": "Updated Consent Manager",
        "consent_manager_id": "consent123",
    }
    update_dto = UpdateOrganizationDTO(**update_data)
    response = await organization_service.update(update_dto)

    assert response == mock_response_message
    expected_validated_data = {
        "id": "1",
        "spocName": "Updated Spoc",
        "spocId": "spoc123",
        "consentManagerName": "Updated Consent Manager",
        "consentManagerId": "consent123",
    }
    organization_service.put.assert_called_with(
        OrganizationEndPoints.UPDATE_ORGANIZATION,
        expected_validated_data,
        GetJsonFromTextResponse,
    )


@pytest.mark.asyncio
async def test_update_validation_error(organization_service):
    """
    Tests that creating an UpdateOrganizationDTO with invalid data raises a
    ValidationError. The service method itself expects a valid DTO.
    """
    invalid_update_data = {"id": "1", "spoc_name": 123}  # spoc_name should be a string
    with pytest.raises(ValidationError) as exc_info:
        UpdateOrganizationDTO(**invalid_update_data)
    assert "spoc_name" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_api_error(organization_service):
    organization_service.put = AsyncMock(side_effect=EhrApiError("API Error", 500))
    update_data = {
        "id": "1",
        "spoc_name": "Updated Spoc",
        "spoc_id": "spoc123",
        "consent_manager_name": "Updated Consent Manager",
        "consent_manager_id": "consent123",
    }
    update_dto = UpdateOrganizationDTO(**update_data)
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.update(update_dto)
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_unexpected_error(organization_service):
    organization_service.put = AsyncMock(side_effect=Exception("Unexpected Error"))
    update_data = {
        "id": "1",
        "spoc_name": "Updated Spoc",
        "spoc_id": "spoc123",
        "consent_manager_name": "Updated Consent Manager",
        "consent_manager_id": "consent123",
    }
    with pytest.raises(EhrApiError) as exc_info:
        update_dto = UpdateOrganizationDTO(**update_data)
        await organization_service.update(update_dto)
    assert "Failed to update organization" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_delete_success(organization_service):
    mock_response = {"message": "organization deleted successfully"}
    service = organization_service
    organization_id = "1"
    with patch(
        "carestack.base.base_service.BaseService.delete", new_callable=AsyncMock
    ) as mock_base_delete:
        await service.delete(organization_id)
        mock_base_delete.assert_called_once_with(
            OrganizationEndPoints.DELETE_ORGANIZATION.format(
                organization_id=organization_id
            )
        )


@pytest.mark.asyncio
async def test_delete_api_error(organization_service):
    organization_service.delete = AsyncMock(side_effect=EhrApiError("API Error", 500))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.delete("1")
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_search_success(organization_service):
    mock_response_data = {
        "facilities": [],
        "message": "ok",
        "totalFacilities": 0,
        "numberOfPages": 0,
    }
    mock_response_obj = SearchOrganizationResponse(**mock_response_data)
    organization_service.post = AsyncMock(return_value=mock_response_obj)
    search_data = {
        "ownership_code": "test_owner",
        "state_lgd_code": "test_state",
        "district_lgd_code": "test_district",
        "sub_district_lgd_code": "test_subdistrict",
        "pincode": "123456",
        "organization_name": "Test organization",
        "organization_id": "1",
        "page": 1,
        "results_per_page": 10,
    }
    search_dto = SearchOrganizationDTO(**search_data)
    response = await organization_service.search(search_dto)
    assert isinstance(response, SearchOrganizationResponse)
    assert response.model_dump(by_alias=True) == mock_response_data
    expected_validated_data = {
        "ownershipCode": "test_owner",  # Alias is correct
        "stateLGDCode": "test_state",
        "districtLGDCode": "test_district",
        "subDistrictLGDCode": "test_subdistrict",
        "pincode": "123456",
        "facilityName": "Test organization",
        "facilityId": "1",
        "page": 1,
        "resultsPerPage": 10,
    }
    organization_service.post.assert_called_with(
        OrganizationEndPoints.SEARCH_ORGANIZATION,
        expected_validated_data,
        SearchOrganizationResponse,
    )


@pytest.mark.asyncio
async def test_search_validation_error(organization_service):
    """
    Tests that creating a SearchOrganizationDTO with invalid data raises a
    ValidationError.
    """
    invalid_search_data = {
        "page": 1,
        "results_per_page": 200,  # > 100, invalid
        "ownership_code": "test_owner",
        "state_lgd_code": "test_state",
        "district_lgd_code": "test_district",
        "sub_district_lgd_code": "test_subdistrict",
        "pincode": "123456",
        "organization_name": "Test organization",
        "organization_id": "1",
    }
    with pytest.raises(ValidationError) as exc_info:
        SearchOrganizationDTO(**invalid_search_data)
    assert "page" in str(exc_info.value)
    assert "less than or equal to 100" in str(exc_info.value)


@pytest.mark.asyncio
async def test_search_api_error(organization_service):
    organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))

    search_data = {
        "ownership_code": "test_owner",
        "state_lgd_code": "test_state",
        "district_lgd_code": "test_district",
        "sub_district_lgd_code": "test_subdistrict",
        "pincode": "123456",
        "organization_name": "Test organization",
        "organization_id": "1",
        "page": 1,
        "results_per_page": 10,
    }
    search_dto = SearchOrganizationDTO(**search_data)

    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.search(search_dto)

    assert "API Error" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_search_unexpected_error(organization_service):
    organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))
    search_data = {
        "ownership_code": "test_owner",
        "state_lgd_code": "test_state",
        "district_lgd_code": "test_district",
        "sub_district_lgd_code": "test_subdistrict",
        "pincode": "123456",
        "organization_name": "Test organization",
        "organization_id": "1",
        "page": 1,
        "results_per_page": 10,
    }
    with pytest.raises(EhrApiError) as exc_info:
        search_dto = SearchOrganizationDTO(**search_data)
        await organization_service.search(search_dto)
    assert "Unexpected error while searching for organization" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_master_types_success(organization_service):
    from carestack.organization.organization_dto import MasterType

    mock_master_types = [MasterType(type="type1", desc="desc1")]
    mock_response_data = {"masterTypes": [{"type": "type1", "desc": "desc1"}]}
    mock_response_obj = MasterTypeResponse(masterTypes=mock_master_types)
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    response = await organization_service.get_master_types()
    assert isinstance(response, MasterTypeResponse)
    assert response.model_dump(by_alias=True) == mock_response_data
    organization_service.get.assert_called_with(
        UTILITY_API_ENDPOINTS.MASTER_TYPES, MasterTypeResponse
    )


@pytest.mark.asyncio
async def test_get_master_types_api_error(organization_service):
    organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_master_types()
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_master_types_unexpected_error(organization_service):
    organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_master_types()
    assert "Failed to get master types" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_master_data_success(organization_service):
    mock_response_data = {
        "type": "test_type",
        "data": [{"code": "d1", "value": "data1"}],
    }
    mock_response_obj = MasterDataResponse(**mock_response_data)
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    response = await organization_service.get_master_data("test_type")
    assert isinstance(response, MasterDataResponse)
    assert response.model_dump() == mock_response_data
    organization_service.get.assert_called_with(
        UTILITY_API_ENDPOINTS.MASTER_DATA_BY_TYPE.format(type="test_type"),
        MasterDataResponse,
    )


@pytest.mark.asyncio
async def test_get_master_data_api_error(organization_service):
    organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_master_data("test_type")
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_master_data_unexpected_error(organization_service):
    organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_master_data("test_type")
    assert "Failed to get master data of type" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_lgd_states_success(organization_service):
    mock_states_data = [
        LGDStatesResponse(
            code="S1",
            name="State1",
            districts=[LGDDistrictsResponse(code="D1", name="Dist1")],
        )
    ]
    mock_response_obj = LGDStatesListResponse(root=mock_states_data)
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    response = await organization_service.get_lgd_states()
    assert isinstance(response, LGDStatesListResponse)
    assert response == mock_response_obj
    organization_service.get.assert_called_with(
        UTILITY_API_ENDPOINTS.STATES_AND_DISTRICTS, LGDStatesListResponse
    )


@pytest.mark.asyncio
async def test_get_lgd_states_api_error(organization_service):
    organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_lgd_states()
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_lgd_states_unexpected_error(organization_service):
    organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_lgd_states()
    assert "Failed to get LGD states" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_lgd_sub_districts_success(organization_service):
    mock_data = [LGDDistrictsResponse(code="SD1", name="SubDistrict1")]
    mock_response_obj = LGDDistrictsListResponse(root=mock_data)
    organization_service.get = AsyncMock(return_value=mock_response_obj)
    response = await organization_service.get_lgd_sub_districts("test_district")
    assert isinstance(response, LGDDistrictsListResponse)
    assert response == mock_response_obj
    organization_service.get.assert_called_with(
        UTILITY_API_ENDPOINTS.SUBDISTRICTS.format(district_code="test_district"),
        LGDDistrictsListResponse,
    )


@pytest.mark.asyncio
async def test_get_lgd_sub_districts_invalid_response_type(organization_service):
    """Tests that get_lgd_sub_districts raises an error for an invalid response format."""
    organization_service.get = AsyncMock(return_value={"invalid": "response"})
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_lgd_sub_districts("test_district")
    assert "Invalid response format" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_lgd_sub_districts_api_error(organization_service):
    organization_service.get = AsyncMock(side_effect=EhrApiError("API Error", 500))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_lgd_sub_districts("test_district")
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_lgd_sub_districts_unexpected_error(organization_service):
    organization_service.get = AsyncMock(side_effect=Exception("Unexpected Error"))
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_lgd_sub_districts("test_district")
    assert "Failed to get LGD sub-districts for district code" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_organization_type_success(organization_service):
    mock_response_data = {
        "type": "facilityType",
        "data": [{"code": "HOSP", "value": "Hospital"}],
    }
    mock_response_obj = MasterDataResponse(**mock_response_data)
    organization_service.post = AsyncMock(return_value=mock_response_obj)
    request_body = OrganizationTypeRequest(
        ownershipCode="test_owner", systemOfMedicineCode="test_system"
    )
    response = await organization_service.get_organization_type(request_body)
    assert isinstance(response, MasterDataResponse)
    assert response.model_dump() == mock_response_data
    organization_service.post.assert_called_with(
        UTILITY_API_ENDPOINTS.ORGANIZATION_TYPE,
        {"ownershipCode": "test_owner", "systemOfMedicineCode": "test_system"},
        MasterDataResponse,
    )


@pytest.mark.asyncio
async def test_get_organization_type_validation_error(organization_service):
    """
    Tests that get_organization_type raises EhrApiError(400) for invalid input
    due to Pydantic validation failure triggered by __validate_data.
    """
    invalid_data = {"ownershipCode": ""}
    with pytest.raises(ValidationError) as exc_info:
        OrganizationTypeRequest(**invalid_data)

    assert "ownershipCode" in str(exc_info.value)
    assert "ownershipCode is required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_organization_type_api_error(organization_service):
    organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))
    request_body = OrganizationTypeRequest(
        ownershipCode="test_owner", systemOfMedicineCode="test_system"
    )
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_organization_type(request_body)
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_organization_type_unexpected_error(organization_service):
    organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))
    request_body = OrganizationTypeRequest(
        ownershipCode="test_owner", systemOfMedicineCode="test_system"
    )
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_organization_type(request_body)
    assert "Failed to get organization types" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_owner_subtypes_success(organization_service):
    mock_response_data = {
        "type": "ownerSubtype",
        "data": [{"code": "SUB1", "value": "Subtype 1"}],
    }
    mock_response_obj = MasterDataResponse(**mock_response_data)
    organization_service.post = AsyncMock(return_value=mock_response_obj)
    request_body = OwnershipSubTypeRequest(
        ownershipCode="test_owner", ownerSubtypeCode="test_subtype"
    )
    response = await organization_service.get_owner_subtypes(request_body)
    assert isinstance(response, MasterDataResponse)
    assert response.model_dump() == mock_response_data
    organization_service.post.assert_called_with(
        UTILITY_API_ENDPOINTS.OWNER_SUBTYPE,
        {"ownershipCode": "test_owner", "ownerSubtypeCode": "test_subtype"},
        MasterDataResponse,
    )


@pytest.mark.asyncio
async def test_get_owner_subtypes_validation_error(organization_service):
    """
    Tests that get_owner_subtypes raises EhrApiError(400) for invalid input
    due to Pydantic validation failure triggered by __validate_data.
    """
    invalid_data = {"ownershipCode": ""}
    with pytest.raises(ValidationError) as exc_info:
        OwnershipSubTypeRequest(**invalid_data)

    assert "ownershipCode" in str(exc_info.value)
    assert "ownershipCode is required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_owner_subtypes_api_error(organization_service):
    organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))
    request_body = OwnershipSubTypeRequest(
        ownershipCode="test_owner", ownerSubtypeCode="test_subtype"
    )
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_owner_subtypes(request_body)
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_owner_subtypes_unexpected_error(organization_service):
    organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))
    request_body = OwnershipSubTypeRequest(
        ownershipCode="test_owner", ownerSubtypeCode="test_subtype"
    )
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_owner_subtypes(request_body)
    assert "Failed to get owner subtypes" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_specialities_success(organization_service):
    mock_response_data = {
        "type": "specialities",
        "data": [{"code": "CARD", "value": "Cardiology"}],
    }
    mock_response_obj = MasterDataResponse(**mock_response_data)
    organization_service.post = AsyncMock(return_value=mock_response_obj)
    request_body = SpecialitiesRequest(systemOfMedicineCode="test_system")
    response = await organization_service.get_specialities(request_body)
    assert isinstance(response, MasterDataResponse)
    assert response.model_dump() == mock_response_data
    organization_service.post.assert_called_with(
        UTILITY_API_ENDPOINTS.SPECIALITIES,
        {"systemOfMedicineCode": "test_system"},
        MasterDataResponse,
    )


@pytest.mark.asyncio
async def test_get_specialities_validation_error(organization_service):
    """
    Tests that get_specialities raises EhrApiError(400) for invalid input
    due to Pydantic validation failure triggered by __validate_data.
    """
    invalid_data = {"systemOfMedicineCode": ""}
    with pytest.raises(ValidationError) as exc_info:
        SpecialitiesRequest(**invalid_data)

    assert "systemOfMedicineCode" in str(exc_info.value)
    assert "systemOfMedicineCode is required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_specialities_api_error(organization_service):
    organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))
    request_body = SpecialitiesRequest(systemOfMedicineCode="test_system")
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_specialities(request_body)
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_specialities_unexpected_error(organization_service):
    organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))
    request_body = SpecialitiesRequest(systemOfMedicineCode="test_system")
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_specialities(request_body)
    assert "Failed to get specialities" in str(exc_info.value)
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_organization_subtypes_success(organization_service):
    mock_response_data = {
        "type": "facilitySubType",
        "data": [{"code": "SUB1", "value": "SubType 1"}],
    }
    mock_response_obj = MasterDataResponse(**mock_response_data)
    organization_service.post = AsyncMock(return_value=mock_response_obj)
    request_body = OrganizationSubTypeRequest(facilityTypeCode="test_type")
    response = await organization_service.get_organization_subtypes(request_body)
    assert isinstance(response, MasterDataResponse)
    assert response.model_dump() == mock_response_data
    organization_service.post.assert_called_with(
        UTILITY_API_ENDPOINTS.ORGANIZATION_SUBTYPE,
        {"facilityTypeCode": "test_type"},
        MasterDataResponse,
    )


@pytest.mark.asyncio
async def test_get_organization_subtypes_validation_error(organization_service):
    """
    Tests that get_organization_subtypes raises EhrApiError(400) for invalid input
    due to Pydantic validation failure triggered by __validate_data.
    """
    invalid_data = {"facilityTypeCode": ""}
    with pytest.raises(ValidationError) as exc_info:
        OrganizationSubTypeRequest(**invalid_data)

    assert "facilityTypeCode" in str(exc_info.value)
    assert "facilityTypeCode is required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_organization_subtypes_api_error(organization_service):
    organization_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))
    request_body = OrganizationSubTypeRequest(facilityTypeCode="test_type")
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_organization_subtypes(request_body)
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_organization_subtypes_unexpected_error(organization_service):
    organization_service.post = AsyncMock(side_effect=Exception("Unexpected Error"))
    request_body = OrganizationSubTypeRequest(facilityTypeCode="test_type")
    with pytest.raises(EhrApiError) as exc_info:
        await organization_service.get_organization_subtypes(request_body)
    assert "Failed to get organization subtypes" in str(exc_info.value)
    assert exc_info.value.status_code == 500
