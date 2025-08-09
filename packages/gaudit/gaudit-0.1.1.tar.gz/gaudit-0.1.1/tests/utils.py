"""
Test utilities and helpers for GLIMPS Audit tests
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


def create_mock_audit_response(
    audit_id: str = "test-audit-123",
    filename: str = "test.exe",
    done: bool = True,
    libraries: Optional[list] = None
) -> Dict[str, Any]:
    """Create a mock audit response for testing"""
    return {
        "status": True,
        "audit": {
            "id": audit_id,
            "filename": filename,
            "filetype": "PE",
            "arch": "amd64",
            "group": "testgroup",
            "comment": "Test audit",
            "size": 1024,
            "viewed": False,
            "failed": False,
            "done": done,
            "user": "test@example.com",
            "created_at": "2023-01-01T00:00:00Z",
            "done_at": "2023-01-01T00:05:00Z" if done else "",
            "libraries": libraries or [],
            "hashes": [
                {"Name": "sha256", "Value": "abc123"},
                {"Name": "md5", "Value": "def456"}
            ]
        },
        "files": {"binary": "file-id-123"}
    }


def create_mock_library(
    name: str = "testlib",
    version: str = "1.0.0",
    score: float = 95.0
) -> Dict[str, Any]:
    """Create a mock library entry for testing"""
    return {
        "name": name,
        "desc": f"Test library {name}",
        "files": {
            f"{name}.dll": [{
                "version": version,
                "arch": "amd64",
                "score": score,
                "id": f"lib-{name}-{version}",
                "license": "MIT"
            }]
        }
    }


def create_test_binary(path: Path, size: int = 1024) -> None:
    """Create a test binary file with minimal PE/ELF header"""
    # Minimal PE header
    content = b"MZ" + b"\x00" * (size - 2)
    path.write_bytes(content)


def create_test_config(
    email: str = "test@example.com",
    token: str = "test-token-123",
    base_url: str = "https://test.api/v2"
) -> Dict[str, Any]:
    """Create a test configuration dict"""
    return {
        "email": email,
        "token": token,
        "base_url": base_url,
        "verify_ssl": True
    }


class MockResponse:
    """Mock response object for testing edge cases"""

    def __init__(self, json_data=None, text_data=None, status_code=200, headers=None):
        self.json_data = json_data
        self.text_data = text_data
        self.status_code = status_code
        self.headers = headers or {}

    def json(self):
        if self.json_data is None:
            raise json.JSONDecodeError("No JSON", "", 0)
        return self.json_data

    @property
    def text(self):
        return self.text_data or ""

    @property
    def content(self):
        return (self.text_data or "").encode()


def assert_api_error(exception, expected_status: int, expected_message: str):
    """Helper to assert API error details"""
    error_str = str(exception.value)
    assert f"API Error {expected_status}" in error_str
    assert expected_message in error_str
