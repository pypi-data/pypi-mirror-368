"""
Unit tests for dataset CLI commands
Add this to tests/test_cli.py or create as tests/test_cli_dataset.py
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from gaudit.cli import gcli
from gaudit.config import Config


@pytest.fixture
def runner():
    """Create a CLI runner"""
    return CliRunner()


@pytest.fixture
def mock_config():
    """Create a mock config with authenticated client"""
    config = Config()
    config.token = "test-token-123"
    config.email = "test@example.com"
    config.url = "https://test.api/v2"
    config.verify_ssl = True
    return config


class TestDatasetUploadCommand:
    """Test dataset upload command"""

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_dataset_upload_success(self, mock_load_config, mock_client_class, runner, mock_config, tmp_path):
        """Test successful file upload for dataset"""
        # Setup
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        # Create test file
        test_file = tmp_path / "library.dll"
        test_file.write_bytes(b"test library content")

        # Mock upload response
        mock_instance.upload_file_for_dataset.return_value = {
            "status": True,
            "id": "6cbce50e71d810cdf1342379b8fdbf16411d0aa25ff53f9a9568bae8bbc24ee8"
        }

        # Execute
        result = runner.invoke(gcli, ["dataset", "upload", str(test_file)])

        # Assert
        assert result.exit_code == 0
        assert "File uploaded successfully" in result.output
        assert "File ID: 6cbce50e71d810cdf1342379b8fdbf16411d0aa25ff53f9a9568bae8bbc24ee8" in result.output
        assert "Use this ID with 'dataset add-files' command" in result.output
        mock_instance.upload_file_for_dataset.assert_called_once_with(str(test_file))

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_dataset_upload_file_not_found(self, mock_load_config, mock_client_class, runner, mock_config):
        """Test upload with non-existent file"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance

        result = runner.invoke(gcli, ["dataset", "upload", "/non/existent/file.dll"])

        assert result.exit_code == 2  # Click error for missing file
        assert "does not exist" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_dataset_upload_api_error(self, mock_load_config, mock_client_class, runner, mock_config, tmp_path):
        """Test upload with API error"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        test_file = tmp_path / "library.dll"
        test_file.write_bytes(b"test content")

        mock_instance.upload_file_for_dataset.side_effect = Exception("File too large")

        result = runner.invoke(gcli, ["dataset", "upload", str(test_file)])

        assert result.exit_code == 1
        assert "Error: File too large" in result.output


class TestDatasetAddFilesCommand:
    """Test dataset add-files command"""

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_with_ids(self, mock_load_config, mock_client_class, runner, mock_config):
        """Test adding files using pre-uploaded IDs"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        # Mock successful addition
        mock_instance.add_dataset_entries.return_value = {
            "status": True,
            "files": [
                {"id": "file_id_1", "status": True},
                {"id": "file_id_2", "status": True}
            ]
        }

        result = runner.invoke(gcli, [
            "dataset", "add-files", "my_dataset",
            "--project", "TestProject",
            "--file", "abcd1234" + "0" * 56 + "@lib1.dll@1.0.0",
            "--file", "efgh5678" + "0" * 56 + "@lib2.dll@2.0.0",
            "--license", "MIT",
            "--source", "Internal"
        ])

        assert result.exit_code == 0
        assert "Adding 2 file(s) to dataset 'my_dataset'" in result.output
        assert "Files added successfully!" in result.output
        assert "✓" in result.output

        # Verify API call
        mock_instance.add_dataset_entries.assert_called_once()
        call_args = mock_instance.add_dataset_entries.call_args
        assert call_args[1]["dataset_name"] == "my_dataset"
        assert call_args[1]["project_name"] == "TestProject"
        assert len(call_args[1]["files"]) == 2
        assert call_args[1]["license"] == "MIT"
        assert call_args[1]["source_name"] == "Internal"

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_with_auto_upload(self, mock_load_config, mock_client_class, runner, mock_config, tmp_path):
        """Test adding files with auto-upload from local paths"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        # Create test files
        file1 = tmp_path / "lib1.dll"
        file1.write_bytes(b"content1")
        file2 = tmp_path / "lib2.so"
        file2.write_bytes(b"content2")

        # Mock upload responses
        upload_returns = [
            {"id": "uploaded_id_1"},
            {"id": "uploaded_id_2"}
        ]
        mock_instance.upload_file_for_dataset.side_effect = upload_returns

        # Mock add entries response
        mock_instance.add_dataset_entries.return_value = {
            "status": True,
            "files": [
                {"id": "uploaded_id_1", "status": True},
                {"id": "uploaded_id_2", "status": True}
            ]
        }

        result = runner.invoke(gcli, [
            "dataset", "add-files", "my_dataset",
            "--project", "AutoUploadTest",
            "--file", f"{file1}@1.0.0",
            "--file", f"{file2}@2.1.3",
            "--auto-upload",
            "--home-page", "https://example.com",
            "--description", "Test libraries"
        ])

        assert result.exit_code == 0
        assert "uploaded_id_1" in result.output
        assert "uploaded_id_2" in result.output
        assert "Files added successfully!" in result.output

        # Verify uploads
        assert mock_instance.upload_file_for_dataset.call_count == 2

        # Verify add entries call
        call_args = mock_instance.add_dataset_entries.call_args
        assert call_args[1]["project_name"] == "AutoUploadTest"
        assert call_args[1]["home_page"] == "https://example.com"
        assert call_args[1]["project_description"] == "Test libraries"

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_mixed_mode(self, mock_load_config, mock_client_class, runner, mock_config, tmp_path):
        """Test adding files with mixed IDs and local paths"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        # Create test file for upload
        local_file = tmp_path / "local_lib.dll"
        local_file.write_bytes(b"local content")

        # Mock upload for local file
        mock_instance.upload_file_for_dataset.return_value = {"id": "uploaded_local_id"}

        # Mock add entries response
        mock_instance.add_dataset_entries.return_value = {
            "status": True,
            "files": [
                {"id": "existing_id", "status": True},
                {"id": "uploaded_local_id", "status": True}
            ]
        }

        result = runner.invoke(gcli, [
            "dataset", "add-files", "mixed_dataset",
            "--project", "MixedProject",
            "--file", "a" * 64 + "@existing.dll@1.0.0",  # Existing ID
            "--file", f"{local_file}@2.0.0",  # Local file to upload
            "--auto-upload"
        ])

        assert result.exit_code == 0, f"error add-files, {local_file}, stderr: {result.stderr.strip()}, stdout: {result.stdout.strip()}"
        assert "Files added successfully!" in result.output

        # Verify only one upload (for the local file)
        mock_instance.upload_file_for_dataset.assert_called_once_with(str(local_file))

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_missing_project(self, mock_load_config, mock_client_class, runner, mock_config):
        """Test error when project parameter is missing"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        result = runner.invoke(gcli, [
            "dataset", "add-files", "my_dataset",
            "--file", "a" * 64 + "@lib.dll@1.0.0"
        ])

        assert result.exit_code == 2  # Click error for missing required option
        assert "--project" in result.output or "Missing option" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_missing_files(self, mock_load_config, mock_client_class, runner, mock_config):
        """Test error when no files are specified"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        result = runner.invoke(gcli, [
            "dataset", "add-files", "my_dataset",
            "--project", "TestProject"
        ])

        assert result.exit_code == 2  # Click error for missing required option
        assert "--file" in result.output or "Missing option" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_api_error_project_required(self, mock_load_config, mock_client_class, runner, mock_config):
        """Test helpful error message when API returns project_name required error"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        # Simulate API error for missing project_name
        mock_instance.add_dataset_entries.side_effect = Exception(
            "Bad Request: project_name is a required field"
        )

        result = runner.invoke(gcli, [
            "dataset", "add-files", "my_dataset",
            "--project", "TestProject",
            "--file", "a" * 64 + "@lib.dll@1.0.0"
        ])

        assert result.exit_code == 1
        assert "project_name is a required field" in result.output
        assert "The --project option is REQUIRED" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_invalid_file_format(self, mock_load_config, mock_client_class, runner, mock_config):
        """Test error with invalid file format"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        result = runner.invoke(gcli, [
            "dataset", "add-files", "my_dataset",
            "--project", "TestProject",
            "--file", "invalid_id@lib.dll@1.0.0"  # ID too short
        ])

        assert result.exit_code == 1
        assert "Error:" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_local_file_not_found(self, mock_load_config, mock_client_class, runner, mock_config):
        """Test error when local file doesn't exist without auto-upload"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        result = runner.invoke(gcli, [
            "dataset", "add-files", "my_dataset",
            "--project", "TestProject",
            "--file", "/non/existent/file.dll@1.0.0"
            # Note: no --auto-upload flag
        ])

        assert result.exit_code == 1
        assert "File /non/existent/file.dll not found" in result.output
        assert "Use --auto-upload to upload local files" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_with_default_version(self, mock_load_config, mock_client_class, runner, mock_config, tmp_path):
        """Test adding file without specifying version (defaults to 1.0.0)"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        # Create test file
        test_file = tmp_path / "lib.dll"
        test_file.write_bytes(b"content")

        mock_instance.upload_file_for_dataset.return_value = {"id": "uploaded_id"}
        mock_instance.add_dataset_entries.return_value = {
            "status": True,
            "files": [{"id": "uploaded_id", "status": True}]
        }

        result = runner.invoke(gcli, [
            "dataset", "add-files", "my_dataset",
            "--project", "TestProject",
            "--file", str(test_file),  # No version specified
            "--auto-upload"
        ])

        assert result.exit_code == 0, f"error add-files, {test_file}, stderr: {result.stderr.strip()}, stdout: {result.stdout.strip()}"
        assert "Files added successfully!" in result.output

        # Verify the default version was used
        call_args = mock_instance.add_dataset_entries.call_args
        assert call_args[1]["files"][0]["version"] == "1.0.0"

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_partial_success(self, mock_load_config, mock_client_class, runner, mock_config):
        """Test when some files succeed and others fail"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        # Mock partial success response
        mock_instance.add_dataset_entries.return_value = {
            "status": True,  # Overall success
            "files": [
                {"id": "file_id_1", "status": True},
                {"id": "file_id_2", "status": False}  # This one failed
            ]
        }

        result = runner.invoke(gcli, [
            "dataset", "add-files", "my_dataset",
            "--project", "TestProject",
            "--file", "a" * 64 + "@lib1.dll@1.0.0",
            "--file", "b" * 64 + "@lib2.dll@2.0.0"
        ])

        assert result.exit_code == 0
        assert "Files added successfully!" in result.output
        assert "✓ file_id_1" in result.output
        assert "✗ file_id_2 (failed)" in result.output

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_add_files_complete_failure(self, mock_load_config, mock_client_class, runner, mock_config):
        """Test when the entire operation fails"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        # Mock failure response
        mock_instance.add_dataset_entries.return_value = {
            "status": False,
            "error": "Dataset not found"
        }

        result = runner.invoke(gcli, [
            "dataset", "add-files", "my_dataset",
            "--project", "TestProject",
            "--file", "a" * 64 + "@lib.dll@1.0.0"
        ])

        assert result.exit_code == 0  # The command itself succeeds, but reports the failure
        assert "Failed to add files to dataset" in result.output
        assert "Error: Dataset not found" in result.output


