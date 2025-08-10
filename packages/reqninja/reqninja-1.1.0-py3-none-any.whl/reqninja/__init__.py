"""
ReqNinja: A Python package and CLI tool for API testing, automation, and debugging.

ReqNinja blends the simplicity of curl with the power and flexibility of Python's requests.
"""

from .client import (
    get, post, put, delete, patch, head, options, request, ReqNinjaClient
)
from .config import Config
from .response import ReqNinjaResponse
from .exceptions import ReqNinjaError, ConfigError, AuthenticationError

__all__ = [
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "head",
    "options",
    "request",
    "ReqNinjaClient",
    "Config",
    "ReqNinjaResponse",
    "ReqNinjaError",
    "ConfigError",
    "AuthenticationError",
]

# Version will be written by setuptools_scm
try:
    from ._version import version as __version__
except ImportError:
    # Fallback if not installed via pip
    __version__ = "unknown"
