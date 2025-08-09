"""
Test module imports to ensure everything is importable
"""



def test_gaudit_imports():
    """Test that main gaudit module can be imported"""
    import gaudit
    assert hasattr(gaudit, "GlimpsAuditClient")
    assert hasattr(gaudit, "Config")
    assert hasattr(gaudit, "__version__")


def test_client_imports():
    """Test that client module can be imported"""
    from gaudit.client import GlimpsAuditClient
    assert GlimpsAuditClient is not None


def test_config_imports():
    """Test that config module can be imported"""
    from gaudit.config import Config, get_config_dir, load_config, save_config, CONFIG_FILE
    assert Config is not None
    assert get_config_dir is not None
    assert load_config is not None
    assert save_config is not None
    assert CONFIG_FILE is not None


def test_cli_imports():
    """Test that CLI module can be imported"""
    from gaudit.cli import gcli
    assert gcli is not None


def test_cli_runs():
    """Test that CLI can be invoked without errors"""
    from click.testing import CliRunner
    from gaudit.cli import gcli

    runner = CliRunner()
    result = runner.invoke(gcli, ["--help"])
    assert result.exit_code == 0
    assert "GLIMPS Audit CLI" in result.output
