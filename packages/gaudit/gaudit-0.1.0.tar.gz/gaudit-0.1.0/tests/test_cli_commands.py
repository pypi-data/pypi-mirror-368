"""
Test CLI commands in isolation with better organization
"""

import json
from unittest.mock import patch, MagicMock
from gaudit.cli import gcli
import gaudit.config


class TestCLICommandExecution:
    """Test that CLI commands execute properly"""

    def test_cli_help(self, cli_runner):
        """Test CLI help command"""
        result = cli_runner.invoke(gcli, ["--help"])
        assert result.exit_code == 0
        assert "GLIMPS Audit CLI" in result.output
        assert "Commands:" in result.output

    def test_audit_help(self, cli_runner):
        """Test audit subcommand help"""
        result = cli_runner.invoke(gcli, ["audit", "--help"])
        assert result.exit_code == 0
        assert "Audit management commands" in result.output

    def test_user_help(self, cli_runner):
        """Test user subcommand help"""
        result = cli_runner.invoke(gcli, ["user", "--help"])
        assert result.exit_code == 0
        assert "User management commands" in result.output

    def test_dataset_help(self, cli_runner):
        """Test dataset subcommand help"""
        result = cli_runner.invoke(gcli, ["dataset", "--help"])
        assert result.exit_code == 0
        assert "Dataset management commands" in result.output

    def test_library_help(self, cli_runner):
        """Test library subcommand help"""
        result = cli_runner.invoke(gcli, ["library", "--help"])
        assert result.exit_code == 0
        assert "Library management commands" in result.output


class TestCLIAuthentication:
    """Test CLI authentication flow"""

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.config.get_config_dir")
    def test_login_interactive(self, mock_get_config_dir, mock_client_class, cli_runner, temp_config_file, monkeypatch):
        """Test interactive login"""
        monkeypatch.setattr(gaudit.config, "CONFIG_FILE", temp_config_file)

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.login.return_value = {
            "name": "testuser",
            "token": "jwt-token-123",
            "group": "testgroup",
            "role": "user",
            "services": ["GlimpsLibCorrelate"]
        }
        mock_get_config_dir.return_value = temp_config_file.parent

        # Test interactive input
        result = cli_runner.invoke(gcli, ["login"], input="test@example.com\npassword123\n")

        assert result.exit_code == 0, f"stderr: {result.stderr.strip()}, stdout: {result.stdout.strip()}"
        assert "Successfully logged in as testuser" in result.output

        # Check config was saved
        assert temp_config_file.exists()
        saved_config = json.loads(temp_config_file.read_text())
        assert saved_config["email"] == "test@example.com"
        assert saved_config["token"] == "jwt-token-123"

    @patch("gaudit.cli.GlimpsAuditClient")
    def test_logout_clears_credentials(self, mock_client_class, cli_runner, temp_config_file, monkeypatch):
        """Test logout clears stored credentials"""
        monkeypatch.setattr(gaudit.config, "CONFIG_FILE", temp_config_file)

        # Create initial config with credentials
        initial_config = {
            "url": "https://test.api/v2",
            "email": "test@example.com",
            "token": "jwt-token-123",
            "verify_ssl": True
        }
        temp_config_file.write_text(json.dumps(initial_config))

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        result = cli_runner.invoke(gcli, ["logout"])

        assert result.exit_code == 0
        assert "Logged out successfully" in result.output

        # Check credentials were cleared
        saved_config = json.loads(temp_config_file.read_text())
        assert saved_config["token"] is None
        assert saved_config["email"] is None
        assert saved_config["url"] == "https://test.api/v2"  # Should preserve url


