"""
Unit tests for the configuration module
"""

from unittest.mock import patch
from gaudit.config import load_config, save_config, Config


class TestConfigFunctions:
    """Test configuration functions"""

    def test_save_and_load_config(self, tmp_path, monkeypatch):
        """Test saving and loading configuration"""
        config_file = tmp_path / "config.json"
        monkeypatch.setattr("gaudit.config.CONFIG_FILE", config_file)

        # Save config
        test_data = Config(
            url="https://test.api/v2",
            email="test@example.com",
            token="test-token",
            verify_ssl=False
        )
        with patch("gaudit.config.get_config_dir") as gcd:
            gcd.return_value = tmp_path
            save_config(test_data)

        # Load config
        loaded_data = load_config()

        assert loaded_data == test_data
        assert config_file.exists()

    def test_load_config_missing_file(self, tmp_path, monkeypatch):
        """Test loading config when file doesn't exist"""
        config_file = tmp_path / "nonexistent.json"
        monkeypatch.setattr("gaudit.config.CONFIG_FILE", config_file)

        result = load_config()
        assert result == Config(url="https://gaudit.glimps.re", verify_ssl=True)

    def test_config_class(self):
        """Test Config class initialization"""
        config = Config()

        assert config.client is None
        assert config.url == ""
        assert config.email == ""
        assert config.token == ""
        assert config.verify_ssl is True
