"""
Shared fixtures for all tests
"""

import pytest
from unittest.mock import MagicMock
from gaudit.client import GlimpsAuditClient


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file"""
    config_file = tmp_path / "config.json"
    return config_file


@pytest.fixture
def mock_client():
    """Create a mock GlimpsAuditClient"""
    client = MagicMock(spec=GlimpsAuditClient)
    client.base_url = "https://test.api/v2"
    client.verify_ssl = True
    client.token = None
    client.token_expiry = None
    return client


@pytest.fixture
def authenticated_mock_client(mock_client):
    """Create an authenticated mock client"""
    mock_client.token = "test-token-123"
    mock_client.is_token_valid.return_value = True
    return mock_client


@pytest.fixture
def sample_config_data():
    """Sample configuration data"""
    return {
        "base_url": "https://test.api/v2",
        "email": "test@example.com",
        "token": "test-token-123",
        "verify_ssl": True
    }


@pytest.fixture
def sample_audit_response():
    """Sample audit response data"""
    return {
        "status": True,
        "audit": {
            "id": "audit-123",
            "filename": "test.exe",
            "filetype": "PE",
            "arch": "amd64",
            "group": "testgroup",
            "comment": "Test audit",
            "size": 1024,
            "done": True,
            "created_at": "2023-01-01T00:00:00Z",
            "done_at": "2023-01-01T00:05:00Z",
            "libraries": [{
                "name": "testlib",
                "desc": "Test Library",
                "files": {
                    "testlib.dll": [{
                        "version": "1.0.0",
                        "arch": "amd64",
                        "score": 95.0
                    }]
                }
            }]
        }
    }


@pytest.fixture
def sample_user_properties():
    """Sample user properties response"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "admin": False,
        "picture": "",
        "services": ["GlimpsLibCorrelate"]
    }


@pytest.fixture
def cli_runner():
    """Click CLI test runner"""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture(autouse=True)
def reset_config_module(monkeypatch):
    """Reset CONFIG_FILE for each test to avoid conflicts"""
    # This ensures each test gets a fresh config setup
    import gaudit.config
    original_config_file = gaudit.config.CONFIG_FILE
    yield
    gaudit.config.CONFIG_FILE = original_config_file