class TestCLIWithAuthentication:
    """Test commands that require authentication"""

    def test_command_without_auth_fails(self, cli_runner, temp_config_file, monkeypatch):
        """Test that commands fail when not authenticated"""
        monkeypatch.setattr(gaudit.config, "CONFIG_FILE", temp_config_file)

        # Empty config (no token)
        temp_config_file.write_text(json.dumps({}))

        result = cli_runner.invoke(gcli, ["audit", "list"])

        assert result.exit_code == 1
        assert "Not authenticated" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    def test_download_with_output_path(self, mock_client_class, cli_runner, temp_config_file, monkeypatch, tmp_path):
        """Test download command with custom output path"""
        monkeypatch.setattr(gaudit.config, "CONFIG_FILE", temp_config_file)

        # Setup authenticated config
        temp_config_file.write_text(json.dumps({"token": "test-token"}))

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.download_audit_binary.return_value = b"binary content"

        output_file = tmp_path / "output.bin"

        result = cli_runner.invoke(gcli, [
            "audit", "download",
            "audit-123", "file-456",
            "--output", str(output_file)
        ])

        assert result.exit_code == 0
        assert f"File downloaded to: {output_file}" in result.output
        mock_instance.download_audit_binary.assert_called_once_with("audit-123", "file-456", str(output_file))


class TestCLIDatasetCommands:
    """Test dataset-specific commands"""

    @patch("gaudit.cli.GlimpsAuditClient")
    def test_dataset_update_command(self, mock_client_class, cli_runner, temp_config_file, monkeypatch):
        """Test dataset update command"""
        monkeypatch.setattr(gaudit.config, "CONFIG_FILE", temp_config_file)

        # Setup authenticated config
        temp_config_file.write_text(json.dumps({"token": "test-token"}))

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.update_dataset.return_value = None

        result = cli_runner.invoke(gcli, ["dataset", "update", "test_dataset"])

        assert result.exit_code == 0
        assert "Dataset test_dataset update started" in result.output
        mock_instance.update_dataset.assert_called_once_with("test_dataset")


class TestCLIErrorHandling:
    """Test error handling in CLI"""

    @patch("gaudit.cli.GlimpsAuditClient")
    def test_api_error_display(self, mock_client_class, cli_runner, temp_config_file, monkeypatch):
        """Test that API errors are displayed properly"""
        monkeypatch.setattr(gaudit.config, "CONFIG_FILE", temp_config_file)

        # Setup authenticated config
        temp_config_file.write_text(json.dumps({"token": "test-token"}))

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token"
        mock_instance.ensure_authenticated.return_value = None
        mock_instance.list_audits.side_effect = Exception("API Error: Invalid request")

        result = cli_runner.invoke(gcli, ["audit", "list"])

        assert result.exit_code == 1
        assert "Error: API Error: Invalid request" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    def test_connection_error_handling(self, mock_client_class, cli_runner, temp_config_file, monkeypatch):
        """Test handling of connection errors"""
        monkeypatch.setattr(gaudit.config, "CONFIG_FILE", temp_config_file)

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.login.side_effect = Exception("Connection refused")

        result = cli_runner.invoke(gcli, ["login", "--email", "test@example.com", "--password", "pass"])

        assert result.exit_code == 1
        assert "Login failed: Connection refused" in result.output


class TestCLIOptions:
    """Test CLI global options"""

    @patch("gaudit.cli.GlimpsAuditClient")
    def test_base_url_from_env(self, mock_client_class, cli_runner, temp_config_file, monkeypatch):
        """Test base URL from environment variable"""
        monkeypatch.setenv("GLIMPS_AUDIT_URL", "https://custom.api/v3")
        monkeypatch.setattr(gaudit.config, "CONFIG_FILE", temp_config_file)

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        cli_runner.invoke(gcli, ["logout"])

        # Verify client was initialized with env var URL
        mock_client_class.assert_called_with(url="https://custom.api/v3", verify_ssl=True)

    @patch("gaudit.cli.GlimpsAuditClient")
    def test_base_url_option_overrides_env(self, mock_client_class, cli_runner, temp_config_file, monkeypatch):
        """Test that CLI option overrides environment variable"""
        monkeypatch.setenv("GLIMPS_AUDIT_URL", "https://env.api/v2")
        monkeypatch.setattr(gaudit.config, "CONFIG_FILE", temp_config_file)

        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        result = cli_runner.invoke(gcli, ["--url", "https://cli.api/v2", "logout"])

        assert result.exit_code == 0, f"logout error, stderr: {result.stderr.strip()}, stdout: {result.stdout.strip()}"

        # Verify client was initialized with CLI option URL
        mock_client_class.assert_called_with(url="https://cli.api/v2", verify_ssl=True)
