"""
Configuration management for GLIMPS Audit CLI
"""

import platform
import json
from pathlib import Path


__all__ = ["Config", "CONFIG_FILE", "get_config_dir", "load_config", "save_config"]


def get_config_dir():
    """Get the appropriate configuration directory based on the OS"""
    system = platform.system()

    if system == "Windows":
        # Windows: Use %APPDATA%/gaudit
        config_dir = Path.home() / "AppData" / "Roaming" / "gaudit"
    elif system == "Darwin":
        # macOS: Use ~/Library/Application Support/gaudit
        config_dir = Path.home() / "Library" / "Application Support" / "gaudit"
    else:
        # Linux and others: Use ~/.config/gaudit
        config_dir = Path.home() / ".config" / "gaudit"

    return config_dir


# Configuration file location - computed once at module import
CONFIG_FILE = get_config_dir() / "config.json"


class Config:
    """Configuration holder for the CLI"""

    def __init__(self, client=None, url="", email="", token="", verify_ssl=True):
        self.client = client
        self.url = url
        self.email = email
        self.token = token
        self.verify_ssl = verify_ssl

    def __eq__(self, value) -> bool:
        if self.url != value.url:
            return False
        if self.email != value.email:
            return False
        if self.token != value.token:
            return False
        if self.verify_ssl != value.verify_ssl:
            return False
        return True


def load_config() -> Config:
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf8") as f:
            data = json.load(f)
            return Config(
                url=data.get("url", "https://gaudit.glimps.re"),
                email=data.get("email", ""),
                token=data.get("token", ""),
                verify_ssl=data.get("verify_ssl", True)
            )
    return Config(url="https://gaudit.glimps.re", verify_ssl=True)


def save_config(config: Config):
    """Save configuration to file"""
    data = {
        "url": config.url,
        "email": config.email,
        "token": config.token,
        "verify_ssl": config.verify_ssl
    }
    if not CONFIG_FILE.exists():
        folder = get_config_dir()
        folder.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf8") as f:
        json.dump(data, f, indent=2)
