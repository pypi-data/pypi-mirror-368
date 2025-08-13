from typing import Annotated, Any, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    RootModel,
    StringConstraints,
    field_validator,
)

from carestack.common.enums import (
    Country,
)


class MasterType(BaseModel):
    """
    Represents a master type with a type and description.

    Attributes:
        type (str): The type identifier.
        desc (str): The description of the type.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    type: str = Field(..., alias="type")
    desc: str = Field(..., alias="desc")


class MasterTypeResponse(BaseModel):
    """
    Represents a response containing a list of master types.

    Attributes:
        master_types (list[MasterType]): List of master types.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    master_types: list[MasterType] = Field(..., alias="masterTypes")


class MasterData(BaseModel):
    """
    Represents a single master data entry with a code and value.

    Attributes:
        code (str): The code for the master data.
        value (str): The value for the master data.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    code: str
    value: str


class MasterDataResponse(BaseModel):
    """
    Represents a response containing a list of master data entries.

    Attributes:
        type (str): The type of master data.
        data (list[MasterData]): List of master data entries.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    type: str
    data: list[MasterData]


class LGDDistrictsResponse(BaseModel):
    """
    Represents a district with its code and name.

    Attributes:
        code (str): The district code.
        name (str): The district name.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    code: str
    name: str


class LGDDistrictsListResponse(RootModel[list[LGDDistrictsResponse]]):
    """
    Represents a list of LGD districts.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )


class LGDStatesResponse(LGDDistrictsResponse):
    """
    Represents a state with its code, name, and a list of districts.
    Inherits code and name from LGDDistrictsResponse.

    Attributes:
        districts (list[LGDDistrictsResponse]): List of districts in the state.
    """

    districts: list[LGDDistrictsResponse]


class LGDStatesListResponse(RootModel[list[LGDStatesResponse]]):
    """
    Represents a list of LGD states.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )


class LocationResponse(BaseModel):
    """
    Represents location response.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    lat: float
    lng: float


class GetOrganizationsResponse(BaseModel):
    """
    Represents the response for retrieving organization data.

    Attributes:
        message (Optional[str]): A message describing the response.
        data (Optional[Any]): The actual data returned in the response.
        next_page_link (Optional[str]): A link to the next page of results.
        total_number_of_records (Optional[int]): The total number of records available.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    message: Optional[str] = None
    data: Optional[Any] = None
    next_page_link: Optional[str] = Field(None, alias="nextPageLink")
    total_number_of_records: Optional[int] = Field(None, alias="totalNumberOfRecords")


PincodeType = Annotated[str, StringConstraints(pattern=r"^\d{6}$")]


class BasicInformation(BaseModel):
    """
    Represents the basic information of an organization.

    Attributes:
        organization_name (str): The name of the organization.
        region (str): The region where the organization is located.
        address_line1 (str): The first line of the organization's address.
        address_line2 (str): The second line of the organization's address.
        district (str): The district of the organization.
        sub_district (str): The sub-district of the organization.
        city (str): The city where the organization is located.
        state (str): The state or union territory.
        country (Country): The country of the organization.
        pincode (PincodeType): The pincode of the organization's location.
        lat_longs (list[str]): The latitude and longitude coordinates of the organization.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    organization_name: str = Field(..., min_length=1, alias="facilityName")
    region: str = Field(..., min_length=0)
    address_line1: str = Field(..., min_length=5, max_length=50, alias="addressLine1")
    address_line2: str = Field(..., min_length=5, max_length=50, alias="addressLine2")
    district: str = Field(..., min_length=1)
    sub_district: str = Field(..., min_length=1, alias="subDistrict")
    city: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    country: Country
    pincode: PincodeType
    lat_longs: list[str] = Field(..., min_length=1, alias="latLongs")


MobileNumberType = Annotated[
    str,
    StringConstraints(pattern=r"^\+?\d{1,3}[-.\s]?\d{1,14}$"),
    Field(alias="mobileNumber"),
]


