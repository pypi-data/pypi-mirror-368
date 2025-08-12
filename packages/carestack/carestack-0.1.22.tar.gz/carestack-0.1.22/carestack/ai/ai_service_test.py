import pytest
import os
from unittest.mock import AsyncMock, patch

from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import AI_ENDPOINTS

from carestack.ai.ai_service import AiService
from carestack.ai.ai_dto import (
    DischargeSummaryResponse,
    FhirBundleResponse,
    GenerateFhirBundleDto,
    ProcessDSDto,
)
from carestack.common.config_test import client_config


class TestAiService:
    """Test cases for AiService class."""

    @pytest.fixture
    def ai_service(self, client_config: ClientConfig) -> AiService:
        """AiService instance fixture."""
        with patch("carestack.ai.ai_service.AiUtilities") as mock_utilities:
            with patch.dict(os.environ, {"AI_SERVICE_KEY": "test_ai_key"}):
                service = AiService(client_config)
                service.utilities = mock_utilities.return_value
                # Mock the post method from BaseService
                service.post = AsyncMock()
                return service

    @pytest.fixture
    def ai_service_no_env(self, client_config: ClientConfig) -> AiService:
        """AiService instance fixture without environment variables."""
        with patch("carestack.ai.ai_service.AiUtilities") as mock_utilities:
            with patch.dict(os.environ, {}, clear=True):
                service = AiService(client_config)
                service.utilities = mock_utilities.return_value
                service.post = AsyncMock()
                return service

    @pytest.fixture
    def mock_fhir_bundle_response(self):
        """Mock FHIR bundle response fixture."""
        return FhirBundleResponse(
            root={"resourceType": "Bundle", "id": "test-bundle", "entry": []}
        )

    @pytest.fixture
    def mock_discharge_summary_response(self) -> DischargeSummaryResponse:
        """Mock discharge summary response fixture."""
        return DischargeSummaryResponse(
            id="mock-id-123",
            dischargeSummary={"summary": "Sample discharge summary"},
            extractedData={"diagnosis": "sample diagnosis"},
            fhirBundle={"resourceType": "Bundle", "entry": []},
        )

    @pytest.fixture
    def valid_process_ds_data(self):
        """Valid ProcessDS data fixture."""
        return {
            "caseType": "DischargeSummary",  # Keep camelCase for API compatibility
            "files": ["file1.pdf", "file2.pdf"],
            "encryptedData": None,
            "publicKey": "test-public-key",
        }

    @pytest.fixture
    def valid_process_ds_data_with_encrypted(self):
        """Valid ProcessDS data with encrypted data fixture."""
        return {
            "caseType": "DischargeSummary",  # Keep camelCase for API compatibility
            "files": None,
            "encryptedData": "encrypted-test-data",
            "publicKey": "test-public-key",
        }

    @pytest.fixture
    def valid_fhir_bundle_data(self):
        """Valid FHIR bundle data fixture."""
        return {
            "caseType": "admission",  # Keep camelCase for API compatibility
            "extractedData": {"patient": "test-patient"},
            "encryptedData": None,
            "documentReferences": ["doc_ref_1", "doc_ref_2"],
            "enableExtraction": False,
            "recordId": "rec-123",
            "publicKey": "test-public-key",
        }

    @pytest.fixture
    def valid_fhir_bundle_data_with_encrypted(self):
        """Valid FHIR bundle data with encrypted data fixture."""
        return {
            "caseType": "admission",  # Keep camelCase for API compatibility
            "extractedData": None,
            "encryptedData": "encrypted-fhir-data",
            "documentReferences": ["doc_ref_1", "doc_ref_2"],
            "enableExtraction": False,
            "recordId": "rec-123",
            "publicKey": "test-public-key",
        }

    class TestValidateData:
        """Test cases for _validate_data method."""

        @pytest.mark.asyncio
        async def test_validate_data_success(self, ai_service: AiService):
            """Test successful data validation."""
            valid_data = {
                "caseType": "DischargeSummary",  # Keep camelCase for API compatibility
                "files": ["file1.pdf"],
                "encryptedData": None,
                "publicKey": "test-key",
            }

            result = await ai_service._validate_data(ProcessDSDto, valid_data)

            assert isinstance(result, ProcessDSDto)
            assert (
                result.case_type == "DischargeSummary"
            )  # DTO uses snake_case internally
            assert result.files == ["file1.pdf"]

        @pytest.mark.asyncio
        async def test_validate_data_validation_error(self, ai_service: AiService):
            """Test validation error handling."""
            invalid_data = {"invalid_field": "invalid_value"}

            with pytest.raises(EhrApiError) as exc_info:
                await ai_service._validate_data(ProcessDSDto, invalid_data)

            assert exc_info.value.status_code == 400
            assert "Validation failed" in str(exc_info.value.message)

    class TestGenerateDischargeSummary:
        """Test cases for generate_discharge_summary method."""

        @pytest.mark.asyncio
        async def test_generate_discharge_summary_no_data_provided(
            self, ai_service: AiService
        ):
            """Test discharge summary generation with no files or encrypted data."""
            data = {
                "caseType": "DischargeSummary",  # Keep camelCase for API compatibility
                "files": None,
                "encryptedData": None,
                "publicKey": "test-key",
            }

            with pytest.raises(EhrApiError) as exc_info:
                await ai_service.generate_discharge_summary(data)

            assert exc_info.value.status_code == 422
            assert "No files or encrypted data provided" in str(exc_info.value.message)

        @pytest.mark.asyncio
        async def test_generate_discharge_summary_validation_error(
            self, ai_service: AiService
        ):
            """Test discharge summary generation with validation error."""
            invalid_data = {"invalid_field": "invalid_value"}

            with pytest.raises(EhrApiError) as exc_info:
                await ai_service.generate_discharge_summary(invalid_data)

            assert exc_info.value.status_code == 400
            assert "Validation failed" in str(exc_info.value.message)

        @pytest.mark.asyncio
        async def test_generate_discharge_summary_ehr_api_error(
            self, ai_service: AiService, valid_process_ds_data
        ):
            """Test discharge summary generation with EHR API error."""
            ai_service.utilities.encryption = AsyncMock(return_value="encrypted-data")
            ai_service.post = AsyncMock(side_effect=EhrApiError("API Error", 500))

            with pytest.raises(EhrApiError) as exc_info:
                await ai_service.generate_discharge_summary(valid_process_ds_data)

            assert exc_info.value.status_code == 500
            assert "API Error" in str(exc_info.value.message)

        @pytest.mark.asyncio
        async def test_generate_discharge_summary_unexpected_error(
            self, ai_service: AiService, valid_process_ds_data
        ):
            """Test discharge summary generation with unexpected error."""
            ai_service.utilities.encryption = AsyncMock(
                side_effect=Exception("Unexpected error")
            )

            with pytest.raises(EhrApiError) as exc_info:
                await ai_service.generate_discharge_summary(valid_process_ds_data)

            assert exc_info.value.status_code == 500
            assert (
                "An unexpected error occurred while generating discharge summary"
                in str(exc_info.value.message)
            )

    # class TestGenerateFhirBundle:
    #     """Test cases for generate_fhir_bundle method."""

    #     @pytest.mark.asyncio
    #     async def test_generate_fhir_bundle_with_extracted_data_success(
    #         self,
    #         ai_service: AiService,
    #         valid_fhir_bundle_data,
    #         mock_fhir_bundle_response,
    #     ):
    #         """Test successful FHIR bundle generation with extracted data."""
    #         ai_service.utilities.encryption = AsyncMock(
    #             side_effect=["encrypted-extracted", "encrypted-docs"]
    #         )
    #         ai_service.post = AsyncMock()
    #         ai_service.post.return_value = mock_fhir_bundle_response

    #         result = await ai_service.generate_fhir_bundle(valid_fhir_bundle_data)

    #         assert result == mock_fhir_bundle_response.root
    #         assert ai_service.utilities.encryption.call_count == 2
    #         ai_service.utilities.encryption.assert_any_call(
    #             payload={"data": {"patient": "test-patient"}}
    #         )
    #         ai_service.utilities.encryption.assert_any_call(
    #             payload={"files": ["doc_ref_1", "doc_ref_2"]}
    #         )

    #     @pytest.mark.asyncio
    #     async def test_generate_fhir_bundle_minimal_data(
    #         self, ai_service: AiService, mock_fhir_bundle_response
    #     ):
    #         """Test FHIR bundle generation with minimal required data."""
    #         minimal_data = {
    #             "caseType": "admission",
    #             "extractedData": {"test": "data"},
    #             "documentReferences": ["doc_ref_1", "doc_ref_2"],
    #             "enableExtraction": False,
    #             "encryptedData": None,
    #             "recordId": None,
    #             "publicKey": None,
    #         }

    #         ai_service.utilities.encryption = AsyncMock(
    #             side_effect=["encrypted-extracted", "encrypted-docs"]
    #         )
    #         ai_service.post = AsyncMock()
    #         ai_service.post.return_value = mock_fhir_bundle_response

    #         result = await ai_service.generate_fhir_bundle(minimal_data)

    #         assert result == mock_fhir_bundle_response.root
    #         ai_service.post.assert_called_once_with(
    #             AI_ENDPOINTS.GENERATE_FHIR_BUNDLE,
    #             {
    #                 "caseType": "admission",
    #                 "enableExtraction": False,
    #                 "encryptedData": "encrypted-extracted",
    #                 "encryptedDocRefs": "encrypted-docs",
    #             },
    #             response_model=FhirBundleResponse,
    #         )

    #     @pytest.mark.asyncio
    #     async def test_generate_fhir_bundle_no_data_provided(
    #         self, ai_service: AiService
    #     ):
    #         """Test FHIR bundle generation with no extracted or encrypted data."""
    #         data = {
    #             "caseType": "admission",
    #             "extractedData": None,
    #             "encryptedData": None,
    #             "documentReferences": ["doc_ref_1", "doc_ref_2"],
    #             "enableExtraction": False,
    #             "recordId": "rec-123",
    #             "publicKey": "test-key",
    #         }

    #         with pytest.raises(EhrApiError) as exc_info:
    #             await ai_service.generate_fhir_bundle(data)

    #         assert exc_info.value.status_code == 422
    #         assert "No extracted data is provided." in str(exc_info.value.message)

    #     @pytest.mark.asyncio
    #     async def test_generate_fhir_bundle_validation_error(
    #         self, ai_service: AiService
    #     ):
    #         """Test FHIR bundle generation with validation error."""
    #         invalid_data = {"invalid_field": "invalid_value"}

    #         with pytest.raises(EhrApiError) as exc_info:
    #             await ai_service.generate_fhir_bundle(invalid_data)

    #         assert exc_info.value.status_code == 400
    #         assert "Validation failed" in str(exc_info.value.message)

    #     @pytest.mark.asyncio
    #     async def test_generate_fhir_bundle_ehr_api_error(
    #         self, ai_service: AiService, valid_fhir_bundle_data
    #     ):
    #         """Test FHIR bundle generation with EHR API error."""
    #         ai_service.utilities.encryption = AsyncMock(return_value="encrypted-data")
    #         ai_service.post = AsyncMock(side_effect=EhrApiError("FHIR API Error", 503))

    #         with pytest.raises(EhrApiError) as exc_info:
    #             await ai_service.generate_fhir_bundle(valid_fhir_bundle_data)

    #         assert exc_info.value.status_code == 503
    #         assert "FHIR API Error" in str(exc_info.value.message)

    #     @pytest.mark.asyncio
    #     async def test_generate_fhir_bundle_unexpected_error(
    #         self, ai_service: AiService, valid_fhir_bundle_data
    #     ):
    #         """Test FHIR bundle generation with unexpected error."""
    #         ai_service.utilities.encryption = AsyncMock(
    #             side_effect=Exception("Encryption failed")
    #         )

    #         with pytest.raises(EhrApiError) as exc_info:
    #             await ai_service.generate_fhir_bundle(valid_fhir_bundle_data)

    #         assert exc_info.value.status_code == 500
    #         assert "An unexpected error occurred while generating FHIR bundle" in str(
    #             exc_info.value.message
    #         )

    class TestInitialization:
        """Test cases for AiService initialization."""

        def test_init_success(self, client_config):
            """Test successful AiService initialization."""
            with patch("carestack.ai.ai_service.AiUtilities") as mock_utilities:
                with patch.dict(os.environ, {"AI_SERVICE_KEY": "test_ai_key"}):
                    service = AiService(client_config)

                    assert service.config == client_config
                    assert service.utilities is not None
                    mock_utilities.assert_called_once()

        def test_logger_initialization(self, client_config):
            """Test logger is properly initialized."""
            with patch("carestack.ai.ai_service.AiUtilities"):
                with patch.dict(os.environ, {"AI_SERVICE_KEY": "test_ai_key"}):
                    service = AiService(client_config)

                    assert hasattr(service, "logger")
                    assert service.logger.name == "carestack.ai.ai_service"

        def test_init_without_env_vars(self, client_config):
            """Test AiService initialization without environment variables."""
            with patch("carestack.ai.ai_service.AiUtilities") as mock_utilities:
                with patch.dict(os.environ, {}, clear=True):
                    service = AiService(client_config)

                    assert service.config == client_config
                    assert service.utilities is not None
                    mock_utilities.assert_called_once()

    class TestEdgeCases:
        """Test cases for edge cases and boundary conditions."""

        @pytest.mark.asyncio
        async def test_empty_files_list(
            self, ai_service: AiService, mock_discharge_summary_response
        ):
            """Test discharge summary generation with empty files list."""
            data = {
                "caseType": "DischargeSummary",  # Keep camelCase for API compatibility
                "files": [],
                "encryptedData": None,
                "publicKey": "test-key",
            }

            with pytest.raises(EhrApiError) as exc_info:
                await ai_service.generate_discharge_summary(data)

            assert exc_info.value.status_code == 422

        # @pytest.mark.asyncio
        # async def test_empty_extracted_data_dict(self, ai_service: AiService):
        #     """Test FHIR bundle generation with empty extracted data dict - should fail."""
        #     data = {
        #         "caseType": "admission",
        #         "extractedData": {},
        #         "encryptedData": None,
        #         "documentReferences": ["doc_ref_1", "doc_ref_2"],
        #         "enableExtraction": False,
        #         "recordId": "rec-123",
        #         "publicKey": "test-key",
        #     }

        #     with pytest.raises(EhrApiError) as exc_info:
        #         await ai_service.generate_fhir_bundle(data)

        #     assert exc_info.value.status_code == 422
        #     assert "No extracted data is provided" in str(exc_info.value.message)

        # @pytest.mark.asyncio
        # async def test_non_empty_extracted_data_dict(
        #     self, ai_service: AiService, mock_fhir_bundle_response
        # ):
        #     """Test FHIR bundle generation with non-empty extracted data dict."""
        #     data = {
        #         "caseType": "admission",
        #         "extractedData": {"patient": "test-data"},
        #         "encryptedData": None,
        #         "documentReferences": ["doc_ref_1", "doc_ref_2"],
        #         "enableExtraction": False,
        #         "recordId": "rec-123",
        #         "publicKey": "test-key",
        #     }

        #     ai_service.utilities.encryption = AsyncMock(
        #         side_effect=["encrypted-extracted", "encrypted-docs"]
        #     )
        #     ai_service.post = AsyncMock()
        #     ai_service.post.return_value = mock_fhir_bundle_response

        #     result = await ai_service.generate_fhir_bundle(data)

        #     assert result == mock_fhir_bundle_response.root
        #     assert ai_service.utilities.encryption.call_count == 2

        @pytest.mark.asyncio
        async def test_large_data_handling(
            self, ai_service: AiService, mock_discharge_summary_response
        ):
            """Test handling of large data payloads."""
            large_files = [f"file_{i}.pdf" for i in range(1000)]
            data = {
                "caseType": "DischargeSummary",  # Keep camelCase for API compatibility
                "files": large_files,
                "encryptedData": None,
                "publicKey": "test-key",
            }

            ai_service.utilities.encryption = AsyncMock(
                return_value="encrypted-large-data"
            )
            ai_service.post = AsyncMock()
            ai_service.post.return_value = mock_discharge_summary_response

            result = await ai_service.generate_discharge_summary(data)

            assert result == mock_discharge_summary_response
            ai_service.utilities.encryption.assert_called_once_with(
                payload={"files": large_files}
            )

        # @pytest.mark.asyncio
        # async def test_special_characters_in_data(
        #     self, ai_service: AiService, mock_fhir_bundle_response
        # ):
        #     """Test handling of special characters in data."""
        #     data = {
        #         "caseType": "admission",
        #         "extractedData": {
        #             "patient_name": "José María Ñoño",
        #             "notes": "Patient has café allergy & takes medication 2x/day",
        #         },
        #         "encryptedData": None,
        #         "documentReferences": ["doc_ref_1", "doc_ref_2"],
        #         "enableExtraction": False,
        #         "recordId": "rec-123",
        #         "publicKey": "test-key",
        #     }

        #     ai_service.utilities.encryption = AsyncMock(
        #         side_effect=["encrypted-extracted", "encrypted-docs"]
        #     )
        #     ai_service.post = AsyncMock()
        #     ai_service.post.return_value = mock_fhir_bundle_response

        #     result = await ai_service.generate_fhir_bundle(data)

        #     assert result == mock_fhir_bundle_response.root
        #     assert ai_service.utilities.encryption.call_count == 2

        @pytest.mark.asyncio
        async def test_none_values_handling(self, ai_service: AiService):
            """Test handling of None values in various fields."""
            data = {
                "case_type": None,
                "files": None,
                "encrypted_data": None,
                "public_key": None,
            }

            with pytest.raises(EhrApiError) as exc_info:
                await ai_service.generate_discharge_summary(data)

            assert exc_info.value.status_code == 400
            assert "Validation failed" in str(exc_info.value.message)

        # @pytest.mark.asyncio
        # async def test_encryption_with_complex_nested_data(
        #     self, ai_service: AiService, mock_fhir_bundle_response
        # ):
        #     """Test encryption with complex nested data structures."""
        #     complex_data = {
        #         "caseType": "DischargeSummary",
        #         "extractedData": {
        #             "patient": {
        #                 "name": "John Doe",
        #                 "age": 35,
        #                 "address": {
        #                     "street": "123 Main St",
        #                     "city": "Anytown",
        #                     "zip": "12345",
        #                 },
        #             },
        #             "practitioner": [
        #                 {
        #                     "name": "Dr. Smith",
        #                     "specialty": "Cardiology",
        #                     "designation": "Senior Consultant",
        #                 }
        #             ],
        #             "conditions": [
        #                 {"code": "I10", "description": "Hypertension"},
        #                 {"code": "E11.9", "description": "Type 2 diabetes"},
        #             ],
        #         },
        #         "encrypted_data": None,
        #         "documentReferences": ["doc_ref_1", "doc_ref_2"],
        #         "enableExtraction": False,
        #         "record_id": "rec-complex-123",
        #         "public_key": "test-key",
        #     }

        #     ai_service.utilities.encryption = AsyncMock(
        #         side_effect=["encrypted-extracted", "encrypted-docs"]
        #     )
        #     ai_service.post = AsyncMock()
        #     ai_service.post.return_value = mock_fhir_bundle_response

        #     result = await ai_service.generate_fhir_bundle(complex_data)

        #     assert result == mock_fhir_bundle_response.root
        #     assert ai_service.utilities.encryption.call_count == 2

    class TestEnvironmentConfiguration:
        """Test cases for environment configuration scenarios."""

        def test_service_with_env_variables(self, client_config):
            """Test AiService with environment variables set."""
            test_env = {
                "AI_SERVICE_KEY": "production_key",
                "AI_DEBUG": "true",
                "AI_TIMEOUT": "60",
            }

            with patch("carestack.ai.ai_service.AiUtilities") as mock_utilities:
                with patch.dict(os.environ, test_env):
                    service = AiService(client_config)

                    assert service.config == client_config
                    assert service.utilities is not None
                    mock_utilities.assert_called_once()

        def test_service_env_override(self, client_config):
            """Test AiService behavior with environment variable overrides."""
            original_env = {"AI_SERVICE_KEY": "original_key"}
            override_env = {"AI_SERVICE_KEY": "override_key"}

            with patch("carestack.ai.ai_service.AiUtilities"):
                # Test with original environment
                with patch.dict(os.environ, original_env):
                    service1 = AiService(client_config)
                    assert service1.config == client_config

                # Test with override environment
                with patch.dict(os.environ, override_env):
                    service2 = AiService(client_config)
                    assert service2.config == client_config