class TestDatasetAddFilesHelp:
    """Test help and documentation for add-files command"""

    def test_add_files_help(self, runner):
        """Test that help text is displayed correctly"""
        result = runner.invoke(gcli, ["dataset", "add-files", "--help"])

        assert result.exit_code == 0
        assert "Add files to a dataset" in result.output
        assert "--project" in result.output
        assert "REQUIRED" in result.output
        assert "--file" in result.output
        assert "--auto-upload" in result.output
        assert "--license" in result.output
        assert "--source" in result.output
        assert "--home-page" in result.output
        assert "--description" in result.output
        assert "Examples:" in result.output


class TestDatasetCommandsIntegration:
    """Integration tests for complete dataset workflow"""

    @patch("gaudit.cli.GlimpsAuditClient")
    @patch("gaudit.cli.load_config")
    def test_complete_dataset_workflow(self, mock_load_config, mock_client_class, runner, mock_config, tmp_path):
        """Test complete workflow: upload, then add to dataset"""
        mock_load_config.return_value = mock_config
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        mock_instance.token = "test-token-123"
        mock_instance.ensure_authenticated.return_value = None

        # Create test file
        test_file = tmp_path / "workflow_lib.dll"
        test_file.write_bytes(b"workflow content")

        # Step 1: Upload file
        mock_instance.upload_file_for_dataset.return_value = {
            "status": True,
            "id": "219a7ef7df1f06e236b097746205385a01b3d8e238a6b7d64ca1cc1713f829d8"
        }

        upload_result = runner.invoke(gcli, ["dataset", "upload", str(test_file)])
        assert upload_result.exit_code == 0
        assert "File ID: 219a7ef7df1f06e236b097746205385a01b3d8e238a6b7d64ca1cc1713f829d8" in upload_result.output

        # Step 2: Add to dataset using the ID
        mock_instance.add_dataset_entries.return_value = {
            "status": True,
            "files": [{"id": "219a7ef7df1f06e236b097746205385a01b3d8e238a6b7d64ca1cc1713f829d8", "status": True}]
        }

        add_result = runner.invoke(gcli, [
            "dataset", "add-files", "workflow_dataset",
            "--project", "WorkflowProject",
            "--file", "219a7ef7df1f06e236b097746205385a01b3d8e238a6b7d64ca1cc1713f829d8@workflow_lib.dll@3.2.1",
            "--license", "Apache-2.0"
        ])

        assert add_result.exit_code == 0, f"add-files stderr: {add_result.stderr.strip()}"
        assert "Files added successfully!" in add_result.output

        # Verify the complete flow
        mock_instance.upload_file_for_dataset.assert_called_once_with(str(test_file))
        mock_instance.add_dataset_entries.assert_called_once()

        add_call_args = mock_instance.add_dataset_entries.call_args[1]
        assert add_call_args["dataset_name"] == "workflow_dataset"
        assert add_call_args["project_name"] == "WorkflowProject"
        assert add_call_args["files"][0]["id"] == "219a7ef7df1f06e236b097746205385a01b3d8e238a6b7d64ca1cc1713f829d8"
        assert add_call_args["files"][0]["binary_name"] == "workflow_lib.dll"
        assert add_call_args["files"][0]["version"] == "3.2.1"
        assert add_call_args["license"] == "Apache-2.0"