class ContactInformation(BaseModel):
    """
    Represents the contact details of an organization.

    Attributes:
        mobile_number (MobileNumberType): The mobile number of the organization.
        email (EmailStr): The email address of the organization.
        landline (str): The landline number of the organization.
        stdcode (str): The STD code associated with the landline.
        website_link (str): The official website link of the organization.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    mobile_number: MobileNumberType
    email: EmailStr
    landline: str = Field(..., min_length=1)
    stdcode: str = Field(..., min_length=1)
    website_link: str = Field(..., min_length=1, alias="websiteLink")


class UploadDocuments(BaseModel):
    """
    Represents the document upload details for an organization.

    Attributes:
        board_photo (dict[str, str]): Must contain 'value' and 'name' keys.
        building_photo (dict[str, str]): Must contain 'value' and 'name' keys.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    board_photo: dict[str, str] = Field(
        ..., description="Must contain 'value' and 'name' keys", alias="boardPhoto"
    )
    building_photo: dict[str, str] = Field(
        ..., description="Must contain 'value' and 'name' keys", alias="buildingPhoto"
    )

    @field_validator("board_photo", "building_photo")
    @classmethod
    def validate_photo_keys(cls, v: dict[str, str]) -> dict[str, str]:
        if not all(key in v for key in ["value", "name"]):
            raise ValueError("Photo must contain 'value' and 'name' keys")
        return v


class AddAddressProof(BaseModel):
    """
    Represents an address proof document with type and attachment details.

    Attributes:
        address_proof_type (str): The type of address proof.
        address_proof_attachment (dict[str, str]): The attachment details, must contain 'value' and 'name' keys.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    address_proof_type: str = Field(..., min_length=1, alias="addressProofType")
    address_proof_attachment: dict[str, str] = Field(
        ...,
        description="Must contain 'value' and 'name' keys",
        alias="addressProofAttachment",
    )

    @field_validator("address_proof_attachment")
    @classmethod
    def validate_attachment_keys(cls, v: dict[str, str]) -> dict[str, str]:
        if not all(key in v for key in ["value", "name"]):
            raise ValueError("Attachment must contain 'value' and 'name' keys")
        return v


class OrganizationTimings(BaseModel):
    """
    Represents organization timings with multiple shifts.

    Attributes:
        timings (str): The timings description.
        shifts (list[dict[str, Optional[Any]]]): List of shift dictionaries, each with 'start' and 'end' keys.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    timings: str = Field(..., min_length=1)
    shifts: list[dict[str, Optional[Any]]] = Field(..., min_length=0)

    @field_validator("shifts", mode="before")
    @classmethod
    def validate_shifts(
        cls, v: list[dict[str, Optional[Any]]]
    ) -> list[dict[str, Optional[Any]]]:
        if not isinstance(v, list):
            raise ValueError("Shifts must be a list of dictionaries.")

        for shift in v:
            if not isinstance(shift, dict) or not all(
                key in shift for key in ["start", "end"]
            ):
                raise ValueError("Each shift must contain 'start' and 'end' keys.")
        return v


class OrganizationDetails(BaseModel):
    """
    Represents the details of an organization, including ownership type, subtype, and status.

    Attributes:
        ownership_type (str): The ownership type.
        ownership_sub_type (str): The ownership sub-type.
        status (str): The status of the organization.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    ownership_type: str = Field(..., min_length=1, alias="ownershipType")
    ownership_sub_type: str = Field(..., min_length=1, alias="ownershipSubType")
    status: str = Field(..., min_length=1)


class SystemOfMedicine(BaseModel):
    """
    Represents a system of medicine, including specialities, organization type, and service type.

    Attributes:
        specialities (list[dict[str, Any]]): List of specialities, each with 'systemofMedicineCode' and 'specialities' keys.
        organization_type (str): The organization type.
        organization_sub_type (str): The organization sub-type.
        service_type (str): The service type.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    specialities: list[dict[str, Any]] = Field(..., alias="specialities")
    organization_type: str = Field(..., alias="facilityType")
    organization_sub_type: str = Field(..., min_length=0, alias="facilitySubType")
    service_type: str = Field(..., min_length=0, alias="serviceType")

    @field_validator("specialities")
    @classmethod
    def validate_specialities(cls, v):
        for speciality in v:
            if not all(
                key in speciality for key in ["systemofMedicineCode", "specialities"]
            ):
                raise ValueError(
                    "Each speciality must contain 'systemofMedicineCode' and 'specialities' keys"
                )
            if not isinstance(speciality["specialities"], list):
                raise ValueError("'specialities' must be a list")
            if not isinstance(speciality["systemofMedicineCode"], str):
                raise ValueError("'systemofMedicineCode' must be a string")
        return v


