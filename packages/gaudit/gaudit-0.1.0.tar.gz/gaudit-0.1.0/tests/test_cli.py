"""
Unit tests for the GLIMPS Audit CLI
"""

import pytest
import json
from pathlib import Path
from unittest.mock import PropertyMock, patch, MagicMock
from click.testing import CliRunner
from gaudit.config import Config, get_config_dir
from gaudit.cli import gcli
from types import SimpleNamespace


@pytest.fixture
def runner():
    """Create a CLI runner"""
    return CliRunner()


@pytest.fixture
def mock_client():
    """Create a mock client"""
    client = MagicMock()
    client.base_url = "https://test.api/v2"
    client.verify_ssl = True
    return client


DefaultConfig = SimpleNamespace(**{
    "token": "jwt-token-123",
    "url": "https://test.api/v2",
    "email": "test@example.com",
    "verify_ssl": True,
    "client": MagicMock()
})


class TestConfigManagement:
    """Test configuration management"""

    def test_get_config_dir_linux(self, monkeypatch):
        """Test config directory on Linux"""
        monkeypatch.setattr("platform.system", lambda: "Linux")
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")
            config_dir = get_config_dir()
            config_path_str = str(config_dir).replace("\\", "/")
            assert "/.config/gaudit" in config_path_str

    def test_get_config_dir_macos(self, monkeypatch):
        """Test config directory on macOS"""
        monkeypatch.setattr("platform.system", lambda: "Darwin")
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/Users/user")
            config_dir = get_config_dir()
            config_path_str = str(config_dir).replace("\\", "/")
            assert "Library/Application Support/gaudit" in config_path_str

    def test_get_config_dir_windows(self, monkeypatch):
        """Test config directory on Windows"""
        monkeypatch.setattr("platform.system", lambda: "Windows")
        with patch("pathlib.Path.home") as mock_home:
            # Use forward slashes for consistency
            mock_home.return_value = Path("C:/Users/user")
            config_dir = get_config_dir()
            # Check components instead of full path
            config_path_str = str(config_dir).replace("\\", "/")
            assert "AppData" in config_path_str
            assert "Roaming" in config_path_str
            assert "gaudit" in config_path_str


class TestAuthenticationCommands:
    """Test authentication CLI commands"""

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    @patch("gaudit.cli.save_config")
    def test_login_success(self, mock_save_config, mock_load_config, mock_client_class, runner):
        """Test successful login"""
        # Mock initial config (empty or minimal)
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        type(mock_client_class.return_value).base_url = PropertyMock()

        mock_instance.login.return_value = {
            "name": "testuser",
            "token": "jwt-token-123",
            "group": "testgroup",
            "role": "user",
            "services": ["GlimpsLibCorrelate"]
        }

        result = runner.invoke(gcli, ["login", "--email", "test@example.com", "--password", "password123"])
        assert result.exit_code == 0
        assert "Successfully logged in as testuser" in result.output
        assert "Group: testgroup" in result.output

        # Check that save_config was called with the right data
        mock_save_config.assert_called_once()
        saved_config = mock_save_config.call_args[0][0]
        assert saved_config.email == "test@example.com"
        assert saved_config.token == "jwt-token-123"

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_login_failure(self, mock_load_config, mock_client_class, runner):
        """Test failed login"""
        # Mock initial config
        mock_load_config.return_value = Config()

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.login.side_effect = Exception("Invalid credentials")

        result = runner.invoke(gcli, ["login", "--email", "test@example.com", "--password", "wrong"])

        assert result.exit_code == 1
        assert "Login failed: Invalid credentials" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    @patch("gaudit.cli.save_config")
    def test_logout(self, mock_save_config, mock_load_config, mock_client_class, runner):
        """Test logout command"""
        # Mock existing config with credentials
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        result = runner.invoke(gcli, ["logout"])

        assert result.exit_code == 0, f"error logout, stderr: {result.stderr.strip()}, stdout: {result.stdout.strip()}"
        assert "Logged out successfully" in result.output

        # Check that save_config was called with cleared credentials
        mock_save_config.assert_called_once()
        saved_config = mock_save_config.call_args[0][0]
        assert saved_config.token is None
        assert saved_config.email is None

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_whoami(self, mock_load_config, mock_client_class, runner):
        """Test whoami command"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.get_user_properties.return_value = {
            "username": "testuser",
            "email": "test@example.com",
            "admin": False,
            "services": ["GlimpsLibCorrelate", "Extract"]
        }

        result = runner.invoke(gcli, ["whoami"])

        assert result.exit_code == 0
        assert "Username: testuser" in result.output
        assert "Email: test@example.com" in result.output
        assert "Admin: False" in result.output
        assert "Services: GlimpsLibCorrelate, Extract" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    @patch("gaudit.config.save_config")
    def test_change_password(self, mock_save_config, mock_load_config, mock_client_class, runner):
        """Test change password command"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.change_password.return_value = {"status": True}

        result = runner.invoke(
            gcli,
            ["change-password"],
            input="oldpass\nnewpass\nnewpass\n"
        )

        assert result.exit_code == 0
        assert "Password changed successfully" in result.output


