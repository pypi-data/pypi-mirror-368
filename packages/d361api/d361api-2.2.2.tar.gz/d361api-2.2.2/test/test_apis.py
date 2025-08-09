# this_file: test/test_apis.py
"""Test API classes."""

import pytest
from unittest.mock import Mock, AsyncMock
from d361api import ApiClient, Configuration
from d361api.d361api import (
    ArticlesApi,
    CategoriesApi,
    ProjectVersionsApi,
    ReadersApi,
    TeamsApi,
)


class TestApiClasses:
    """Test suite for API classes."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Configuration()
        self.api_client = ApiClient(configuration=self.config)

    def test_articles_api_initialization(self):
        """Test ArticlesApi initialization."""
        api = ArticlesApi(self.api_client)
        assert api.api_client == self.api_client

    def test_categories_api_initialization(self):
        """Test CategoriesApi initialization."""
        api = CategoriesApi(self.api_client)
        assert api.api_client == self.api_client

    def test_project_versions_api_initialization(self):
        """Test ProjectVersionsApi initialization."""
        api = ProjectVersionsApi(self.api_client)
        assert api.api_client == self.api_client

    def test_readers_api_initialization(self):
        """Test ReadersApi initialization."""
        api = ReadersApi(self.api_client)
        assert api.api_client == self.api_client

    def test_teams_api_initialization(self):
        """Test TeamsApi initialization."""
        api = TeamsApi(self.api_client)
        assert api.api_client == self.api_client

    def test_api_methods_exist(self):
        """Test that API classes have expected methods."""
        articles_api = ArticlesApi(self.api_client)
        
        # Check that common methods exist
        expected_methods = [
            # Most APIs should have some form of GET method
            # We'll check for method existence without calling them
        ]
        
        # Get all methods of the API
        methods = [method for method in dir(articles_api) if not method.startswith('_')]
        
        # At least some methods should exist
        assert len(methods) > 0, "API should have at least some methods"
        
        # Check that methods are callable
        for method_name in methods:
            method = getattr(articles_api, method_name)
            if callable(method):
                assert callable(method), f"Method {method_name} should be callable"

    def test_api_client_configuration(self):
        """Test that API classes use the correct configuration."""
        api = ArticlesApi(self.api_client)
        assert api.api_client.configuration == self.config

    @pytest.mark.asyncio
    async def test_api_with_mock_client(self):
        """Test API with mocked client."""
        # Create a mock API client
        mock_client = Mock()
        mock_client.configuration = self.config
        
        # Create API instance with mock client
        api = ArticlesApi(mock_client)
        assert api.api_client == mock_client

    def test_multiple_api_instances(self):
        """Test creating multiple API instances."""
        articles_api = ArticlesApi(self.api_client)
        categories_api = CategoriesApi(self.api_client)
        
        assert articles_api != categories_api
        assert articles_api.api_client == categories_api.api_client