class ImagingCenterServiceType(BaseModel):
    """
    Represents an imaging center service type with a service name and count.

    Attributes:
        service (str): The name of the imaging service.
        count (int): The count of the service.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    service: str = Field(..., min_length=0)
    count: int = Field(..., gt=-1)


class OrganizationInventory(BaseModel):
    """
    Represents the inventory details of a healthcare organization, including
    available ventilators, beds, and various organization attributes.

    Attributes:
        total_number_of_ventilators (int): Total number of ventilators.
        total_number_of_beds (int): Total number of beds.
        has_dialysis_center (str): Whether the organization has a dialysis center.
        has_pharmacy (str): Whether the organization has a pharmacy.
        has_blood_bank (str): Whether the organization has a blood bank.
        has_cath_lab (str): Whether the organization has a cath lab.
        has_diagnostic_lab (str): Whether the organization has a diagnostic lab.
        has_imaging_center (str): Whether the organization has an imaging center.
        services_by_imaging_center (list[ImagingCenterServiceType]): List of imaging center services.
        nhrrid (str): NHRR ID.
        nin (str): NIN.
        abpmjayid (str): ABPMJAY ID.
        rohini_id (str): ROHINI ID.
        echs_id (str): ECHS ID.
        cghs_id (str): CGHS ID.
        cea_registration (str): CEA registration.
        state_insurance_scheme_id (str): State insurance scheme ID.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    total_number_of_ventilators: int = Field(
        ..., gt=0, alias="totalNumberOfVentilators"
    )
    total_number_of_beds: int = Field(..., gt=0, alias="totalNumberOfBeds")
    has_dialysis_center: str = Field(..., min_length=1, alias="hasDialysisCenter")
    has_pharmacy: str = Field(..., min_length=1, alias="hasPharmacy")
    has_blood_bank: str = Field(..., min_length=1, alias="hasBloodBank")
    has_cath_lab: str = Field(..., min_length=1, alias="hasCathLab")
    has_diagnostic_lab: str = Field(..., min_length=1, alias="hasDiagnosticLab")
    has_imaging_center: str = Field(..., min_length=1, alias="hasImagingCenter")
    services_by_imaging_center: list[ImagingCenterServiceType] = Field(
        ..., min_length=0, alias="servicesByImagingCenter"
    )
    nhrrid: str = Field(..., min_length=0)
    nin: str = Field(..., min_length=0)
    abpmjayid: str = Field(..., min_length=0)
    rohini_id: str = Field(..., min_length=0, alias="rohiniId")
    echs_id: str = Field(..., min_length=0, alias="echsId")
    cghs_id: str = Field(..., min_length=0, alias="cghsId")
    cea_registration: str = Field(..., min_length=0, alias="ceaRegistration")
    state_insurance_scheme_id: str = Field(
        ..., min_length=0, alias="stateInsuranceSchemeId"
    )

    @field_validator("services_by_imaging_center")
    @classmethod
    def validate_services_by_imaging_center(cls, v):
        if len(v) == 1 and v[0].service == "" and v[0].count == 0:
            return v
        for service in v:
            if not isinstance(service.service, str) or not isinstance(
                service.count, int
            ):
                raise ValueError("Each service must contain 'service' and 'count' keys")
        return v


