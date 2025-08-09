"""
Unit tests for the GLIMPS Audit API Client
"""

import pytest
import responses
from datetime import datetime, timedelta
from gaudit.client import GlimpsAuditClient
from .utils import (
    create_mock_audit_response,
    create_mock_library,
    create_test_binary,
    assert_api_error
)

@pytest.fixture
def authenticated_client():
    client = GlimpsAuditClient()
    client.token = "test-token"
    return client

@pytest.fixture
def client():
    """Create a test client instance"""
    return GlimpsAuditClient(url="https://test.api/v2", verify_ssl=True)


@pytest.fixture
def auth_client():
    """Create an authenticated test client instance"""
    client = GlimpsAuditClient(url="https://test.api/v2", verify_ssl=True)
    client.token = "test-token-123"
    client.token_expiry = datetime.now() + timedelta(hours=1)
    return client


class TestAuthentication:
    """Test authentication-related methods"""

    @responses.activate
    def test_login_success(self, client):
        """Test successful login"""
        responses.add(
            responses.POST,
            "https://test.api/api/v2/user/login",
            json={
                "name": "testuser",
                "validity": 86400000,
                "token": "jwt-token-123",
                "group": "testgroup",
                "services": ["GlimpsLibCorrelate"],
                "role": "user"
            },
            status=200
        )

        result = client.login("test@example.com", "password123")

        assert result["name"] == "testuser"
        assert result["token"] == "jwt-token-123"
        assert client.token == "jwt-token-123"
        assert client.token_expiry is not None

    @responses.activate
    def test_login_failure(self, client):
        """Test failed login with invalid credentials"""
        responses.add(
            responses.POST,
            "https://test.api/api/v2/user/login",
            json={"status": False, "error": "Unauthorized"},
            status=401
        )

        with pytest.raises(Exception) as exc_info:
            client.login("test@example.com", "wrongpassword")

        assert "API Error 401: Unauthorized" in str(exc_info.value)

    @responses.activate
    def test_refresh_token(self, auth_client):
        """Test token refresh"""
        responses.add(
            responses.POST,
            "https://test.api/api/v2/user/refresh",
            json={
                "name": "testuser",
                "validity": 86400000,
                "token": "new-jwt-token-456",
                "group": "testgroup",
                "services": ["GlimpsLibCorrelate"],
                "role": "user"
            },
            status=200
        )

        result = auth_client.refresh_token()

        assert result["token"] == "new-jwt-token-456"
        assert auth_client.token == "new-jwt-token-456"

    def test_is_token_valid(self, auth_client):
        """Test token validity check"""
        assert auth_client.is_token_valid() is True

        # Test with expired token
        auth_client.token_expiry = datetime.now() - timedelta(hours=1)
        assert auth_client.is_token_valid() is False

        # Test with no token
        auth_client.token = None
        assert auth_client.is_token_valid() is False


class TestUserManagement:
    """Test user management endpoints"""

    @responses.activate
    def test_change_password(self, auth_client):
        """Test password change"""
        responses.add(
            responses.POST,
            "https://test.api/api/v2/user/password",
            json={"status": True, "message": "password updated"},
            status=200
        )

        result = auth_client.change_password("oldpass", "newpass")
        assert result["status"] is True
        assert result["message"] == "password updated"

    @responses.activate
    def test_get_user_properties(self, auth_client):
        """Test getting user properties"""
        responses.add(
            responses.GET,
            "https://test.api/api/v2/user/properties",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "admin": False,
                "picture": "",
                "services": ["GlimpsLibCorrelate"]
            },
            status=200
        )

        result = auth_client.get_user_properties()
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
        assert result["admin"] is False

    @responses.activate
    def test_get_user_analyses(self, auth_client):
        """Test getting user analyses stats"""
        responses.add(
            responses.GET,
            "https://test.api/api/v2/user/analyses",
            json={
                "analyses": 3,
                "delete_old": False,
                "duration": 365,
                "disk_usage": 11678324,
                "disk_available": 0,
                "analysis_duration": 50047
            },
            status=200
        )

        result = auth_client.get_user_analyses()
        assert result["analyses"] == 3
        assert result["disk_usage"] == 11678324

    @responses.activate
    def test_delete_user_analyses(self, auth_client):
        """Test deleting user analyses"""
        responses.add(
            responses.POST,
            "https://test.api/api/v2/user/delete_analyses",
            json={"status": True, "message": "analyses deleted"},
            status=200
        )

        result = auth_client.delete_user_analyses()
        assert result["status"] is True


