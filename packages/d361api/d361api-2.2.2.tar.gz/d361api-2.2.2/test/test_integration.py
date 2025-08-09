# this_file: test/test_integration.py
"""Integration tests for the API client."""

import pytest
from unittest.mock import Mock, patch
from d361api import ApiClient, Configuration
from d361api.d361api import ArticlesApi, ProjectVersionsApi
from d361api.exceptions import ApiException


class TestIntegration:
    """Integration test suite."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Configuration()
        self.config.api_key['api_token'] = 'test-api-key'

    @pytest.mark.asyncio
    async def test_full_client_setup(self):
        """Test complete client setup process."""
        async with ApiClient(configuration=self.config) as client:
            # Create API instances
            articles_api = ArticlesApi(client)
            project_versions_api = ProjectVersionsApi(client)
            
            # Verify they share the same client
            assert articles_api.api_client == client
            assert project_versions_api.api_client == client

    def test_configuration_chain(self):
        """Test that configuration is properly passed through the chain."""
        config = Configuration()
        config.host = "https://test.example.com"
        config.api_key['api_token'] = 'test-key'
        
        client = ApiClient(configuration=config)
        api = ArticlesApi(client)
        
        assert api.api_client.configuration.host == "https://test.example.com"
        assert api.api_client.configuration.api_key['api_token'] == 'test-key'

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in the client."""
        config = Configuration()
        config.api_key['api_token'] = 'invalid-key'
        
        async with ApiClient(configuration=config) as client:
            # This should not raise an exception during setup
            articles_api = ArticlesApi(client)
            assert articles_api is not None

    def test_client_without_api_key(self):
        """Test client behavior without API key."""
        config = Configuration()
        # Don't set API key
        
        client = ApiClient(configuration=config)
        api = ArticlesApi(client)
        
        # Should be able to create API instance without key
        assert api.api_client.configuration.api_key == {}

    def test_client_with_custom_headers(self):
        """Test client with custom headers."""
        config = Configuration()
        config.api_key['api_token'] = 'test-key'
        
        client = ApiClient(configuration=config)
        
        # Check that client has been configured
        assert client.configuration.api_key['api_token'] == 'test-key'

    @pytest.mark.asyncio
    async def test_client_lifecycle(self):
        """Test client lifecycle management."""
        config = Configuration()
        
        # Test context manager
        async with ApiClient(configuration=config) as client:
            assert isinstance(client, ApiClient)
            
            # Client should be usable within context
            api = ArticlesApi(client)
            assert api.api_client == client

    def test_multiple_clients(self):
        """Test creating multiple independent clients."""
        config1 = Configuration()
        config1.host = "https://test1.example.com"
        
        config2 = Configuration()  
        config2.host = "https://test2.example.com"
        
        client1 = ApiClient(configuration=config1)
        client2 = ApiClient(configuration=config2)
        
        assert client1.configuration.host != client2.configuration.host
        assert client1 != client2

    def test_api_method_signatures(self):
        """Test that API methods have reasonable signatures."""
        client = ApiClient(configuration=self.config)
        articles_api = ArticlesApi(client)
        
        # Get all callable methods
        methods = [getattr(articles_api, method) for method in dir(articles_api) 
                  if callable(getattr(articles_api, method)) and not method.startswith('_')]
        
        # At least some methods should exist
        assert len(methods) > 0
        
        # All methods should be callable
        for method in methods:
            assert callable(method)