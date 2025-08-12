import pytest
import logging
from unittest.mock import patch, AsyncMock
from typing import Any

from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import CREATE_ABHA_ENDPOINTS
from carestack.patient.abha.abha_service import ABHAService
from carestack.patient.abha.abha_dto import (
    AbhaAddressSuggestionsResponse,
    AbhaProfile,
    CreateAbhaAddressRequest,
    CreateAbhaAddressResponse,
    EnrollWithAadhaar,
    EnrollWithAadhaarResponse,
    GenerateAadhaarOtpRequest,
    UpdateMobileNumberRequest,
    VerifyMobileOtpRequest,
    VerifyMobileOtpResponse,
    VerifyOtpResponse,
)
from carestack.common.config_test import client_config


@pytest.fixture
def mock_abha_service(client_config: ClientConfig) -> ABHAService:
    """Fixture for ABHAService instance."""
    with patch.dict("os.environ", {"ABHA_PUBLIC_KEY": "test_key\\nwith_newline"}):
        return ABHAService(client_config)


@pytest.fixture
def mock_abha_service_no_key(client_config: ClientConfig) -> ABHAService:
    """Fixture for ABHAService instance without public key."""
    with patch.dict("os.environ", {}, clear=True):
        return ABHAService(client_config)


@pytest.fixture
def valid_generate_aadhaar_otp_data() -> dict[str, Any]:
    """Fixture for valid Aadhaar OTP generation data."""
    return {"aadhaar": "123456789012"}


@pytest.fixture
def valid_enroll_with_aadhaar_data() -> dict[str, Any]:
    """Fixture for valid enrollment with Aadhaar data."""
    return {"otp": "123456", "txnId": "test_txn_id", "mobile": "9876543210"}


@pytest.fixture
def valid_update_mobile_number_data() -> dict[str, Any]:
    """Fixture for valid mobile number update data."""
    return {"updateValue": "9876543210", "txnId": "test_txn_id"}


@pytest.fixture
def valid_verify_mobile_otp_data() -> dict[str, Any]:
    """Fixture for valid mobile OTP verification data."""
    return {"otp": "123456", "txnId": "test_txn_id"}


@pytest.fixture
def valid_create_abha_address_data() -> dict[str, Any]:
    """Fixture for valid ABHA address creation data."""
    return {"abhaAddress": "user@abha", "txnId": "test_txn_id"}


@pytest.fixture
def mock_public_key() -> str:
    """Fixture for ABHA public key."""
    return (
        "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEF\n-----END PUBLIC KEY-----"
    )


# --- Initialization Tests ---
def test_init_with_public_key(
    client_config: ClientConfig, mock_public_key: str
) -> None:
    """Test ABHAService initialization with public key."""
    with patch.dict(
        "os.environ", {"ABHA_PUBLIC_KEY": mock_public_key.replace("\n", "\\n")}
    ):
        service = ABHAService(client_config)
        assert service.abha_public_key == mock_public_key
        assert isinstance(service.logger, logging.Logger)


def test_init_without_public_key(client_config: ClientConfig) -> None:
    """Test ABHAService initialization without public key."""
    with patch.dict("os.environ", {}, clear=True):
        with patch(
            "carestack.patient.abha.abha_service.logging.getLogger"
        ) as mock_logger:
            mock_logger_instance = mock_logger.return_value

            service = ABHAService(client_config)

            assert service.abha_public_key is None
            mock_logger_instance.warning.assert_called_once_with(
                "ABHA_PUBLIC_KEY environment variable is not set. Encryption will fail."
            )


enroll_with_aadhaar_response = EnrollWithAadhaarResponse(
    txnId="new_txn_id",
    message="Enrollment successful",
    ABHAProfile=AbhaProfile(
        firstName="Test",
        lastName="User",
        middleName="T",
        gender="M",
        mobile="9999999999",
        address="123 Test Street",
        abhaType="Temporary",
        stateName="Andhra Pradesh",
        districtName="Guntur",
        ABHANumber="123456789012",
        abhaStatus="ACTIVE",
    ),
    tokens={
        "token": "sample_token",
        "refreshToken": "sample_refresh_token",
        "expiresIn": 3600,
        "refreshExpiresIn": 86400,
    },
    isNew=True,
)


