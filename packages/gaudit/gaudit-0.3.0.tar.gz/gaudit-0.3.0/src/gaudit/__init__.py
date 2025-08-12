"""
GLIMPS Audit Client Library

A Python client library for interacting with the GLIMPS Audit API.
"""

from .client import GlimpsAuditClient
from .cli import gcli
from .config import Config

__version__ = "0.3.0"
__all__ = ["GlimpsAuditClient", "gcli", "Config"]
