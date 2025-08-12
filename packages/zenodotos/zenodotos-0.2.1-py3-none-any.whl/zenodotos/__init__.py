"""Zenodotos - Google Drive Library and CLI Tool."""

__version__ = "0.1.1"

# Main library exports
from .client import Zenodotos
from .drive.client import DriveClient
from .drive.models import DriveFile
from .auth import Auth
from .utils import FieldParser, validate_file_id, sanitize_filename, format_file_size
from .config import Config, ZenodotosConfig
from .exceptions import (
    ZenodotosError,
    AuthenticationError,
    FileNotFoundError,
    PermissionError,
    ExportError,
    ValidationError,
    ConfigurationError,
    RateLimitError,
    NetworkError,
    MultipleFilesFoundError,
    NoFilesFoundError,
)

__all__ = [
    # High-level library interface
    "Zenodotos",
    # Utility functions
    "FieldParser",
    "validate_file_id",
    "sanitize_filename",
    "format_file_size",
    # Configuration
    "Config",
    "ZenodotosConfig",
    # Core components (existing)
    "DriveClient",
    "DriveFile",
    "Auth",
    # Custom exceptions
    "ZenodotosError",
    "AuthenticationError",
    "FileNotFoundError",
    "PermissionError",
    "ExportError",
    "ValidationError",
    "ConfigurationError",
    "RateLimitError",
    "NetworkError",
    "MultipleFilesFoundError",
    "NoFilesFoundError",
    # Version
    "__version__",
]
