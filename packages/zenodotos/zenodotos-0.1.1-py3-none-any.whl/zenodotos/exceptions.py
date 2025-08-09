"""Custom exceptions for the Zenodotos library."""

from typing import Optional


class ZenodotosError(Exception):
    """Base exception for all Zenodotos library errors."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """Initialize the exception.

        Args:
            message: Human-readable error message
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class AuthenticationError(ZenodotosError):
    """Authentication-related errors.

    Raised when:
    - Credentials are invalid or expired
    - OAuth flow fails
    - Service account authentication fails
    """

    pass


class FileNotFoundError(ZenodotosError):
    """File not found in Google Drive.

    Raised when:
    - File ID doesn't exist
    - File has been deleted
    - File is in trash
    """

    pass


class PermissionError(ZenodotosError):
    """Permission-related errors.

    Raised when:
    - User doesn't have access to the file
    - Insufficient permissions for the operation
    - File is shared but user lacks required permissions
    """

    pass


class ExportError(ZenodotosError):
    """Export operation errors.

    Raised when:
    - Export format is not supported
    - File type cannot be exported
    - Export operation fails
    """

    pass


class ValidationError(ZenodotosError):
    """Input validation errors.

    Raised when:
    - Invalid file ID format
    - Invalid query syntax
    - Invalid field names
    - Invalid format options
    """

    pass


class ConfigurationError(ZenodotosError):
    """Configuration-related errors.

    Raised when:
    - Configuration file is invalid
    - Required configuration is missing
    - Environment variables are misconfigured
    """

    pass


class RateLimitError(ZenodotosError):
    """API rate limiting errors.

    Raised when:
    - Google Drive API quota is exceeded
    - Too many requests in a short time
    - Rate limiting is enforced
    """

    pass


class NetworkError(ZenodotosError):
    """Network-related errors.

    Raised when:
    - Network connection fails
    - Timeout occurs
    - DNS resolution fails
    """

    pass


class MultipleFilesFoundError(ZenodotosError):
    """Multiple files found when expecting single match.

    Raised when:
    - Search query returns multiple files
    - Export with query finds multiple matches
    """

    def __init__(self, message: str, files: Optional[list] = None):
        """Initialize the exception.

        Args:
            message: Human-readable error message
            files: List of files that were found
        """
        super().__init__(message)
        self.files = files or []


class NoFilesFoundError(ZenodotosError):
    """No files found when expecting at least one match.

    Raised when:
    - Search query returns no results
    - Export with query finds no matches
    """

    pass
