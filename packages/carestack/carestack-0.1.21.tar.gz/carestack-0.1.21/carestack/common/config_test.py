import pytest
from carestack.base.base_types import ClientConfig


@pytest.fixture
def client_config() -> ClientConfig:
    """
    Provides a ClientConfig instance initialized with API credentials from environment variables.

    Raises:
        ValueError: If API_KEY environment variables are not set.

    Returns:
        ClientConfig: Configured with API key and URL.
    """

    return ClientConfig(
        api_key="test_api_key",
        x_hpr_id="test_x_hpr_id",
        api_url="http://test.api.url",
    )