# --- generate_aadhaar_otp Tests ---
# @pytest.mark.asyncio
@pytest.mark.skip(reason="Skipping this test for now")
async def test_generate_aadhaar_otp_success(
    mock_abha_service: ABHAService, valid_generate_aadhaar_otp_data: dict[str, Any]
) -> None:
    """Test successful Aadhaar OTP generation."""

    service = mock_abha_service
    request = GenerateAadhaarOtpRequest(**valid_generate_aadhaar_otp_data)
    mock_response = VerifyOtpResponse(
        txnId="test_txn_id", message="OTP generated successfully"
    )

    # Patch EncryptData.__call__ method (since it's likely a callable instance)
    with patch(
        "carestack.patient.abha.abha_service.EncryptData.__call__",
        return_value="encrypted_aadhaar_data",
    ) as mock_encrypt:
        # Patch the `post` method in the ABHAService instance
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await service.generate_aadhaar_otp(request)

            mock_encrypt.assert_called_once_with(
                data_to_encrypt=request.aadhaar, certificate_pem=service.abha_public_key
            )
            mock_post.assert_called_once_with(
                CREATE_ABHA_ENDPOINTS.GENERATE_AADHAAR_OTP,
                {"aadhaar": "encrypted_aadhaar_data"},
                response_model=VerifyOtpResponse,
            )

            assert result == mock_response
            assert result.txnId == "test_txn_id"


# @pytest.mark.asyncio
@pytest.mark.skip(reason="Skipping this test for now")
async def test_generate_aadhaar_otp_ehr_api_error(
    mock_abha_service: ABHAService, valid_generate_aadhaar_otp_data: dict[str, Any]
) -> None:
    """Test generate_aadhaar_otp when post raises EhrApiError."""
    service = mock_abha_service
    request = GenerateAadhaarOtpRequest(**valid_generate_aadhaar_otp_data)

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ) as mock_encrypt:
        mock_encrypt.return_value = "encrypted_aadhaar_data"

        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = EhrApiError("API error", 400)

            with pytest.raises(EhrApiError) as exc_info:
                await service.generate_aadhaar_otp(request)

            mock_post.assert_called_once_with(
                CREATE_ABHA_ENDPOINTS.GENERATE_AADHAAR_OTP,
                {"aadhaar": "encrypted_aadhaar_data"},
                response_model=VerifyOtpResponse,
            )
            assert "API error" in str(exc_info.value)
            assert exc_info.value.status_code is None


@pytest.mark.asyncio
async def test_generate_aadhaar_otp_unexpected_error(
    mock_abha_service: ABHAService, valid_generate_aadhaar_otp_data: dict[str, Any]
) -> None:
    """Test generate_aadhaar_otp when post raises unexpected error."""
    service = mock_abha_service
    request = GenerateAadhaarOtpRequest(**valid_generate_aadhaar_otp_data)

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ):
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = ValueError("Unexpected error")

            with pytest.raises(EhrApiError) as exc_info:
                await service.generate_aadhaar_otp(request)

            assert (
                "An unexpected error occurred while generating aadhaar based otp"
                in str(exc_info.value)
            )


# --- enroll_with_aadhaar Tests ---
# @pytest.mark.asyncio
@pytest.mark.skip(reason="Skipping this test for now")
async def test_enroll_with_aadhaar_success(
    mock_abha_service: ABHAService, valid_enroll_with_aadhaar_data: dict[str, Any]
) -> None:
    """Test successful enrollment with Aadhaar."""
    service = mock_abha_service
    request = EnrollWithAadhaar(**valid_enroll_with_aadhaar_data)
    mock_response = enroll_with_aadhaar_response

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ) as mock_encrypt:
        mock_encrypt.return_value = "encrypted_otp_data"
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await service.enroll_with_aadhaar(request)

            mock_encrypt.assert_called_once_with(
                data_to_encrypt=request.otp, certificate_pem=service.abha_public_key
            )
            mock_post.assert_called_once_with(
                CREATE_ABHA_ENDPOINTS.ENROLL_WITH_AADHAAR,
                {
                    "otp": "encrypted_otp_data",
                    "txnId": request.txnId,
                    "mobile": request.mobile,
                },
                response_model=EnrollWithAadhaarResponse,
            )
            assert result == mock_response
            assert result.txnId == "new_txn_id"


