import logging
from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

from carestack.base.base_service import BaseService
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import (
    UTILITY_API_ENDPOINTS,
    OrganizationsIdType,
    OrganizationEndPoints,
)
from carestack.organization.organization_dto import (
    AddOrganizationDTO,
    GetOrganizationsResponse,
    LGDDistrictsListResponse,
    LGDStatesListResponse,
    LocationResponse,
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


class GetJsonFromTextResponse(BaseModel):
    response: str


class Organization(BaseService):
    """
    SDK-friendly service for managing organization-related operations.

    This service provides a comprehensive interface for interacting with the CareStack
    organization API. It supports operations such as creating, updating, deleting, and searching
    organizations, as well as fetching master data types and LGD administrative data.

    It internally validates all input data using Pydantic DTOs, manages request formatting,
    and gracefully handles errors with comprehensive logging.

    !!! note "Key Features"
        - Asynchronous operations for non-blocking I/O.
        - Strongly typed request and response models using Pydantic.
        - Error handling with custom exceptions for API failures.
        - Support for complex search queries and pagination.
        - Utility methods to fetch master data types and LGD administrative data.

    Methods:
        create: Registers a new organization.
        find_all: Retrieves all organizations with optional pagination.
        find_by_id: Fetches an organization by a specific ID type and value.
        exists: Checks if an organization exists by ID type and value.
        update: Updates an existing organization's information.
        delete: Deletes an organization by its unique ID.
        search: Searches for organizations based on complex criteria.
        get_master_types: Retrieves master types of organizations.
        get_master_data: Fetches master data for a specific type (e.g., ownership, organization type).
        get_lgd_states: Retrieves all states with their districts.
        get_lgd_sub_districts: Retrieves sub-districts for a given district code.
        get_organization_type: Retrieves organization types based on ownership and optional system of medicine.
        get_owner_subtypes: Retrieves ownership subtypes for a given ownership code.
        get_specialities: Retrieves specialities associated with a system of medicine.
        get_organization_subtypes: Retrieves organization subtypes for a given organization type code.

    Args:
        config (ClientConfig): Configuration object with API connection and authentication details.

    Raises:
        EhrApiError: If any API request fails or validation errors occur.

    Example Usage:
        ```
        config = ClientConfig(api_key="your_api_key",hprid_auth="your_auth_token")
        organization_service = Organization(config)

        # Register a new organization
        new_org_data = {
            "basicInformation": {
                "facilityName": "City Hospital",
                "region": "East Zone",
                "addressLine1": "123 Main Street",
                "addressLine2": "Near City Mall",
                "district": "District One",
                "subDistrict": "Subdistrict A",
                "city": "Metropolis",
                "state": "State X",
                "country": "IN",
                "pincode": "123456",
                "latLongs": ["28.6139,77.2090"]
            },
            ...
        }
        message = await organization_service.create(new_org_data)
        print(message)  # e.g., "Organization registered successfully."
        ```

    """

    def __init__(self, config: ClientConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    async def __validate_data(
        self, dto_type: Type[BaseModel], request_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validates request data using Pydantic models.

        Args:
            dto_type (Type[BaseModel]): Pydantic model class for validation.
            request_data (dict[str, Any]): Data to be validated.

        Returns:
            dict[str, Any]: Validated data as a dictionary.

        Raises:
            EhrApiError: If validation fails.
        """
        try:
            validated_data = dto_type(**request_data)
            return validated_data.model_dump(by_alias=True)
        except ValidationError as e:
            self.logger.error("Validation failed: %s", e.json())
            raise EhrApiError(f"Validation failed: {e}", 400) from e

    async def create(self, organization: dict[str, Any]) -> str:
        """
        Registers a new organization.

        Args:
            organization (AddOrganizationDTO): Data for the new organization, validated via AddOrganizationDTO.

        Returns:
            str: Response message indicating success or error description.

        Raises:
            EhrApiError: On validation or API request failure.

        Example:
            ```
            message = await organization_service.create(new_org_data)
            print(message)  # "Organization registered successfully."
            ```
        ### Response:
            Sample Output:
             "Organization registered successfully."
        """

        try:
            validated_data = await self.__validate_data(
                AddOrganizationDTO, organization
            )
            response = await self.post(
                OrganizationEndPoints.REGISTER_ORGANIZATION,
                validated_data,
                response_model=GetJsonFromTextResponse,
            )
            return response.response
        except EhrApiError:
            raise
        except Exception as e:
            self.logger.error("Error registering organization: %s", e)
            raise EhrApiError(f"Failed to register organization: {e}", 500) from e

    async def find_all(
        self, next_page: Optional[str] = None
    ) -> GetOrganizationsResponse:
        """
        Retrieves all organizations with optional pagination.

        Args:
            next_page (Optional[str]): Token for fetching next page of results.

        Returns:
            GetOrganizationsResponse: Includes organization list, pagination tokens, and total count.

        Raises:
            EhrApiError: On API communication failures.

        Example:
            ```
            response = await organization_service.find_all()
            print(response.data)
            if response.next_page:
                print("More results available at:", response.next_page)
            ```
        ### Response:
            Sample Output:
             {
            "data": [
                {
                    "organizationId": "org123",
                    "organizationName": "City Hospital",
                    "district": "District One",
                    "pincode": "110001",
                    "state": "State X",
                    "country": "IN"
                },
                {
                    "organizationId": "org456",
                    "organizationName": "Another Hospital",
                    "district": "District Two",
                    "pincode": "110002",
                    "state": "State Y",
                    "country": "IN"
                }
            ],
            "nextPage": "token_for_next_page",
            "total": 5
             }
        """
        try:
            params = {"nextPage": next_page} if next_page else None
            response = await self.get(
                OrganizationEndPoints.GET_ALL_ORGANIZATIONS,
                GetOrganizationsResponse,
                params,
            )
            if not isinstance(response, GetOrganizationsResponse):
                raise EhrApiError("Invalid response format", 500)
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error fetching facilities: %s", str(e))
            raise EhrApiError(f"Failed to fetch facilities: {e}", 500) from e

    async def find_by_id(
        self, search_param: OrganizationsIdType, search_term: str
    ) -> GetOrganizationsResponse:
        """
        Retrieves an organization by a specific ID type and its corresponding value.

        Args:
            search_param (OrganizationsId): Enum specifying ID type (e.g., ACCOUNT_ID, ORGANIZATION_ID).
            search_term (str): The unique identifier value.

        Returns:
            GetOrganizationsResponse: Detailed organization information.

        Raises:
            EhrApiError: On invalid IDs or request errors.

        Example:
            ```
            org = await organization_service.find_by_id(OrganizationsId.ORGANIZATION_ID, "org123")
            print(org.data)
            ```
        ### Response:
            Sample Output:
             {
            "data": {
                "organizationId": "org123",
                "organizationName": "City Hospital",
                "district": "District One",
                "pincode": "110001",
                "state": "State X",
                "country": "IN"
            }
             }
        """
        try:
            response = await self.get(
                OrganizationEndPoints.GET_ORGANIZATION_BY_ID.format(
                    search_param=search_param.value, search_term=search_term
                ),
                GetOrganizationsResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "Error fetching organization by ID %s: %s", search_term, e
            )
            raise EhrApiError(
                f"Failed to fetch organization with ID: {search_term}", 500
            ) from e

    async def exists(self, search_param: OrganizationsIdType, search_term: str) -> bool:
        """
        Checks whether an organization exists given a specific ID and its value.

        Args:
            search_param (OrganizationsIdType): The ID type (e.g., ACCOUNT_ID, ORGANIZATION_ID).
            search_term (str): The unique ID value.

        Returns:
            bool: True if the organization exists; otherwise False.

        Raises:
            EhrApiError: On API failures.

        Example:
            ```
            exists = await organization_service.exists(OrganizationsId.ORGANIZATION_ID, "org123")
            print(exists)
            ```
        ### Response:
            Sample Output:
             True or False depending on existence of organization with ID `search_term`.
        """
        try:
            response = await self.get(
                OrganizationEndPoints.ORGANIZATION_EXISTS.format(
                    search_param=search_param.value, search_term=search_term
                ),
                GetOrganizationsResponse,
            )
            if search_param == OrganizationsIdType.ORGANIZATION_ID:
                return response.message == "Facility Found !!!"
            elif search_param == OrganizationsIdType.ACCOUNT_ID:
                return response.message == "Records Found!!"
        except EhrApiError as e:
            if e.status_code == 404:
                return False
            raise e
        except Exception as e:
            self.logger.error(
                "Error checking existence of organization %s: %s", search_term, e
            )
            raise EhrApiError(
                f"Error while checking organization {search_term}: {e}", 500
            ) from e

    async def update(self, update_organization_data: UpdateOrganizationDTO) -> str:
        """
        Updates an existing organization's information.

        Args:
            update_organization_data (UpdateOrganizationDTO): Data including organization update fields.

        Returns:
            str: Response message from the update operation.

        Raises:
            EhrApiError: On validation or API request failure.

        Example:
            ```
            update_info = UpdateOrganizationDTO(
                id="org123",
                spocName="Dr. Smith",
                spocId="spoc001",
                consentManagerName="Manager Name",
                consentManagerId="cm001"
            )
            message = await organization_service.update(update_info)
            print(message)  # "Organization updated successfully."
            ```
        ### Response:
            Sample Output:
             "Organization updated successfully."
        """

        try:
            validated_data = await self.__validate_data(
                UpdateOrganizationDTO,
                update_organization_data.model_dump(by_alias=True),
            )
            response = await self.put(
                OrganizationEndPoints.UPDATE_ORGANIZATION,
                validated_data,
                GetJsonFromTextResponse,
            )
            return response.response
        except EhrApiError:
            raise
        except Exception as e:
            self.logger.error("Error updating organization: %s", e)
            raise EhrApiError(f"Failed to update organization: {e}", 500) from e

    async def delete(self, organization_id: str) -> str:
        """
        Deletes an organization by its unique ID.

        Args:
            organization_id (str): The unique ID of the organization to delete.

        Returns:
            str: Response message indicating success or failure.

        Raises:
            EhrApiError: On invalid IDs or unsuccessful deletion.

        Example:
            ```
            message = await organization_service.delete("org123")
            print(message)  # "Organization deleted successfully."
            ```
        ### Response:
            Sample Output:
             "Organization deleted successfully."

            ### Raises:
            EhrApiError: If the organization ID is invalid or deletion fails.
        """
        if not organization_id:
            raise EhrApiError("Organization ID cannot be null or empty.", 400)
        try:
            await super().delete(
                OrganizationEndPoints.DELETE_ORGANIZATION.format(
                    organization_id=organization_id
                )
            )

        except EhrApiError:
            raise
        except Exception as e:
            self.logger.error("Error deleting organization %s: %s", organization_id, e)
            raise EhrApiError(
                f"Failed to delete organization {organization_id}: {e}", 500
            ) from e

    async def search(
        self, search_organization_data: SearchOrganizationDTO
    ) -> SearchOrganizationResponse:
        """
        Searches for organizations based on complex criteria.

        Args:
            search_organization_data (SearchOrganizationDTO): DTO containing search parameters, including location, type, etc.

        Returns:
            SearchOrganizationResponse: Contains matching organizations and pagination info.

        Raises:
            EhrApiError: On validation failure or API request errors.

        Example:
            ```
            criteria = SearchOrganizationDTO(
                organizationName="City Hospital",
                districtLGDCode="DL01",
                pincode="110001",
                page=1,
                resultsPerPage=20
            )
            response = await organization_service.search(criteria)
            print(f"Found {response.total} organizations matching criteria.")
            for org in response.organizations:
                print(org.organization_name, org.district)
            ```
        ### Response:
            Sample Output:
             {            "total": 5,
            "page": 1,
            "resultsPerPage": 20,
            "organizations": [
                {
                    "organizationId": "org123",
                    "organizationName": "City Hospital",
                    "district": "District One",
                    "pincode": "110001",
                    "state": "State X",
                    "country": "IN"
                },
                {
                    "organizationId": "org456",
                    "organizationName": "Another Hospital",
                    "district": "District Two",
                    "pincode": "110002",
                    "state": "State Y",
                    "country": "IN"
                }
            ]
             }
        """
        try:
            validated_data = await self.__validate_data(
                SearchOrganizationDTO,
                search_organization_data.model_dump(by_alias=True),
            )
            response = await self.post(
                OrganizationEndPoints.SEARCH_ORGANIZATION,
                validated_data,
                SearchOrganizationResponse,
            )
            return response
        except EhrApiError as e:
            self.logger.error(f"Error while searching for organization: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error while searching for organization: {e}")
            raise EhrApiError(
                f"Unexpected error while searching for organization: {e}", 500
            ) from e

    async def get_master_types(self) -> MasterTypeResponse:
        """
        Retrieves master types of organizations from the utility API.

        Returns:
            MasterTypeResponse: List of master types with descriptions.

        Raises:
            EhrApiError: On API request failure.

        Example:
            ```
            master_types = await organization_service.get_master_types()
            for mt in master_types.master_types:
                print(mt.type, mt.desc)
            ```
        ### Response:
            Sample Output:
             {
            "master_types": [
                {"type": "ownershipType", "desc": "Ownership Type"},
                {"type": "organizationType", "desc": "Organization Type"},
                {"type": "specialities", "desc": "Specialities"}
            ]
             }
        """
        try:
            response = await self.get(
                UTILITY_API_ENDPOINTS.MASTER_TYPES, MasterTypeResponse
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting master types: %s", e)
            raise EhrApiError(f"Failed to get master types: {e}", 500) from e

    async def get_master_data(self, data_type: str) -> MasterDataResponse:
        """
        Retrieves master data of a given type from the utility API.

        Args:
            data_type (str): The type of master data to fetch, e.g., "ownershipType", "organizationType", etc.

        Returns:
            MasterDataResponse: List of key-value master data pairs.

        Raises:
            EhrApiError: On invalid data type or API failure.

        Example:
            ```
            ownership_types = await organization_service.get_master_data("ownershipType")
            for item in ownership_types.data:
                print(item.code, item.value)
            ```
        ### Response:
            Sample Output:
             {
            "data": [
                {"code": "GOV", "value": "Government"},
                {"code": "PRV", "value": "Private"}
            ],
            "type": "ownershipType"
             }
        """
        try:
            response = await self.get(
                UTILITY_API_ENDPOINTS.MASTER_DATA_BY_TYPE.format(type=data_type),
                MasterDataResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(f"Error getting master data of type {data_type}: {e}")
            raise EhrApiError(
                f"Failed to get master data of type {data_type}: {e}", 500
            ) from e

    async def get_lgd_states(self) -> LGDStatesListResponse:
        """
        Retrieves all states with their districts from the LGD (Local Government Directory) API.

        Returns:
            LGDStatesListResponse: List of states, each containing a list of districts.

        Raises:
            EhrApiError: On API communication failure or invalid response.

        Example:
            ```
            states = await organization_service.get_lgd_states()
            for state in states.root:
                print(state.code, state.name)
                for district in state.districts:
                    print("  -", district.code, district.name)
            ```
        ### Response:
            Sample Output:
             {
                {"code": "DL", "name": "Delhi", "districts": [
                    {"code": "DL01", "name": "District One"},
                    {"code": "DL02", "name": "District Two"}
                ]},
        """
        try:
            response = await self.get(
                UTILITY_API_ENDPOINTS.STATES_AND_DISTRICTS, LGDStatesListResponse
            )
            if not isinstance(response, LGDStatesListResponse):
                raise EhrApiError(
                    "Invalid response format from LGD states API: Expected a list.", 500
                )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting LGD states: %s", e)
            raise EhrApiError(f"Failed to get LGD states: {e}", 500) from e

    async def get_lgd_sub_districts(
        self, district_code: str
    ) -> LGDDistrictsListResponse:
        """
        Retrieves sub-districts for a given district code from the LGD API.

        Args:
            district_code (str): The code identifying the district.

        Returns:
            LGDDistrictsListResponse: List of sub-districts.

        Raises:
            EhrApiError: On invalid district code or API failures.

        Example:
            ```
            subdistricts = await organization_service.get_lgd_districts("DL01")
            for sd in subdistricts.root:
                print(sd.code, sd.name)
            ```
        ### Response:
            Sample Output:
             {
            "root": [
                {"code": "DL01", "name": "Subdistrict A"},
                {"code": "DL02", "name": "Subdistrict B"}
            ]
             }
        """
        try:
            response = await self.get(
                UTILITY_API_ENDPOINTS.SUBDISTRICTS.format(district_code=district_code),
                LGDDistrictsListResponse,
            )
            if not isinstance(response, LGDDistrictsListResponse):
                raise EhrApiError(
                    "Invalid response format from LGD states API: Expected a list.", 500
                )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error(
                "Error getting LGD sub-districts for district code %s: %s",
                district_code,
                e,
            )
            raise EhrApiError(
                f"Failed to get LGD sub-districts for district code {district_code}: {e}",
                500,
            ) from e

    async def get_organization_type(
        self, request_body: OrganizationTypeRequest
    ) -> MasterDataResponse:
        """
        Retrieves organization types based on given ownership and optional system of medicine.

        Args:
            request_body (OrganizationTypeRequest): DTO specifying ownership code and optional systemOfMedicineCode.

        Returns:
            MasterDataResponse: List of organization types.

        Raises:
            EhrApiError: On validation or API failure.

        Example:
            ```
            request = OrganizationTypeRequest(ownershipCode="GOV", systemOfMedicineCode="AYUSH")
            types = await organization_service.get_organization_type(request)
            for t in types.data:
                print(t.code, t.value)
            ```
        ### Response:
            Sample Output:
             {
            "data": [
                {"code": "HOSP", "value": "Hospital"},
                {"code": "CLINIC", "value": "Clinic"},
                {"code": "LAB", "value": "Laboratory"}
            ],
            "type": "organizationType"
             }
        """
        try:
            validated_data = await self.__validate_data(
                OrganizationTypeRequest, request_body.model_dump(by_alias=True)
            )
            response = await self.post(
                UTILITY_API_ENDPOINTS.ORGANIZATION_TYPE,
                validated_data,
                MasterDataResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting organization types: %s", e)
            raise EhrApiError(f"Failed to get organization types: {e}", 500) from e

    async def get_owner_subtypes(
        self, request_body: OwnershipSubTypeRequest
    ) -> MasterDataResponse:
        """
        Retrieves ownership subtypes for a given ownership code and optional subtype code.

        Args:
            request_body (OwnershipSubTypeRequest): DTO specifying ownership code and optional owner subtype code.

        Returns:
            MasterDataResponse: List of ownership subtypes.

        Raises:
            EhrApiError: On validation or API failure.

        Example:
            ```
            request = OwnershipSubTypeRequest(ownershipCode="PRV")
            subtypes = await organization_service.get_owner_subtypes(request)
            for s in subtypes.data:
                print(s.code, s.value)
            ```
        ### Response:
            Sample Output:
             {
            "data": [
                {"code": "PRV", "value": "Private"},
                {"code": "GOV", "value": "Government"}
            ],
            "type": "ownershipSubType"
             }
        """
        try:
            validated_data = await self.__validate_data(
                OwnershipSubTypeRequest, request_body.model_dump(by_alias=True)
            )
            response = await self.post(
                UTILITY_API_ENDPOINTS.OWNER_SUBTYPE, validated_data, MasterDataResponse
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting owner subtypes: %s", e)
            raise EhrApiError(f"Failed to get owner subtypes: {e}", 500) from e

    async def get_specialities(
        self, request_body: SpecialitiesRequest
    ) -> MasterDataResponse:
        """
        Retrieves specialities associated with a given system of medicine.

        Args:
            request_body (SpecialitiesRequest): DTO specifying systemOfMedicineCode.

        Returns:
            MasterDataResponse: List of specialities.

        Raises:
            EhrApiError: On request failure or invalid input.

        Example:
            ```
            request = SpecialitiesRequest(systemOfMedicineCode="ALL")
            specialities = await organization_service.get_specialities(request)
            for sp in specialities.data:
                print(sp.code, sp.value)
            ```
        ### Response:
            Sample Output:
             {
            "data": [
                {"code": "ALL", "value": "All"},
                {"code": "CARD", "value": "Cardiology"},
                {"code": "NEURO", "value": "Neurology"}
            ],
            "type": "specialities"
             }
        """
        try:
            validated_data = await self.__validate_data(
                SpecialitiesRequest, request_body.model_dump(by_alias=True)
            )
            response = await self.post(
                UTILITY_API_ENDPOINTS.SPECIALITIES, validated_data, MasterDataResponse
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting specialities: %s", e)
            raise EhrApiError(f"Failed to get specialities: {e}", 500) from e

    async def get_organization_subtypes(
        self, request_body: OrganizationSubTypeRequest
    ) -> MasterDataResponse:
        """
        Retrieves organization subtypes for a given organization type code.

        Args:
            request_body (OrganizationSubTypeRequest): DTO specifying organization type code.

        Returns:
            MasterDataResponse: List of organization subtypes.

        Raises:
            EhrApiError: On validation or API failure.

        Example:
            ```
            request = OrganizationSubTypeRequest(facilityType="HOSP")
            subtypes = await organization_service.get_organization_subtypes(request)
            for st in subtypes.data:
                print(st.code, st.value)
            ```
        ### Response:
            Sample Output:
             {
            "data": [
                {"code": "HOSP", "value": "Hospital"},
                {"code": "CLINIC", "value": "Clinic"}
            ],
            "type": "organizationSubType",
             }
        """
        try:
            validated_data = await self.__validate_data(
                OrganizationSubTypeRequest, request_body.model_dump(by_alias=True)
            )
            response = await self.post(
                UTILITY_API_ENDPOINTS.ORGANIZATION_SUBTYPE,
                validated_data,
                MasterDataResponse,
            )
            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting organization subtypes: %s", e)
            raise EhrApiError(f"Failed to get organization subtypes: {e}", 500)

    async def get_location(self, address: str) -> LocationResponse:
        """
        Retrieves location information for a given address.

        Args:
            address (str): The address for which to retrieve location information.

        Returns:
            LocationResponse:

        Example:
            ```
            location = await organization_service.get_location("123 Main St, City")
            print(location.lat, location.lng)
            ```
        ### Response:
            Sample Output:
             {
            "lat": "28.6139",
            "lng": "77.2090"
             }

        """
        try:
            self.logger.info("Location response: %s", address)
            response = await self.get(
                UTILITY_API_ENDPOINTS.LOCATION.format(address=address),
                LocationResponse,
            )

            return response
        except EhrApiError as e:
            raise e
        except Exception as e:
            self.logger.error("Error getting location : %s", e)
            raise EhrApiError(f"Failed to get location: {e}", 500)
