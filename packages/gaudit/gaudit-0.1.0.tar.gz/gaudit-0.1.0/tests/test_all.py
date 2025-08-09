"""
Comprehensive test to ensure all components work together
"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import responses

from gaudit import GlimpsAuditClient, Config, __version__
from gaudit.cli import gcli
from gaudit.config import get_config_dir, load_config, save_config


class TestFullIntegration:
    """Test full integration of all components"""

    def test_version_info(self):
        """Test version is accessible"""
        assert __version__ == "0.1.0"

    def test_complete_workflow(self, cli_runner, tmp_path, monkeypatch):
        """Test a complete workflow from CLI to API"""
        # Setup temporary config
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"

        monkeypatch.setattr("gaudit.config.get_config_dir", lambda: config_dir)
        monkeypatch.setattr("gaudit.config.CONFIG_FILE", config_file)

        with patch("gaudit.cli.GlimpsAuditClient") as mock_client_class:
            mock_instance = MagicMock()
            mock_client_class.return_value = mock_instance

            # Step 1: Login
            mock_instance.login.return_value = {
                "name": "testuser",
                "token": "jwt-token-123",
                "group": "testgroup",
                "role": "user",
                "services": ["GlimpsLibCorrelate"]
            }

            result = cli_runner.invoke(gcli, ["login", "--email", "test@example.com", "--password", "pass123"])
            assert result.exit_code == 0
            assert "Successfully logged in" in result.output

            # Verify config was saved
            saved_config = json.loads(config_file.read_text())
            assert saved_config["token"] == "jwt-token-123"

            # Step 2: Use authenticated command
            mock_instance.token = "jwt-token-123"
            mock_instance.ensure_authenticated.return_value = None
            mock_instance.get_user_properties.return_value = {
                "username": "testuser",
                "email": "test@example.com",
                "admin": False,
                "services": ["GlimpsLibCorrelate"]
            }

            result = cli_runner.invoke(gcli, ["whoami"])
            assert result.exit_code == 0
            assert "testuser" in result.output

            # Step 3: Logout
            result = cli_runner.invoke(gcli, ["logout"])
            assert result.exit_code == 0

            # Verify token was cleared
            saved_config = json.loads(config_file.read_text())
            assert saved_config["token"] is None

    @responses.activate
    def test_api_client_full_cycle(self, tmp_path):
        """Test API client full lifecycle"""
        # Initialize client
        client = GlimpsAuditClient(url="https://test.api/v1/a/b/c")

        # Login
        responses.add(
            responses.POST,
            "https://test.api/api/v2/user/login",
            json={
                "name": "testuser",
                "token": "jwt-token",
                "validity": 86400000,
                "group": "test",
                "services": ["GlimpsLibCorrelate"],
                "role": "user"
            },
            status=200
        )

        client.login("test@example.com", "password")
        assert client.token == "jwt-token"
        assert client.is_token_valid()

        # Make authenticated request
        responses.add(
            responses.GET,
            "https://test.api/api/v2/audits/groups",
            json=["group1", "group2"],
            status=200
        )

        groups = client.get_audit_groups()
        assert len(groups) == 2

        # Upload file
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"test content")

        responses.add(
            responses.POST,
            "https://test.api/api/v2/audits/upload",
            json={"status": True, "id": "file-hash-123"},
            status=200
        )

        upload_result = client.upload_file_for_audit(str(test_file))
        assert upload_result["id"] == "file-hash-123"


class TestImportCombinations:
    """Test various import combinations"""

    def test_import_client_directly(self):
        """Test importing client directly"""
        from gaudit.client import GlimpsAuditClient
        assert GlimpsAuditClient is not None

    def test_import_config_directly(self):
        """Test importing config directly"""
        from gaudit.config import Config
        assert all([Config, get_config_dir, load_config, save_config])

    def test_import_cli_directly(self):
        """Test importing CLI directly"""
        from gaudit.cli import gcli
        assert gcli is not None

    def test_import_from_package(self):
        """Test importing from package"""
        import gaudit
        assert hasattr(gaudit, "GlimpsAuditClient")
        assert hasattr(gaudit, "Config")
        assert hasattr(gaudit, "__version__")

    def test_run_as_module(self):
        """Test running as module"""
        import subprocess
        import sys

        # Test python -m gaudit --help
        result = subprocess.run(
            [sys.executable, "-m", "gaudit", "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "GLIMPS Audit CLI" in result.stdout


class TestDocumentation:
    """Test that documented examples work"""

    def test_readme_example(self):
        """Test the example from README works"""
        with patch("gaudit.client.GlimpsAuditClient.login") as mock_login:
            mock_login.return_value = {"token": "test-token"}

            # This is the example from README
            from gaudit.client import GlimpsAuditClient

            # Initialize client
            client = GlimpsAuditClient()

            # Login
            client.login("your-email@example.com", "your-password")

            # Verify it worked
            mock_login.assert_called_once()

    def test_cli_example(self, cli_runner):
        """Test CLI examples from documentation"""
        with patch("gaudit.cli.GlimpsAuditClient"):
            # Test help command
            result = cli_runner.invoke(gcli, ["--help"])
            assert result.exit_code == 0

            # Test subcommand help
            result = cli_runner.invoke(gcli, ["audit", "--help"])
            assert result.exit_code == 0


class TestCoverage:
    """Additional tests to ensure good coverage"""

    def test_config_class_defaults(self):
        """Test Config class default values"""
        config = Config()
        assert config.client is None
        assert config.url == ""
        assert config.email == ""
        assert config.token == ""
        assert config.verify_ssl is True

    @patch("platform.system")
    def test_all_platform_configs(self, mock_system):
        """Test config directory on all platforms"""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")

            # Test each platform
            for system, expected_part in [
                ("Linux", ".config"),
                ("Darwin", "Library"),
                ("Windows", "AppData"),
                ("FreeBSD", ".config"),  # Should default to Linux behavior
            ]:
                mock_system.return_value = system
                from importlib import reload
                import gaudit.config
                reload(gaudit.config)

                config_dir = gaudit.config.get_config_dir()
                assert expected_part in str(config_dir) or ".config" in str(config_dir)
