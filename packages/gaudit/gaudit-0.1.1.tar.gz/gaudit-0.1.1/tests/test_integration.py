"""
Integration tests for GLIMPS Audit API Client

These tests require a real API server and valid credentials.
They are marked with @pytest.mark.integration and can be skipped with:
    pytest -m "not integration"
"""

import pytest
import os
from gaudit.client import GlimpsAuditClient


# Skip all tests in this module if GLIMPS_TEST_API_URL is not set
pytestmark = pytest.mark.skipif(
    not os.environ.get("GLIMPS_TEST_API_URL"),
    reason="Integration tests require GLIMPS_TEST_API_URL environment variable"
)


@pytest.fixture
def api_credentials():
    """Get API credentials from environment variables"""
    return {
        "base_url": os.environ.get("GLIMPS_TEST_API_URL", "https://gaudit.glimps.re/api/v2"),
        "email": os.environ.get("GLIMPS_TEST_EMAIL"),
        "password": os.environ.get("GLIMPS_TEST_PASSWORD"),
    }


@pytest.fixture
def authenticated_client(api_credentials):
    """Create an authenticated client for integration tests"""
    if not api_credentials["email"] or not api_credentials["password"]:
        pytest.skip("Integration tests require GLIMPS_TEST_EMAIL and GLIMPS_TEST_PASSWORD")

    client = GlimpsAuditClient(base_url=api_credentials["base_url"], verify_ssl=True)
    client.login(api_credentials["email"], api_credentials["password"])
    return client


@pytest.mark.integration
class TestIntegrationAuth:
    """Integration tests for authentication"""

    def test_login_logout_cycle(self, api_credentials):
        """Test complete login/logout cycle"""
        client = GlimpsAuditClient(base_url=api_credentials["base_url"])

        # Login
        result = client.login(api_credentials["email"], api_credentials["password"])
        assert "token" in result
        assert client.is_token_valid()

        # Verify we can make authenticated requests
        user_props = client.get_user_properties()
        assert "email" in user_props

        # Token should still be valid
        assert client.is_token_valid()

    def test_token_refresh(self, authenticated_client):
        """Test token refresh functionality"""
        old_token = authenticated_client.token

        # Refresh token
        result = authenticated_client.refresh_token()
        assert "token" in result

        # Token should have changed
        assert authenticated_client.token != old_token
        assert authenticated_client.is_token_valid()


@pytest.mark.integration
class TestIntegrationUser:
    """Integration tests for user endpoints"""

    def test_get_user_properties(self, authenticated_client):
        """Test getting user properties"""
        props = authenticated_client.get_user_properties()

        assert "username" in props
        assert "email" in props
        assert "admin" in props
        assert "services" in props
        assert isinstance(props["services"], list)

    def test_get_user_analyses(self, authenticated_client):
        """Test getting user analyses stats"""
        stats = authenticated_client.get_user_analyses()

        assert "analyses" in stats
        assert "disk_usage" in stats
        assert "analysis_duration" in stats
        assert isinstance(stats["analyses"], int)


@pytest.mark.integration
class TestIntegrationAudit:
    """Integration tests for audit endpoints"""

    def test_get_audit_groups(self, authenticated_client):
        """Test getting audit groups"""
        groups = authenticated_client.get_audit_groups()
        assert isinstance(groups, list)

    def test_list_audits(self, authenticated_client):
        """Test listing audits"""
        result = authenticated_client.list_audits(page_size=5)

        assert "audits" in result
        assert "count" in result
        assert isinstance(result["audits"], list)

    @pytest.mark.slow
    def test_audit_workflow(self, authenticated_client, tmp_path):
        """Test complete audit workflow: upload, create, get, delete"""
        # This test requires:
        # 1. Valid audit groups configured for the test user
        # 2. Sufficient permissions to create/delete audits

        groups = authenticated_client.get_audit_groups()
        if not groups:
            pytest.skip("No audit groups available for testing")

        # Create a test file
        test_file = tmp_path / "test_binary.exe"
        test_file.write_bytes(b"MZ" + b"\x00" * 1022)  # Minimal PE header

        # Upload file
        upload_result = authenticated_client.upload_file_for_audit(str(test_file))
        assert "id" in upload_result
        file_id = upload_result["id"]

        # Create audit
        audit_result = authenticated_client.create_audit(
            group=groups[0],
            files={file_id: "test_binary.exe"},
            comment="Integration test audit"
        )
        assert "aids" in audit_result
        assert len(audit_result["aids"]) > 0
        audit_id = audit_result["aids"][0]

        # Get audit details
        audit_details = authenticated_client.get_audit(audit_id)
        assert audit_details["audit"]["id"] == audit_id

        # Delete audit
        delete_result = authenticated_client.delete_audit(audit_id)
        assert delete_result.get("status") is True


@pytest.mark.integration
class TestIntegrationLibrary:
    """Integration tests for library endpoints"""

    def test_list_libraries(self, authenticated_client):
        """Test listing libraries"""
        result = authenticated_client.list_libraries(page_size=10)

        assert "libraries" in result
        assert "count" in result
        assert isinstance(result["libraries"], list)

        if result["libraries"]:
            lib = result["libraries"][0]
            assert "binary_name" in lib
            assert "sha256" in lib


@pytest.mark.integration
class TestIntegrationDataset:
    """Integration tests for dataset endpoints"""

    def test_list_datasets(self, authenticated_client):
        """Test listing datasets"""
        result = authenticated_client.list_datasets()

        assert "datasets" in result
        assert "count" in result
        assert isinstance(result["datasets"], list)

    @pytest.mark.slow
    def test_dataset_workflow(self, authenticated_client, tmp_path):
        """Test complete dataset workflow: create, add entries, list, delete"""
        import time

        # Create unique dataset name
        dataset_name = f"test_ds_{int(time.time())}"

        try:
            # Create dataset
            create_result = authenticated_client.create_dataset(
                dataset_name,
                "Integration test dataset"
            )
            assert "kind" in create_result

            # List datasets to verify creation
            datasets = authenticated_client.list_datasets()
            dataset_names = [ds["name"] for ds in datasets["datasets"]]
            assert dataset_name in dataset_names

            # Get dataset entries (should be empty)
            entries = authenticated_client.get_dataset_entries(dataset_name)
            assert entries["count"] == 0

        finally:
            # Clean up - delete dataset
            try:
                authenticated_client.delete_dataset(dataset_name)
            except Exception:
                pass  # Ignore cleanup errors


# Helper function to run integration tests
def run_integration_tests():
    """
    Run integration tests with proper environment setup.

    Example usage:
        export GLIMPS_TEST_API_URL="https://gaudit.glimps.re/api/v2"
        export GLIMPS_TEST_EMAIL="test@example.com"
        export GLIMPS_TEST_PASSWORD="password"
        pytest tests/test_integration.py -v
    """
    import subprocess
    import sys

    required_vars = ["GLIMPS_TEST_API_URL", "GLIMPS_TEST_EMAIL", "GLIMPS_TEST_PASSWORD"]
    missing = [var for var in required_vars if not os.environ.get(var)]

    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        print("\nTo run integration tests, set the following environment variables:")
        for var in required_vars:
            print(f"  export {var}='your-value-here'")
        sys.exit(1)

    # Run pytest with integration tests
    subprocess.run([sys.executable, "-m", "pytest", __file__, "-v", "-m", "integration"])