class TestUserCommands:
    """Test user management commands"""

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_user_stats(self, mock_load_config, mock_client_class, runner):
        """Test user stats command"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.get_user_analyses.return_value = {
            "analyses": 5,
            "disk_usage": 1024000,
            "analysis_duration": 30000,
            "delete_old": False,
            "duration": 365
        }

        result = runner.invoke(gcli, ["user", "stats"])

        assert result.exit_code == 0
        assert "Analyses count: 5" in result.output
        assert "Disk usage: 1024000 bytes" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_delete_user_analyses(self, mock_load_config, mock_client_class, runner):
        """Test delete user analyses command"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.delete_user_analyses.return_value = {"status": True}

        result = runner.invoke(gcli, ["user", "delete-analyses"], input="y\n")

        assert result.exit_code == 0
        assert "All user analyses deleted successfully" in result.output


class TestAuditCommands:
    """Test audit management commands"""

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    @patch("gaudit.config.save_config")
    def test_upload_file(self, mock_save_config, mock_load_config, mock_client_class, runner, tmp_path):
        """Test file upload command"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        DefaultConfig.client = mock_instance
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.upload_file_for_audit.return_value = {
            "status": True,
            "id": "sha256-hash-123"
        }

        # Create test file
        test_file = tmp_path / "test.exe"
        test_file.write_bytes(b"test content")

        result = runner.invoke(gcli, ["audit", "upload", str(test_file)])

        assert result.exit_code == 0, f"result: {result.stdout.strip()} err: {result.stderr.strip()}"
        assert "File uploaded successfully" in result.output
        assert "File ID: sha256-hash-123" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_create_audit_with_upload(self, mock_load_config, mock_client_class, runner, tmp_path):
        """Test creating audit with file upload"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.upload_file_for_audit.return_value = {
            "status": True,
            "id": "file-id-123"
        }
        mock_instance.create_audit.return_value = {
            "status": True,
            "aids": ["audit-id-456"],
            "ids": ["file-id-123"]
        }

        # Create test file
        test_file = tmp_path / "test.exe"
        test_file.write_bytes(b"test content")

        result = runner.invoke(gcli, [
            "audit", "create",
            "--group", "testgroup",
            "--file", str(test_file),
            "--comment", "Test audit"
        ])

        assert result.exit_code == 0
        assert "Uploading" in result.output
        assert "Audit created successfully" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_list_audits(self, mock_load_config, mock_client_class, runner):
        """Test listing audits"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.list_audits.return_value = {
            "count": 2,
            "audits": [{
                "id": "audit-id-123",
                "filename": "test.exe",
                "group": "testgroup",
                "done": True,
                "created_at": "2023-01-01T00:00:00Z",
                "comment": "Test audit"
            }]
        }

        result = runner.invoke(gcli, ["audit", "list"])

        assert result.exit_code == 0
        assert "Total audits: 2" in result.output
        assert "audit-id-123" in result.output
        assert "test.exe" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_list_audits_json(self, mock_load_config, mock_client_class, runner):
        """Test listing audits with JSON output"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.list_audits.return_value = {
            "count": 1,
            "audits": [{"id": "audit-id-123"}]
        }

        result = runner.invoke(gcli, ["audit", "list", "--json"])

        assert result.exit_code == 0
        output_json = json.loads(result.output)
        assert output_json["count"] == 1

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_get_audit(self, mock_load_config, mock_client_class, runner):
        """Test getting audit details"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.get_audit.return_value = {
            "audit": {
                "id": "audit-id-123",
                "filename": "test.exe",
                "filetype": "PE",
                "arch": "amd64",
                "size": 1024,
                "group": "testgroup",
                "comment": "Test",
                "created_at": "2023-01-01T00:00:00Z",
                "libraries": [{
                    "name": "msvcrt",
                    "desc": "Microsoft C Runtime",
                    "files": {
                        "msvcrt.dll": [{
                            "version": "7.0",
                            "score": 95.5
                        }]
                    }
                }]
            }
        }

        result = runner.invoke(gcli, ["audit", "get", "audit-id-123"])

        assert result.exit_code == 0
        assert "Audit ID: audit-id-123" in result.output
        assert "Libraries found:" in result.output
        assert "msvcrt" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_audit_groups(self, mock_load_config, mock_client_class, runner):
        """Test listing audit groups"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.get_audit_groups.return_value = ["group1", "group2", "group3"]

        result = runner.invoke(gcli, ["audit", "groups"])

        assert result.exit_code == 0
        assert "Audit groups:" in result.output
        assert "- group1" in result.output
        assert "- group2" in result.output


