from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, patch
from carestack.appointment.appointment_service import Appointment
from carestack.appointment.appointment_dto import (
    AppointmentDTO,
    AppointmentResponse,
    CreateAppointmentResponeType,
    GetAppointmentResponse,
    UpdateAppointmentDTO,
)
from carestack.base.base_types import ClientConfig
from carestack.base.errors import EhrApiError
from carestack.common.enums import AppointmentEndpoints
from carestack.common.config_test import client_config


@pytest.fixture
def appointment_service(client_config: ClientConfig) -> Appointment:
    """Fixture for Appointment instance."""
    return Appointment(client_config)


@pytest.fixture
def sample_appointment_dto() -> AppointmentDTO:
    return AppointmentDTO(
        practitionerReference="prac-123",
        patientReference="pat-456",
        start=datetime(2023, 10, 26, 10, 0, tzinfo=timezone.utc),
        end=datetime(2023, 10, 26, 10, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_update_appointment_dto() -> UpdateAppointmentDTO:
    """Sample update appointment data for testing."""
    return UpdateAppointmentDTO(
        appointment_start_time="2023-10-26T10:00:00Z",
        appointment_end_time="2023-10-26T11:00:00Z",
    )


@pytest.fixture
def sample_appointment_response() -> AppointmentResponse:
    """Sample appointment response for testing."""
    return AppointmentResponse(
        type="success",
        message="Appointment Found",
        request_resource=None,
        total_records=1,
        next_page=None,
    )


@pytest.fixture
def sample_create_appointment_response() -> CreateAppointmentResponeType:
    """Sample create appointment response for testing."""
    return CreateAppointmentResponeType(
        type="success",
        message="Appointment Created",
        resource={
            "patientReference": "pat-456",
            "practitionerReference": "prac-123",
            "start": "2023-10-26T10:00:00Z",
            "end": "2023-10-26T11:00:00Z",
            "priority": "Emergency",
            "reference": "app-789",
            "organizationId": "org-123",
            "slot": "slot-456",
        },
    )


@pytest.fixture
def sample_get_appointment_response() -> GetAppointmentResponse:
    """Sample get appointment response for testing."""
    return GetAppointmentResponse(
        type="success",
        message="Appointments Fetched",
        request_resource=[],
        total_records=0,
        next_page=None,
    )


class TestAppointmentCreate:
    """Test cases for create method."""

    @pytest.mark.asyncio
    async def test_create_success(
        self,
        appointment_service,
        sample_appointment_dto,
        sample_create_appointment_response,
    ):
        """Test successful appointment creation."""

        appointment_service.post = AsyncMock(
            return_value=sample_create_appointment_response
        )

        result = await appointment_service.create(sample_appointment_dto)

        assert result == sample_create_appointment_response
        appointment_service.post.assert_called_once_with(
            AppointmentEndpoints.ADD_APPOINTMENT,
            {
                "practitionerReference": "prac-123",
                "patientReference": "pat-456",
                "start": "2023-10-26T10:00:00Z",
                "end": "2023-10-26T10:00:00Z",
                "priority": "Emergency",
            },
            response_model=CreateAppointmentResponeType,
        )


class TestAppointmentFindAll:
    """Test cases for find_all method."""

    @pytest.mark.asyncio
    async def test_find_all_without_pagination(
        self,
        appointment_service: Appointment,
        sample_get_appointment_response: GetAppointmentResponse,
    ):
        """Test find_all without pagination."""
        appointment_service.get = AsyncMock(
            return_value=sample_get_appointment_response
        )

        result = await appointment_service.find_all()

        assert result == sample_get_appointment_response
        appointment_service.get.assert_called_once_with(
            AppointmentEndpoints.GET_ALL_APPOINTMENTS,
            response_model=GetAppointmentResponse,
            query_params=None,
        )

    @pytest.mark.asyncio
    async def test_find_all_with_pagination(
        self,
        appointment_service: Appointment,
        sample_get_appointment_response: GetAppointmentResponse,
    ):
        """Test find_all with pagination."""
        appointment_service.get = AsyncMock(
            return_value=sample_get_appointment_response
        )
        next_page = "next_page_token"

        result = await appointment_service.find_all(next_page)

        assert result == sample_get_appointment_response
        appointment_service.get.assert_called_once_with(
            AppointmentEndpoints.GET_ALL_APPOINTMENTS,
            response_model=GetAppointmentResponse,
            query_params={"nextPage": next_page},
        )

    @pytest.mark.asyncio
    async def test_find_all_ehr_api_error(self, appointment_service: Appointment):
        """Test find_all with EhrApiError."""
        appointment_service.get = AsyncMock(side_effect=EhrApiError("API Error", 400))

        with pytest.raises(EhrApiError):
            await appointment_service.find_all()

    @pytest.mark.asyncio
    async def test_find_all_unexpected_error(self, appointment_service: Appointment):
        """Test find_all with unexpected error."""
        appointment_service.get = AsyncMock(side_effect=Exception("Unexpected error"))

        with pytest.raises(EhrApiError) as exc_info:
            await appointment_service.find_all()

        assert "An unexpected error occurred while fetching all appointments." in str(
            exc_info.value
        )
        assert exc_info.value.status_code == 500


class TestAppointmentFindById:
    """Test cases for find_by_id method."""

    @pytest.mark.asyncio
    async def test_find_by_id_success(
        self,
        appointment_service: Appointment,
        sample_appointment_response: AppointmentResponse,
    ):
        """Test successful find_by_id."""
        appointment_service.get = AsyncMock(return_value=sample_appointment_response)
        appointment_reference = "test-ref-123"

        result = await appointment_service.find_by_id(appointment_reference)

        assert result == sample_appointment_response
        appointment_service.get.assert_called_once_with(
            AppointmentEndpoints.GET_APPOINTMENT_BY_ID.format(
                reference=appointment_reference
            ),
            response_model=AppointmentResponse,
        )

    @pytest.mark.asyncio
    async def test_find_by_id_null_reference(self, appointment_service: Appointment):
        """Test find_by_id with null reference."""
        with pytest.raises(EhrApiError) as exc_info:
            await appointment_service.find_by_id(None)

        assert "Appointment Reference cannot be null or empty." in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_find_by_id_empty_reference(self, appointment_service: Appointment):
        """Test find_by_id with empty reference."""
        with pytest.raises(EhrApiError) as exc_info:
            await appointment_service.find_by_id("")

        assert "Appointment Reference cannot be null or empty." in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_find_by_id_whitespace_reference(
        self, appointment_service: Appointment
    ):
        """Test find_by_id with whitespace-only reference."""
        with pytest.raises(EhrApiError) as exc_info:
            await appointment_service.find_by_id("   ")

        assert "Appointment Reference cannot be null or empty." in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_find_by_id_ehr_api_error(self, appointment_service: Appointment):
        """Test find_by_id with EhrApiError."""
        appointment_service.get = AsyncMock(side_effect=EhrApiError("Not found", 404))

        with pytest.raises(EhrApiError):
            await appointment_service.find_by_id("test-ref")

    @pytest.mark.asyncio
    async def test_find_by_id_unexpected_error(self, appointment_service: Appointment):
        """Test find_by_id with unexpected error."""
        appointment_service.get = AsyncMock(side_effect=Exception("Unexpected error"))

        with pytest.raises(EhrApiError) as exc_info:
            await appointment_service.find_by_id("test-ref")

        assert "An unexpected error occurred while fetching appointment." in str(
            exc_info.value
        )
        assert exc_info.value.status_code == 500


class TestAppointmentExists:
    """Test cases for exists method."""

    @pytest.mark.asyncio
    async def test_exists_appointment_found(
        self,
        appointment_service: Appointment,
        sample_appointment_response: AppointmentResponse,
    ):
        """Test exists when appointment is found."""
        sample_appointment_response.message = "Appointment Found !!!"
        appointment_service.get = AsyncMock(return_value=sample_appointment_response)

        result = await appointment_service.exists("test-ref")

        assert result is True
        appointment_service.get.assert_called_once_with(
            AppointmentEndpoints.APPOINTMENT_EXISTS.format(reference="test-ref"),
            AppointmentResponse,
        )

    @pytest.mark.asyncio
    async def test_exists_appointment_not_found(
        self,
        appointment_service: Appointment,
        sample_appointment_response: AppointmentResponse,
    ):
        """Test exists when appointment is not found."""
        sample_appointment_response.message = "Appointment Not Found"
        appointment_service.get = AsyncMock(return_value=sample_appointment_response)

        result = await appointment_service.exists("test-ref")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_empty_reference(self, appointment_service: Appointment):
        """Test exists with empty reference."""
        result = await appointment_service.exists("")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_none_reference(self, appointment_service: Appointment):
        """Test exists with None reference."""
        result = await appointment_service.exists(None)
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_ehr_api_error(self, appointment_service: Appointment):
        """Test exists with EhrApiError."""
        appointment_service.get = AsyncMock(side_effect=EhrApiError("API Error", 400))

        with pytest.raises(EhrApiError):
            await appointment_service.exists("test-ref")

    @pytest.mark.asyncio
    async def test_exists_unexpected_error(self, appointment_service: Appointment):
        """Test exists with unexpected error."""
        appointment_service.get = AsyncMock(side_effect=Exception("Unexpected error"))

        with pytest.raises(EhrApiError) as exc_info:
            await appointment_service.exists("test-ref")

        assert (
            "An unexcepted error occurred while checking appointment existence."
            in str(exc_info.value)
        )
        assert exc_info.value.status_code == 500


class TestAppointmentDelete:
    """Test cases for delete method."""

    @pytest.mark.asyncio
    async def test_delete_success(self, appointment_service: Appointment):
        """Test successful delete."""
        # Mock the parent delete method
        with patch.object(
            appointment_service.__class__.__bases__[0], "delete", new_callable=AsyncMock
        ) as mock_delete:
            await appointment_service.delete("test-ref")

            mock_delete.assert_called_once_with(
                AppointmentEndpoints.DELETE_APPOINTMENT.format(reference="test-ref")
            )

    @pytest.mark.asyncio
    async def test_delete_empty_reference(self, appointment_service: Appointment):
        """Test delete with empty reference."""
        with pytest.raises(EhrApiError) as exc_info:
            await appointment_service.delete("")

        assert "Appointment Reference cannot be null or empty." in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_none_reference(self, appointment_service: Appointment):
        """Test delete with None reference."""
        with pytest.raises(EhrApiError) as exc_info:
            await appointment_service.delete(None)

        assert "Appointment Reference cannot be null or empty." in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_ehr_api_error(self, appointment_service: Appointment):
        """Test delete with EhrApiError."""
        with patch.object(
            appointment_service.__class__.__bases__[0], "delete", new_callable=AsyncMock
        ) as mock_delete:
            mock_delete.side_effect = EhrApiError("Not found", 404)

            with pytest.raises(EhrApiError):
                await appointment_service.delete("test-ref")

    @pytest.mark.asyncio
    async def test_delete_unexpected_error(self, appointment_service: Appointment):
        """Test delete with unexpected error."""
        with patch.object(
            appointment_service.__class__.__bases__[0], "delete", new_callable=AsyncMock
        ) as mock_delete:
            mock_delete.side_effect = Exception("Unexpected error")

            with pytest.raises(EhrApiError) as exc_info:
                await appointment_service.delete("test-ref")

            assert "An unexpected error occurred while deleting Appointment:" in str(
                exc_info.value
            )
            assert exc_info.value.status_code == 500


class TestAppointmentUpdate:
    """Test cases for update method."""

    @pytest.mark.asyncio
    async def test_update_success(
        self,
        sample_update_appointment_dto,
        appointment_service,
        sample_appointment_response,
    ):
        # No need to patch .dict — just compute the dict value
        expected_dict = sample_update_appointment_dto.model_dump(
            by_alias=True, exclude_none=True
        )

        appointment_service.put = AsyncMock(return_value=sample_appointment_response)

        result = await appointment_service.update(sample_update_appointment_dto)

        assert result == sample_appointment_response
        appointment_service.put.assert_called_once_with(
            AppointmentEndpoints.UPDATE_APPOINTMENT,
            expected_dict,
            response_model=AppointmentResponse,
        )

    @pytest.mark.asyncio
    async def test_update_ehr_api_error(
        self, appointment_service, sample_update_appointment_dto
    ):
        """Test update with EhrApiError."""
        expected_dict = sample_update_appointment_dto.model_dump(
            by_alias=True, exclude_none=True
        )

        appointment_service.put = AsyncMock(
            side_effect=EhrApiError("Update failed", 400)
        )

        with pytest.raises(EhrApiError):
            await appointment_service.update(sample_update_appointment_dto)

        appointment_service.put.assert_called_once_with(
            AppointmentEndpoints.UPDATE_APPOINTMENT,
            expected_dict,
            response_model=AppointmentResponse,
        )

    @pytest.mark.asyncio
    async def test_update_unexpected_error(
        self, appointment_service, sample_update_appointment_dto
    ):
        """Test update with unexpected error."""
        expected_dict = sample_update_appointment_dto.model_dump(
            by_alias=True, exclude_none=True
        )

        appointment_service.put = AsyncMock(side_effect=Exception("Unexpected error"))

        with pytest.raises(EhrApiError) as exc_info:
            await appointment_service.update(sample_update_appointment_dto)

        assert "An unexpected error occurred while updating appointment." in str(
            exc_info.value
        )
        assert exc_info.value.status_code == 500

        appointment_service.put.assert_called_once_with(
            AppointmentEndpoints.UPDATE_APPOINTMENT,
            expected_dict,
            response_model=AppointmentResponse,
        )


class TestAppointmentInitialization:
    """Test cases for service initialization."""

    def test_service_initialization(self, client_config: ClientConfig):
        """Test service initialization."""
        service = Appointment(client_config)

        assert service.logger is not None
        assert service.logger.name == "carestack.appointment.appointment_service"

    # @patch('carestack.appointment.appointment_service.logging.getLogger')
    # def test_logger_initialization(self, mock_get_logger, client_config: ClientConfig):
    #     """Test logger initialization."""
    #     mock_logger = client_config()
    #     mock_get_logger.return_value = mock_logger

    #     service = Appointment(client_config)

    #     mock_get_logger.assert_called_once_with("carestack.appointment.appointment_service")
    #     assert service.logger == mock_logger
