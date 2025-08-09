# this_file: test/test_api_client.py
"""Test API client functionality."""

import pytest
from unittest.mock import Mock, patch
from d361api import ApiClient, Configuration
from d361api.exceptions import ApiException


class TestApiClient:
    """Test suite for ApiClient class."""

    def test_api_client_initialization(self):
        """Test that ApiClient can be initialized with configuration."""
        config = Configuration()
        client = ApiClient(configuration=config)
        assert client.configuration == config

    def test_api_client_default_configuration(self):
        """Test that ApiClient uses default configuration when none provided."""
        client = ApiClient()
        assert client.configuration is not None
        assert isinstance(client.configuration, Configuration)

    def test_configuration_host_default(self):
        """Test that Configuration has correct default host."""
        config = Configuration()
        assert config.host == "https://apihub.document360.io"

    def test_configuration_api_key_setting(self):
        """Test that API key can be set in configuration."""
        config = Configuration()
        config.api_key['api_token'] = 'test-api-key'
        assert config.api_key['api_token'] == 'test-api-key'

    def test_configuration_with_custom_host(self):
        """Test that custom host can be set."""
        custom_host = "https://custom.document360.io"
        config = Configuration(host=custom_host)
        assert config.host == custom_host

    @pytest.mark.asyncio
    async def test_api_client_context_manager(self):
        """Test that ApiClient can be used as an async context manager."""
        config = Configuration()
        async with ApiClient(configuration=config) as client:
            assert isinstance(client, ApiClient)

    def test_api_exception_creation(self):
        """Test that ApiException can be created."""
        status = 404
        reason = "Not Found"
        exception = ApiException(status=status, reason=reason)
        assert exception.status == status
        assert exception.reason == reason