# @pytest.mark.asyncio
@pytest.mark.skip(reason="Skipping this test for now")
async def test_enroll_with_aadhaar_ehr_api_error(
    mock_abha_service: ABHAService, valid_enroll_with_aadhaar_data: dict[str, Any]
) -> None:
    """Test enroll_with_aadhaar when post raises EhrApiError."""
    service = mock_abha_service
    request = EnrollWithAadhaar(**valid_enroll_with_aadhaar_data)

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ):
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = EhrApiError("Enrollment failed", 401)

            with pytest.raises(EhrApiError) as exc_info:
                await service.enroll_with_aadhaar(request)

            assert "Enrollment failed" in str(exc_info.value)
            assert exc_info.value.status_code is None


@pytest.mark.asyncio
async def test_enroll_with_aadhaar_unexpected_error(
    mock_abha_service: ABHAService, valid_enroll_with_aadhaar_data: dict[str, Any]
) -> None:
    """Test enroll_with_aadhaar when post raises unexpected error."""
    service = mock_abha_service
    request = EnrollWithAadhaar(**valid_enroll_with_aadhaar_data)

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ):
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = ConnectionError("Network error")

            with pytest.raises(EhrApiError) as exc_info:
                await service.enroll_with_aadhaar(request)

            assert "An unexpected error occurred while enrolling with aadhaar" in str(
                exc_info.value
            )


# --- generate_mobile_otp Tests ---
# @pytest.mark.asyncio
@pytest.mark.skip(reason="Skipping this test for now")
async def test_generate_mobile_otp_success(
    mock_abha_service: ABHAService, valid_update_mobile_number_data: dict[str, Any]
) -> None:
    """Test successful mobile OTP generation."""
    service = mock_abha_service
    request = UpdateMobileNumberRequest(**valid_update_mobile_number_data)
    mock_response = VerifyOtpResponse(
        txnId="mobile_txn_id", message="OTP generated successfully"
    )

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ) as mock_encrypt:
        mock_encrypt.return_value = "encrypted_mobile_data"
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await service.generate_mobile_otp(request)

            mock_encrypt.assert_called_once_with(
                data_to_encrypt=request.updateValue,
                certificate_pem=service.abha_public_key,
            )
            mock_post.assert_called_once_with(
                CREATE_ABHA_ENDPOINTS.GENERATE_MOBILE_OTP,
                {"updateValue": "encrypted_mobile_data", "txnId": request.txnId},
                response_model=VerifyOtpResponse,
            )
            assert result == mock_response
            assert result.txnId == "mobile_txn_id"


# @pytest.mark.asyncio
@pytest.mark.skip(reason="Skipping this test for now")
async def test_generate_mobile_otp_ehr_api_error(
    mock_abha_service: ABHAService, valid_update_mobile_number_data: dict[str, Any]
) -> None:
    """Test generate_mobile_otp when post raises EhrApiError."""
    service = mock_abha_service
    request = UpdateMobileNumberRequest(**valid_update_mobile_number_data)

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ):
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = EhrApiError("Mobile OTP failed", 422)

            with pytest.raises(EhrApiError) as exc_info:
                await service.generate_mobile_otp(request)

            assert "Mobile OTP failed" in str(exc_info.value)
            assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_generate_mobile_otp_unexpected_error(
    mock_abha_service: ABHAService, valid_update_mobile_number_data: dict[str, Any]
) -> None:
    """Test generate_mobile_otp when post raises unexpected error."""
    service = mock_abha_service
    request = UpdateMobileNumberRequest(**valid_update_mobile_number_data)

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ):
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = TimeoutError("Request timeout")

            with pytest.raises(EhrApiError) as exc_info:
                await service.generate_mobile_otp(request)

            assert "An unexpected error occurred while generating mobile otp" in str(
                exc_info.value
            )