class TestLibraryCommands:
    """Test library commands"""

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_list_libraries(self, mock_load_config, mock_client_class, runner):
        """Test listing libraries"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.list_libraries.return_value = {
            "count": 100,
            "libraries": [{
                "project_name": "Microsoft",
                "binary_name": "kernel32.dll",
                "version": "10.0.0",
                "architecture": "amd64",
                "sha256": "hash123",
                "license": "Proprietary"
            }]
        }

        result = runner.invoke(gcli, ["library", "list"])

        assert result.exit_code == 0
        assert "Total libraries: 100" in result.output
        assert "Project: Microsoft" in result.output
        assert "kernel32.dll" in result.output


class TestDatasetCommands:
    """Test dataset commands"""

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_list_datasets(self, mock_load_config, mock_client_class, runner):
        """Test listing datasets"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.list_datasets.return_value = {
            "count": 2,
            "datasets": [{
                "name": "test_dataset",
                "group": "testgroup",
                "comment": "Test dataset",
                "kind": "udb:testgroup:hash123",
                "status": "active"
            }]
        }

        result = runner.invoke(gcli, ["dataset", "list"])

        assert result.exit_code == 0
        assert "Total datasets: 2" in result.output
        assert "Name: test_dataset" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_create_dataset(self, mock_load_config, mock_client_class, runner):
        """Test creating dataset"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.create_dataset.return_value = {
            "status": True,
            "kind": "udb:testgroup:newhash"
        }

        result = runner.invoke(gcli, ["dataset", "create", "new_dataset", "--comment", "New test dataset"])

        assert result.exit_code == 0
        assert "Dataset created successfully" in result.output
        assert "Dataset ID: udb:testgroup:newhash" in result.output


class TestErrorHandling:
    """Test error handling in CLI"""

    @patch("gaudit.cli.load_config")
    def test_not_authenticated(self, mock_load_config, runner):
        """Test command when not authenticated"""
        # Mock empty config (no token)
        mock_load_config.return_value = Config()

        result = runner.invoke(gcli, ["audit", "list"])

        assert result.exit_code == 1
        assert "Not authenticated" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_command_failure(self, mock_load_config, mock_client_class, runner):
        """Test handling of command failures"""
        # Mock config loading
        mock_load_config.return_value = DefaultConfig

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        mock_instance.token = "jwt-token-123"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.list_audits.side_effect = Exception("API Error")

        result = runner.invoke(gcli, ["audit", "list"])

        assert result.exit_code == 1
        assert "Error: API Error" in result.output


class TestCliOptions:
    """Test CLI global options"""

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    @patch("gaudit.cli.save_config")
    def test_base_url_option(self, mock_save_config, mock_load_config, mock_client_class, runner):
        """Test --url option"""
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_load_config.return_value = DefaultConfig

        result = runner.invoke(gcli, ["--url", "https://custom.api.tld/v2", "logout"])

        assert result.exit_code == 0

        # Check that client was initialized with custom URL
        mock_client_class.assert_called_with(url="https://custom.api.tld/v2", verify_ssl=True)

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    @patch("gaudit.cli.save_config")
    def test_insecure_option(self, mock_save_config, mock_load_config, mock_client_class, runner):
        """Test --insecure option"""
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_load_config.return_value = DefaultConfig

        result = runner.invoke(gcli, ["--insecure", "logout"])
        assert result.exit_code == 0

        # Check that client was initialized with verify_ssl=False
        mock_client_class.assert_called_with(url="https://test.api/v2", verify_ssl=False)
