# this_file: test/test_configuration.py
"""Test configuration functionality."""

import pytest
from d361api import Configuration


class TestConfiguration:
    """Test suite for Configuration class."""

    def test_configuration_defaults(self):
        """Test configuration default values."""
        config = Configuration()
        assert config.host == "https://apihub.document360.io"
        assert config.api_key == {}
        assert config.api_key_prefix == {}
        assert config.username is None
        assert config.password is None

    def test_configuration_with_host(self):
        """Test configuration with custom host."""
        custom_host = "https://custom.example.com"
        config = Configuration(host=custom_host)
        assert config.host == custom_host

    def test_configuration_api_key_management(self):
        """Test API key management."""
        config = Configuration()
        
        # Test setting API key
        config.api_key['api_token'] = 'test-key'
        assert config.api_key['api_token'] == 'test-key'
        
        # Test API key prefix
        config.api_key_prefix['api_token'] = 'Bearer'
        assert config.api_key_prefix['api_token'] == 'Bearer'

    def test_configuration_ssl_verification(self):
        """Test SSL verification settings."""
        config = Configuration()
        assert config.verify_ssl is True
        assert config.ssl_ca_cert is None

    def test_configuration_timeout(self):
        """Test timeout configuration."""
        config = Configuration()
        # Default timeout should be set
        assert hasattr(config, 'timeout')

    def test_configuration_user_agent(self):
        """Test user agent configuration."""
        config = Configuration()
        assert hasattr(config, 'user_agent')
        assert 'd361api' in config.user_agent.lower()

    def test_configuration_proxy(self):
        """Test proxy configuration."""
        config = Configuration()
        assert hasattr(config, 'proxy')
        assert config.proxy is None

    def test_configuration_auth_settings(self):
        """Test authentication settings."""
        config = Configuration()
        config.username = 'test-user'
        config.password = 'test-pass'
        assert config.username == 'test-user'
        assert config.password == 'test-pass'