class AddOrganizationDTO(BaseModel):
    """
    Represents the data transfer object for adding a new healthcare organization.

    This includes organization-related information such as basic details, contact
    information, documents, address proof, timings, details, system of medicine,
    inventory, and account identifiers.

    Attributes:
        basic_information (BasicInformation): Basic information about the organization.
        contact_information (ContactInformation): Contact details.
        upload_documents (UploadDocuments): Uploaded documents.
        add_address_proof (list[AddAddressProof]): List of address proof documents.
        organization_timings (list[OrganizationTimings]): Organization timings.
        organization_details (OrganizationDetails): Organization details.
        system_of_medicine (SystemOfMedicine): System of medicine information.
        organization_inventory (OrganizationInventory): Inventory details.
        account_id (str): Account ID.
        organization_id (Optional[str]): Organization ID.
        id (Optional[str]): Internal ID.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    basic_information: BasicInformation = Field(..., alias="basicInformation")
    contact_information: ContactInformation = Field(..., alias="contactInformation")
    upload_documents: UploadDocuments = Field(..., alias="uploadDocuments")
    add_address_proof: list[AddAddressProof] = Field(..., alias="addAddressProof")
    organization_timings: list[OrganizationTimings] = Field(
        ..., alias="facilityTimings"
    )
    organization_details: OrganizationDetails = Field(..., alias="facilityDetails")
    system_of_medicine: SystemOfMedicine = Field(..., alias="systemOfMedicine")
    organization_inventory: OrganizationInventory = Field(
        ..., alias="facilityInventory"
    )
    account_id: str = Field(..., min_length=1, alias="accountId")
    organization_id: Optional[str] = Field(None, alias="facilityId")
    id: Optional[str] = None


class UpdateOrganizationDTO(BaseModel):
    """
    Represents the data transfer object for updating organization details.

    This includes fields related to the organization's Single Point of Contact (SPOC),
    along with optional consent manager details.

    Attributes:
        spoc_name (str): Name of the SPOC.
        id (str): Organization ID.
        spoc_id (str): SPOC ID.
        consent_manager_name (Optional[str]): Consent manager name.
        consent_manager_id (Optional[str]): Consent manager ID.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    spoc_name: str = Field(..., min_length=1, alias="spocName")
    id: str = Field(..., min_length=1)
    spoc_id: str = Field(..., min_length=1, alias="spocId")
    consent_manager_name: Optional[str] = Field(None, alias="consentManagerName")
    consent_manager_id: Optional[str] = Field(None, alias="consentManagerId")


class SearchOrganizationDTO(BaseModel):
    """
    Represents the data transfer object for searching facilities.

    Attributes:
        ownership_code (Optional[str]): The ownership code of the organization.
        state_lgd_code (Optional[str]): The LGD code of the state.
        district_lgd_code (Optional[str]): The LGD code of the district.
        sub_district_lgd_code (Optional[str]): The LGD code of the sub-district.
        pincode (Optional[str]): The pincode of the organization's location.
        organization_name (Optional[str]): The name of the organization.
        organization_id (Optional[str]): The ID of the organization.
        page (int): The page number for pagination.
        results_per_page (int): The number of results per page for pagination.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    ownership_code: Optional[str] = Field(None, alias="ownershipCode")
    state_lgd_code: Optional[str] = Field(None, alias="stateLGDCode")
    district_lgd_code: Optional[str] = Field(None, alias="districtLGDCode")
    sub_district_lgd_code: Optional[str] = Field(None, alias="subDistrictLGDCode")
    pincode: Optional[str] = Field(
        None,
        pattern=r"^\d{6}$",
        alias="pincode",
        description="Pincode must be a 6-digit number",
    )
    organization_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
        alias="facilityName",
        description="organization name must be between 3 and 200 characters",
    )
    organization_id: Optional[str] = Field(None, alias="facilityId")
    page: int = Field(..., gt=0, description="Page number must be at least 1")
    results_per_page: int = Field(
        ...,
        gt=0,
        le=100,
        alias="resultsPerPage",
        description="Results per page must be between 1 and 100",
    )


class Organization(BaseModel):
    """
    Represents an organization.

    Attributes:
        organization_id (str): The ID of the organization.
        organization_name (str): The name of the organization.
        organization_status (str): The status of the organization.
        ownership (str): The ownership of the organization.
        ownership_code (str): The ownership code of the organization.
        system_of_medicine_code (str): The system of medicine code of the organization.
        system_of_medicine (str): The system of medicine of the organization.
        organization_type_code (str): The organization type code of the organization.
        organization_type (str): The organization type of the organization.
        state_name (str): The name of the state.
        state_lgd_code (str): The LGD code of the state.
        district_name (str): The name of the district.
        district_lgd_code (str): The LGD code of the district.
        sub_district_name (str): The name of the sub-district.
        sub_district_lgd_code (str): The LGD code of the sub-district.
        village_city_town_name (Optional[str]): The name of the village, city, or town.
        village_city_town_lgd_code (str): The LGD code of the village, city, or town.
        address (str): The address of the organization.
        pincode (str): The pincode of the organization.
        latitude (str): The latitude of the organization's location.
        longitude (str): The longitude of the organization's location.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    organization_id: str = Field(..., alias="facilityId")
    organization_name: str = Field(..., alias="facilityName")
    organization_status: str = Field(..., alias="facilityStatus")
    ownership: str = Field(...)
    ownership_code: str = Field(..., alias="ownershipCode")
    system_of_medicine_code: str = Field(..., alias="systemOfMedicineCode")
    system_of_medicine: str = Field(..., alias="systemOfMedicine")
    organization_type_code: str = Field(..., alias="facilityTypeCode")
    organization_type: str = Field(..., alias="facilityType")
    state_name: str = Field(..., alias="stateName")
    state_lgd_code: str = Field(..., alias="stateLGDCode")
    district_name: str = Field(..., alias="districtName")
    district_lgd_code: str = Field(..., alias="districtLGDCode")
    sub_district_name: str = Field(..., alias="subDistrictName")
    sub_district_lgd_code: str = Field(..., alias="subDistrictLGDCode")
    village_city_town_name: Optional[str] = Field(None, alias="villageCityTownName")
    village_city_town_lgd_code: str = Field(..., alias="villageCityTownLGDCode")
    address: str = Field(...)
    pincode: str = Field(...)
    latitude: str = Field(...)
    longitude: str = Field(...)