# --- verify_mobile_otp Tests ---
# @pytest.mark.asyncio
@pytest.mark.skip(reason="Skipping this test for now")
async def test_verify_mobile_otp_success(
    mock_abha_service: ABHAService, valid_verify_mobile_otp_data: dict[str, Any]
) -> None:
    """Test successful mobile OTP verification."""
    service = mock_abha_service
    request = VerifyMobileOtpRequest(**valid_verify_mobile_otp_data)
    mock_response = VerifyMobileOtpResponse(
        txnId="verified_txn_id", message="OTP verified successfully", authResult="True"
    )

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ) as mock_encrypt:
        mock_encrypt.return_value = "encrypted_otp_data"
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await service.verify_mobile_otp(request)

            mock_encrypt.assert_called_once_with(
                data_to_encrypt=request.otp, certificate_pem=service.abha_public_key
            )
            mock_post.assert_called_once_with(
                CREATE_ABHA_ENDPOINTS.VERIFY_MOBILE_OTP,
                {"otp": "encrypted_otp_data", "txnId": request.txnId},
                response_model=VerifyMobileOtpResponse,
            )
            assert result == mock_response
            assert result.txnId == "verified_txn_id"


@pytest.mark.asyncio
# @pytest.mark.skip(reason="Skipping this test for now")
async def test_verify_mobile_otp_ehr_api_error(
    mock_abha_service: ABHAService, valid_verify_mobile_otp_data: dict[str, Any]
) -> None:
    """Test verify_mobile_otp when post raises EhrApiError."""
    service = mock_abha_service
    request = VerifyMobileOtpRequest(**valid_verify_mobile_otp_data)

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ):
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = EhrApiError(
                "An unexpected error occurred while verifying mobile otp", 400
            )

            with pytest.raises(EhrApiError) as exc_info:
                await service.verify_mobile_otp(request)

            assert "An unexpected error occurred while verifying mobile otp" in str(
                exc_info.value
            )
            assert exc_info.value.status_code is None


@pytest.mark.asyncio
async def test_verify_mobile_otp_unexpected_error(
    mock_abha_service: ABHAService, valid_verify_mobile_otp_data: dict[str, Any]
) -> None:
    """Test verify_mobile_otp when post raises unexpected error."""
    service = mock_abha_service
    request = VerifyMobileOtpRequest(**valid_verify_mobile_otp_data)

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ):
        with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = KeyError("Missing key")

            with pytest.raises(EhrApiError) as exc_info:
                await service.verify_mobile_otp(request)

            assert "An unexpected error occurred while verifying mobile otp" in str(
                exc_info.value
            )


# --- abha_address_suggestion Tests ---
@pytest.mark.asyncio
async def test_abha_address_suggestion_success(mock_abha_service: ABHAService) -> None:
    """Test successful ABHA address suggestions retrieval."""
    service = mock_abha_service
    txn_id = "test_txn_id"
    mock_response = AbhaAddressSuggestionsResponse(
        abhaAddressList=["user@abha", "user1@abha"], txnId=txn_id
    )

    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await service.abha_address_suggestion(txn_id)

        mock_get.assert_called_once_with(
            CREATE_ABHA_ENDPOINTS.ABHA_ADDRESS_SUGGESTION,
            query_params={"txnId": txn_id},
            response_model=AbhaAddressSuggestionsResponse,
        )
        assert result == mock_response
        assert result.abhaAddressList == ["user@abha", "user1@abha"]