class TestAuditEndpoints:
    """Test audit-related endpoints"""

    @responses.activate
    def test_get_audit_groups(self, auth_client):
        """Test getting audit groups"""
        responses.add(
            responses.GET,
            "https://test.api/api/v2/audits/groups",
            json=["group1", "group2", "group3"],
            status=200
        )

        result = auth_client.get_audit_groups()
        assert len(result) == 3
        assert "group1" in result

    @responses.activate
    def test_create_audit(self, auth_client):
        """Test creating an audit"""
        responses.add(
            responses.POST,
            "https://test.api/api/v2/audits",
            json={
                "status": True,
                "ids": ["file-id-123"],
                "aids": ["audit-id-456"]
            },
            status=200
        )

        result = auth_client.create_audit(
            group="testgroup",
            files={"file-id-123": "test.exe"},
            comment="Test audit",
            services={"GlimpsLibCorrelate": {"dataset": "default"}}
        )

        assert result["status"] is True
        assert result["ids"] == ["file-id-123"]
        assert result["aids"] == ["audit-id-456"]

    @responses.activate
    def test_list_audits(self, auth_client):
        """Test listing audits"""
        responses.add(
            responses.GET,
            "https://test.api/api/v2/audits",
            json={
                "status": True,
                "count": 1,
                "audits": [{
                    "id": "audit-id-123",
                    "filename": "test.exe",
                    "filetype": "PE",
                    "arch": "amd64",
                    "group": "testgroup",
                    "comment": "Test",
                    "size": 1024,
                    "viewed": False,
                    "failed": False,
                    "done": True,
                    "user": "test@example.com",
                    "files": 1,
                    "created_at": "2023-01-01T00:00:00Z",
                    "done_at": "2023-01-01T00:05:00Z"
                }]
            },
            status=200
        )

        result = auth_client.list_audits(page_size=10)
        assert result["count"] == 1
        assert len(result["audits"]) == 1
        assert result["audits"][0]["id"] == "audit-id-123"

    @responses.activate
    def test_get_audit(self, auth_client):
        """Test getting audit details"""
        mock_audit = create_mock_audit_response(
            audit_id="audit-id-123",
            filename="test.exe",
            done=True,
            libraries=[create_mock_library("msvcrt", "7.0.0", 95.5)]
        )

        responses.add(
            responses.GET,
            "https://test.api/api/v2/audits/audit-id-123",
            json=mock_audit,
            status=200
        )

        result = auth_client.get_audit("audit-id-123")
        assert result["audit"]["id"] == "audit-id-123"
        assert len(result["audit"]["libraries"]) == 1
        assert result["audit"]["libraries"][0]["name"] == "msvcrt"

    @responses.activate
    def test_delete_audit(self, auth_client):
        """Test deleting an audit"""
        responses.add(
            responses.DELETE,
            "https://test.api/api/v2/audits/audit-id-123",
            json={"status": True, "message": "analysis deleted"},
            status=200
        )

        result = auth_client.delete_audit("audit-id-123")
        assert result["status"] is True

    @responses.activate
    def test_upload_file_for_audit(self, auth_client, tmp_path):
        """Test uploading a file for audit"""
        # Create a test file
        test_file = tmp_path / "test.exe"
        create_test_binary(test_file)

        responses.add(
            responses.POST,
            "https://test.api/api/v2/audits/upload",
            json={"status": True, "id": "sha256-hash-123"},
            status=200
        )

        result = auth_client.upload_file_for_audit(str(test_file))
        assert result["status"] is True
        assert result["id"] == "sha256-hash-123"

    @responses.activate
    def test_generate_idc(self, auth_client):
        """Test generating IDC file"""
        responses.add(
            responses.POST,
            "https://test.api/api/v2/audits/audit-id-123/idc",
            body='static main() {\nset_name(0x004490c0, "GDS_get_user_var");\n}',
            content_type="text/plain",
            status=200
        )

        result = auth_client.generate_idc("audit-id-123", ["lib-id-1", "lib-id-2"])
        assert "static main()" in result
        assert "set_name" in result

    @responses.activate
    def test_download_audit_binary(self, auth_client, tmp_path):
        """Test downloading binary from audit"""
        binary_content = b"test binary content"
        responses.add(
            responses.GET,
            "https://test.api/api/v2/audits/audit-id-123/file-id-456/binary",
            body=binary_content,
            content_type="application/octet-stream",
            status=200
        )

        save_path = tmp_path / "downloaded.exe"
        result = auth_client.download_audit_binary("audit-id-123", "file-id-456", str(save_path))

        assert result == binary_content
        assert save_path.read_bytes() == binary_content


class TestLibraryEndpoints:
    """Test library endpoints"""

    @responses.activate
    def test_list_libraries(self, auth_client):
        """Test listing libraries"""
        responses.add(
            responses.GET,
            "https://test.api/api/v2/libraries",
            json={
                "status": True,
                "count": 100,
                "libraries": [{
                    "source_name": "Win10",
                    "project_name": "Microsoft",
                    "binary_name": "kernel32.dll",
                    "size": 2048,
                    "sha256": "hash123",
                    "architecture": "amd64",
                    "file_format": "PE"
                }]
            },
            status=200
        )

        result = auth_client.list_libraries(filter="kernel", page_size=50)
        assert result["count"] == 100
        assert len(result["libraries"]) == 1
        assert result["libraries"][0]["binary_name"] == "kernel32.dll"


