# this_file: test/conftest.py
"""Test configuration and fixtures."""

import pytest
from unittest.mock import Mock
from d361api import Configuration, ApiClient


@pytest.fixture
def config():
    """Create a test configuration."""
    config = Configuration()
    config.api_key['api_token'] = 'test-api-key'
    return config


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Mock(spec=Configuration)
    config.host = "https://test.example.com"
    config.api_key = {'api_token': 'mock-api-key'}
    config.api_key_prefix = {}
    config.username = None
    config.password = None
    config.verify_ssl = True
    config.ssl_ca_cert = None
    config.timeout = None
    config.proxy = None
    return config


@pytest.fixture
def api_client(config):
    """Create a test API client."""
    return ApiClient(configuration=config)


@pytest.fixture
def mock_api_client(mock_config):
    """Create a mock API client for testing."""
    client = Mock(spec=ApiClient)
    client.configuration = mock_config
    return client


@pytest.fixture
def sample_article_data():
    """Sample article data for testing."""
    return {
        'id': 'test-article-id',
        'title': 'Test Article',
        'content': 'This is test content for the article.',
        'category_id': 'test-category-id',
        'status': 'published',
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for testing."""
    return {
        'id': 'test-category-id',
        'name': 'Test Category',
        'description': 'This is a test category.',
        'parent_id': None,
        'order': 1,
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }


@pytest.fixture
def sample_project_version_data():
    """Sample project version data for testing."""
    return {
        'id': 'test-project-version-id',
        'name': 'Test Project Version',
        'version': '1.0.0',
        'is_default': True,
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'id': 'test-user-id',
        'email': 'test@example.com',
        'name': 'Test User',
        'role': 'admin',
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks after each test."""
    yield
    # Any cleanup code would go here