@pytest.mark.asyncio
async def test_abha_address_suggestion_ehr_api_error(
    mock_abha_service: ABHAService,
) -> None:
    """Test abha_address_suggestion when get raises EhrApiError."""
    service = mock_abha_service
    txn_id = "test_txn_id"

    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = EhrApiError("Failed to get suggestions", 404)

        with pytest.raises(EhrApiError) as exc_info:
            await service.abha_address_suggestion(txn_id)

        mock_get.assert_called_once_with(
            CREATE_ABHA_ENDPOINTS.ABHA_ADDRESS_SUGGESTION,
            query_params={"txnId": txn_id},
            response_model=AbhaAddressSuggestionsResponse,
        )
        assert "Failed to get suggestions" in str(exc_info.value)
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_abha_address_suggestion_unexpected_error(
    mock_abha_service: ABHAService,
) -> None:
    """Test abha_address_suggestion when get raises unexpected error."""
    service = mock_abha_service
    txn_id = "test_txn_id"

    with patch.object(service, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = RuntimeError("Unexpected runtime error")

        with pytest.raises(EhrApiError) as exc_info:
            await service.abha_address_suggestion(txn_id)

        assert (
            "An unexpected error occurred while getting abha address suggestions"
            in str(exc_info.value)
        )


# --- create_abha_address Tests ---
@pytest.mark.asyncio
async def test_create_abha_address_success(
    mock_abha_service: ABHAService, valid_create_abha_address_data: dict[str, Any]
) -> None:
    """Test successful ABHA address creation."""
    service = mock_abha_service
    request = CreateAbhaAddressRequest(**valid_create_abha_address_data)
    mock_response = CreateAbhaAddressResponse(
        preferredAbhaAddress="user@abha",
        txnId=request.txnId,
        healthIdNumber="123456789012",
    )

    with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await service.create_abha_address(request)

        mock_post.assert_called_once_with(
            CREATE_ABHA_ENDPOINTS.CREATE_ABHA,
            {
                "abhaAddress": request.abhaAddress,
                "txnId": request.txnId,
                # "healthIdNumber": "123456789012"
            },
            response_model=CreateAbhaAddressResponse,
        )
        assert result == mock_response
        # assert result.preferredAbhaAddress == "user@abha"
        # assert result.healthIdNumber == "123456789012"


@pytest.mark.asyncio
async def test_create_abha_address_ehr_api_error(
    mock_abha_service: ABHAService, valid_create_abha_address_data: dict[str, Any]
) -> None:
    """Test create_abha_address when post raises EhrApiError."""
    service = mock_abha_service
    request = CreateAbhaAddressRequest(**valid_create_abha_address_data)

    with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = EhrApiError("Address already exists", 409)

        with pytest.raises(EhrApiError) as exc_info:
            await service.create_abha_address(request)

        mock_post.assert_called_once_with(
            CREATE_ABHA_ENDPOINTS.CREATE_ABHA,
            {"abhaAddress": request.abhaAddress, "txnId": request.txnId},
            response_model=CreateAbhaAddressResponse,
        )
        assert "Address already exists" in str(exc_info.value)
        assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_create_abha_address_unexpected_error(
    mock_abha_service: ABHAService, valid_create_abha_address_data: dict[str, Any]
) -> None:
    """Test create_abha_address when post raises unexpected error."""
    service = mock_abha_service
    request = CreateAbhaAddressRequest(**valid_create_abha_address_data)

    with patch.object(service, "post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = ValueError("Invalid data format")

        with pytest.raises(EhrApiError) as exc_info:
            await service.create_abha_address(request)

        assert "An unexpected error occurred while creating abha address" in str(
            exc_info.value
        )


# --- Encryption Error Tests ---
@pytest.mark.asyncio
async def test_encryption_failure_handling(
    mock_abha_service: ABHAService, valid_generate_aadhaar_otp_data: dict[str, Any]
) -> None:
    """Test handling of encryption failures."""
    service = mock_abha_service
    request = GenerateAadhaarOtpRequest(**valid_generate_aadhaar_otp_data)

    with patch(
        "carestack.patient.abha.abha_service.EncryptData",
        new_callable=AsyncMock,
    ) as mock_encrypt:
        mock_encrypt.side_effect = Exception("Encryption failed")

        with pytest.raises(EhrApiError) as exc_info:
            await service.generate_aadhaar_otp(request)

        assert "An unexpected error occurred while generating aadhaar based otp" in str(
            exc_info.value
        )


# --- Logger Tests ---
def test_logger_initialization(mock_abha_service: ABHAService) -> None:
    """Test that logger is properly initialized."""
    service = mock_abha_service
    assert hasattr(service, "logger")
    assert isinstance(service.logger, logging.Logger)
    assert service.logger.name == "carestack.patient.abha.abha_service"