class TestDatasetEndpoints:
    """Test dataset endpoints"""

    @responses.activate
    def test_list_datasets(self, auth_client):
        """Test listing datasets"""
        responses.add(
            responses.GET,
            "https://test.api/api/v2/datasets",
            json={
                "status": True,
                "count": 2,
                "datasets": [{
                    "group": "testgroup",
                    "name": "test_dataset",
                    "comment": "Test dataset",
                    "kind": "udb:testgroup:hash123"
                }]
            },
            status=200
        )

        result = auth_client.list_datasets()
        assert result["count"] == 2
        assert result["datasets"][0]["name"] == "test_dataset"

    @responses.activate
    def test_create_dataset(self, auth_client):
        """Test creating a dataset"""
        responses.add(
            responses.POST,
            "https://test.api/api/v2/datasets",
            json={
                "status": True,
                "kind": "udb:testgroup:newhash456"
            },
            status=200
        )

        result = auth_client.create_dataset("new_dataset", "Description")
        assert result["status"] is True
        assert result["kind"] == "udb:testgroup:newhash456"

    @responses.activate
    def test_delete_dataset(self, auth_client):
        """Test deleting a dataset"""
        responses.add(
            responses.DELETE,
            "https://test.api/api/v2/datasets/test_dataset",
            json={"status": True},
            status=200
        )

        result = auth_client.delete_dataset("test_dataset")
        assert result["status"] is True

    @responses.activate
    def test_get_dataset_entries(self, auth_client):
        """Test getting dataset entries"""
        responses.add(
            responses.GET,
            "https://test.api/api/v2/datasets/test_dataset",
            json={
                "count": 1,
                "entries": [{
                    "project_name": "test",
                    "binary_name": "test.exe",
                    "size": 1024,
                    "sha256": "hash123",
                    "architecture": "amd64",
                    "file_format": "PE"
                }]
            },
            status=200
        )

        result = auth_client.get_dataset_entries("test_dataset")
        assert result["count"] == 1
        assert result["entries"][0]["binary_name"] == "test.exe"

    @responses.activate
    def test_add_dataset_entries(self, auth_client):
        """Test adding entries to dataset"""
        responses.add(
            responses.POST,
            "https://test.api/api/v2/datasets/test_dataset",
            json={
                "status": True,
                "files": [{
                    "id": "file-id-123",
                    "status": True
                }]
            },
            status=200
        )

        result = auth_client.add_dataset_entries(
            "test_dataset",
            "TestProject",
            [{"id": "file-id-123", "binary_name": "test.exe", "version": "1.0"}]
        )
        assert result["status"] is True
        assert result["files"][0]["status"] is True

    @responses.activate
    def test_update_dataset(self, auth_client):
        """Test updating dataset"""
        responses.add(
            responses.POST,
            "https://test.api/api/v2/datasets/test_dataset/update",
            status=202
        )

        # Should not raise exception
        auth_client.update_dataset("test_dataset")


class TestErrorHandling:
    """Test error handling"""

    @responses.activate
    def test_handle_400_error(self, auth_client):
        """Test handling 400 Bad Request"""
        responses.add(
            responses.GET,
            "https://test.api/api/v2/audits/invalid",
            json={
                "status": False,
                "error": "Bad Request",
                "details": "Invalid audit ID format"
            },
            status=400
        )

        with pytest.raises(Exception) as exc_info:
            auth_client.get_audit("invalid")

        assert_api_error(exc_info, 400, "Bad Request")
        assert "Invalid audit ID format" in str(exc_info.value)

    @responses.activate
    def test_handle_401_error(self, auth_client):
        """Test handling 401 Unauthorized"""
        responses.add(
            responses.GET,
            "https://test.api/api/v2/user/properties",
            json={"status": False, "error": "Unauthorized"},
            status=401
        )

        with pytest.raises(Exception) as exc_info:
            auth_client.get_user_properties()

        assert_api_error(exc_info, 401, "Unauthorized")

    @responses.activate
    def test_handle_non_json_error(self, auth_client):
        """Test handling non-JSON error response"""
        responses.add(
            responses.GET,
            "https://test.api/api/v2/audits",
            body="Internal Server Error",
            status=500
        )

        with pytest.raises(Exception) as exc_info:
            auth_client.list_audits()

        assert "API Error 500: Internal Server Error" in str(exc_info.value)


class TestUtilities:
    """Test utility methods"""

    def test_ensure_authenticated_no_token(self, client):
        """Test ensure_authenticated with no token"""
        with pytest.raises(Exception) as exc_info:
            client.ensure_authenticated()

        assert "Not authenticated" in str(exc_info.value)

    @responses.activate
    def test_ensure_authenticated_refresh_token(self, auth_client):
        """Test ensure_authenticated refreshes expired token"""
        # Set token as expired
        auth_client.token_expiry = datetime.now() - timedelta(hours=1)

        responses.add(
            responses.POST,
            "https://test.api/api/v2/user/refresh",
            json={
                "name": "testuser",
                "validity": 86400000,
                "token": "new-token-789",
                "group": "testgroup",
                "services": ["GlimpsLibCorrelate"],
                "role": "user"
            },
            status=200
        )

        auth_client.ensure_authenticated()
        assert auth_client.token == "new-token-789"