class SearchOrganizationResponse(BaseModel):
    """
    Represents the response for searching facilities.

    Attributes:
        organizations (list[Organization]): A list of organizations.
        message (str): A message describing the response.
        total_organizations (int): The total number of organizations.
        number_of_pages (int): The number of pages.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    organizations: list[Organization] = Field(..., alias="facilities")
    message: str = Field(...)
    total_organizations: int = Field(..., alias="totalFacilities")
    number_of_pages: int = Field(..., alias="numberOfPages")


class OrganizationTypeRequest(BaseModel):
    """
    Represents the request body for fetching organization types.

    Attributes:
        ownership_code (str): The ownership code. Required.
        system_of_medicine_code (Optional[str]): The system of medicine code. Optional.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    ownership_code: str = Field(..., alias="ownershipCode")
    system_of_medicine_code: Optional[str] = Field(None, alias="systemOfMedicineCode")

    @field_validator("ownership_code")
    @classmethod
    def validate_ownership_code(cls, value):
        if not value:
            raise ValueError("ownershipCode is required")
        return value

    @field_validator("system_of_medicine_code")
    @classmethod
    def validate_system_of_medicine_code(cls, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("systemOfMedicineCode must be a string")
        return value


class OwnershipSubTypeRequest(BaseModel):
    """
    Represents the request body for fetching ownership subtypes.

    Attributes:
        ownership_code (str): The ownership code. Required.
        owner_subtype_code (Optional[str]): The owner subtype code. Optional.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    ownership_code: str = Field(..., alias="ownershipCode")
    owner_subtype_code: Optional[str] = Field(None, alias="ownerSubtypeCode")

    @field_validator("ownership_code")
    @classmethod
    def validate_ownership_code(cls, value):
        if not value:
            raise ValueError("ownershipCode is required")
        return value

    @field_validator("owner_subtype_code")
    @classmethod
    def validate_owner_subtype_code(cls, value):
        if value is not None and not isinstance(value, str):
            raise ValueError("ownerSubtypeCode must be a string")
        return value


class SpecialitiesRequest(BaseModel):
    """
    Represents the request body for fetching specialities.

    Attributes:
        system_of_medicine_code (str): The system of medicine code. Required.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    system_of_medicine_code: str = Field(..., alias="systemOfMedicineCode")

    @field_validator("system_of_medicine_code")
    @classmethod
    def validate_system_of_medicine_code(cls, value):
        if not value:
            raise ValueError("systemOfMedicineCode is required")
        return value


class OrganizationSubTypeRequest(BaseModel):
    """
    Represents the request body for fetching organization subtypes.

    Attributes:
        organization_type_code (str): The organization type code. Required.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    organization_type_code: str = Field(..., alias="facilityTypeCode")

    @field_validator("organization_type_code")
    @classmethod
    def validate_organization_type_code(cls, value):
        if not value:
            raise ValueError("facilityTypeCode is required")
        return value
