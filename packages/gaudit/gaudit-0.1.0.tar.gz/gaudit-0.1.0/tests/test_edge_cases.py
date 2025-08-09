"""
Test edge cases and error conditions
"""

import pytest
import json
import responses
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from gaudit.client import GlimpsAuditClient
from gaudit.config import load_config, save_config, Config
from gaudit.cli import gcli


@pytest.fixture
def authenticated_client():
    client = GlimpsAuditClient()
    client.token = "test-token"
    return client


class TestClientEdgeCases:
    """Test edge cases in the client library"""

    def test_client_with_custom_base_url_trailing_slash(self):
        """Test client handles trailing slashes in base URL"""
        client1 = GlimpsAuditClient(url="https://api.test.com/v2/")
        client2 = GlimpsAuditClient(url="https://api.test.com/v2")

        # Both should result in the same base URL without trailing slash
        assert client1.base_url == "https://api.test.com/api/v2"
        assert client2.base_url == "https://api.test.com/api/v2"

    @responses.activate
    def test_empty_response_handling(self):
        """Test handling of empty responses"""
        client = GlimpsAuditClient()
        client.token = "test-token"

        responses.add(
            responses.GET,
            "https://gaudit.glimps.re/api/v2/audits/groups",
            json=[],
            status=200
        )

        result = client.get_audit_groups()
        assert result == []

    @responses.activate
    def test_malformed_json_response(self):
        """Test handling of malformed JSON responses"""
        client = GlimpsAuditClient()
        client.token = "test-token"

        responses.add(
            responses.GET,
            "https://gaudit.glimps.re/api/v2/user/properties",
            body="<html>Not JSON</html>",
            content_type="text/html",
            status=200
        )

        # Should return the text content
        result = client.get_user_properties()
        assert "<html>Not JSON</html>" in result

    def test_token_expiry_edge_cases(self):
        """Test token expiry edge cases"""
        client = GlimpsAuditClient()

        # No token
        assert not client.is_token_valid()

        # Token but no expiry
        client.token = "test-token"
        assert not client.is_token_valid()

        # Expired by exactly 1 second
        client.token_expiry = datetime.now() - timedelta(seconds=1)
        assert not client.is_token_valid()

        # Valid for exactly 1 second
        client.token_expiry = datetime.now() + timedelta(seconds=1)
        assert client.is_token_valid()

    @responses.activate
    def test_file_upload_with_special_characters(self, tmp_path):
        """Test file upload with special characters in filename"""
        client = GlimpsAuditClient()
        client.token = "test-token"

        # Create file with special characters
        test_file = tmp_path / "test file (special) [chars] #1.exe"
        test_file.write_bytes(b"test content")

        responses.add(
            responses.POST,
            "https://gaudit.glimps.re/api/v2/audits/upload",
            json={"status": True, "id": "file-id-123"},
            status=200
        )

        result = client.upload_file_for_audit(str(test_file))
        assert result["id"] == "file-id-123"

    @responses.activate
    def test_pagination_edge_cases(self):
        """Test pagination edge cases"""
        client = GlimpsAuditClient()
        client.token = "test-token"

        # Test with maximum page size
        responses.add(
            responses.GET,
            "https://gaudit.glimps.re/api/v2/audits",
            json={"audits": [], "count": 0},
            status=200
        )

        result = client.list_audits(page_size=1000, page_number=0)
        assert result["count"] == 0

        # Verify request was made with correct params
        assert len(responses.calls) == 1
        assert "pageSize=1000" in responses.calls[0].request.url


class TestConfigEdgeCases:
    """Test edge cases in configuration handling"""

    def test_config_file_corruption(self, tmp_path, monkeypatch):
        """Test handling of corrupted config file"""
        config_file = tmp_path / "config.json"
        config_file.write_text("{invalid json content")

        monkeypatch.setattr("gaudit.config.CONFIG_FILE", config_file)

        # Should handle gracefully and return empty dict
        with pytest.raises(json.JSONDecodeError):
            load_config()

    def test_config_file_permissions(self, tmp_path, monkeypatch):
        """Test handling of permission errors"""
        import platform

        if platform.system() == "Windows":
            pytest.skip("Permission test not applicable on Windows")

        config_file = tmp_path / "config.json"
        config_file.write_text("{}")
        config_file.chmod(0o000)  # Remove all permissions

        monkeypatch.setattr("gaudit.config.CONFIG_FILE", config_file)

        try:
            # Should handle permission error gracefully
            with pytest.raises(PermissionError):
                load_config()
        finally:
            # Restore permissions for cleanup
            config_file.chmod(0o644)

    def test_config_unicode_handling(self, tmp_path, monkeypatch):
        """Test config with unicode characters"""
        config_file = tmp_path / "config.json"
        monkeypatch.setattr("gaudit.config.CONFIG_FILE", config_file)

        # Save config with unicode
        unicode_config = Config(
            email="user@例え.jp",
            token="token-with-émojis-🔐",
            url="https://api.test.com/v2"
        )
        with patch("gaudit.config.get_config_dir") as gcd:
            gcd.return_value = tmp_path
            save_config(unicode_config)

        # Load and verify
        loaded = load_config()
        assert loaded.email == "user@例え.jp"
        assert loaded.token == "token-with-émojis-🔐"


class TestCLIEdgeCases:
    """Test CLI edge cases"""

    @patch("gaudit.cli.GlimpsAuditClient")
    def test_cli_with_very_long_input(self, mock_client_class, cli_runner):
        """Test CLI with very long input"""
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        # Very long comment
        long_comment = "A" * 10000

        mock_instance.token = "test-token"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.create_audit.return_value = {
            "status": True,
            "aids": ["audit-123"],
            "ids": ["file-123"]
        }

        result = cli_runner.invoke(gcli, [
            "audit", "create",
            "--group", "test",
            "--file", "file-123:test.exe",
            "--comment", long_comment
        ])

        # Should handle long input without issues
        assert result.exit_code == 0

    @patch("gaudit.cli.GlimpsAuditClient")
    def test_cli_keyboard_interrupt(self, mock_client_class, cli_runner):
        """Test CLI handles keyboard interrupt"""
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        # Simulate Ctrl+C during password input
        mock_instance.login.side_effect = KeyboardInterrupt()

        result = cli_runner.invoke(gcli, ["login", "--email", "test@example.com", "--password", "pass"])

        # Should exit gracefully
        assert result.exit_code != 0

    @patch("gaudit.cli.GlimpsAuditClient")
    def test_cli_with_invalid_json_output(self, mock_client_class, cli_runner, temp_config_file, monkeypatch):
        """Test CLI --json flag with non-JSON serializable data"""
        monkeypatch.setattr("gaudit.config.CONFIG_FILE", temp_config_file)
        temp_config_file.write_text(json.dumps({"token": "test-token"}))

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token"
        mock_instance.ensure_authenticated.return_value = None

        # Return object with datetime (not JSON serializable by default)
        mock_instance.list_audits.return_value = {
            "audits": [{
                "id": "audit-123",
                "created_at": datetime.now()  # This will cause JSON serialization to fail
            }],
            "count": 1
        }

        result = cli_runner.invoke(gcli, ["audit", "list", "--json"])

        # Should handle the error gracefully
        assert result.exit_code == 1
