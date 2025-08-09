"""Google Drive API client implementation."""

from typing import List, Optional, Dict, Any
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..auth import Auth
from .models import DriveFile


class DriveClient:
    """Google Drive API client."""

    def __init__(self, credentials_path: Optional[str] = None):
        self.auth = Auth(credentials_path=credentials_path)
        self.service = None

    def get_service(self):
        """Get or create the Drive API service."""
        if not self.service:
            credentials = self.auth.get_credentials()
            self.service = build("drive", "v3", credentials=credentials)
        return self.service

    def list_files(
        self,
        page_size: int = 10,
        page_token: Optional[str] = None,
        query: Optional[str] = None,
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """List files in Google Drive.

        Args:
            page_size: Number of files to return per page.
            page_token: Token for the next page of results.
            query: Query string to filter files.
            fields: List of fields to include in the response.

        Returns:
            Dict containing:
                - files: List of DriveFile objects
                - next_page_token: Token for the next page (if any)
        """
        try:
            service = self.get_service()

            # Build the fields string
            default_fields = [
                "id",
                "name",
                "mimeType",
                "size",
                "createdTime",
                "modifiedTime",
                "description",
                "owners",
                "webViewLink",
            ]
            fields_to_request = fields or default_fields
            fields_str = f"nextPageToken, files({', '.join(fields_to_request)})"

            # Build the request
            request = service.files().list(
                pageSize=page_size,
                pageToken=page_token,
                q=query,
                fields=fields_str,
                orderBy="modifiedTime desc",
            )

            # Execute the request
            results = request.execute()

            # Convert API response to DriveFile objects
            files = [DriveFile.from_api_response(f) for f in results.get("files", [])]

            return {
                "files": files,
                "next_page_token": results.get("nextPageToken"),
            }

        except HttpError as error:
            if error.resp.status == 401:
                raise PermissionError(
                    "Authentication failed. Please check your credentials."
                ) from error
            if error.resp.status == 403:
                raise PermissionError(
                    "Insufficient permissions to access Google Drive."
                ) from error
            raise RuntimeError(f"Failed to list files: {error}") from error

    def get_file(self, file_id: str) -> DriveFile:
        """Get a specific file by ID.

        Args:
            file_id: The ID of the file to retrieve.

        Returns:
            DriveFile object representing the requested file.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            PermissionError: If the user doesn't have permission to access the file.
            RuntimeError: For other API errors.
        """
        try:
            service = self.get_service()
            file = (
                service.files()
                .get(
                    fileId=file_id,
                    fields="id,name,mimeType,size,createdTime,modifiedTime,description,owners,webViewLink",
                )
                .execute()
            )
            return DriveFile.from_api_response(file)

        except HttpError as error:
            if error.resp.status == 404:
                raise FileNotFoundError(f"File with ID {file_id} not found.") from error
            if error.resp.status in (401, 403):
                raise PermissionError(
                    "Insufficient permissions to access the file."
                ) from error
            raise RuntimeError(f"Failed to get file: {error}") from error

    def export(
        self,
        file_id: str,
        output_path: Optional[str] = None,
        format: Optional[str] = None,
    ) -> str:
        """Export a file from Google Drive.

        Currently supports Google Docs export to HTML format (ZIP file).

        Args:
            file_id: The ID of the file to export.
            output_path: Optional path where to save the file. If not provided,
                         saves to current directory with the document name.
            format: Optional export format. If not provided, uses smart defaults
                   based on file type.

        Returns:
            String path where the file was saved.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            PermissionError: If the user doesn't have permission to export the file.
            ValueError: If the specified format is not supported.
            RuntimeError: For other API errors.
        """
        try:
            service = self.get_service()

            # Validate format if provided
            if format:
                self._validate_format(format)
            else:
                # Use smart default based on file type
                format = self._get_smart_default_format(file_id)

            # Get MIME type for the format
            mime_type = self._get_mime_type_for_format(format)

            # If no output path provided, get the file name and use current directory
            if output_path is None:
                file_metadata = (
                    service.files().get(fileId=file_id, fields="name").execute()
                )
                file_name = file_metadata["name"]
                output_path = (
                    f"{file_name}.{self._get_file_extension_for_format(format)}"
                )

            # Export the document
            export_request = service.files().export(fileId=file_id, mimeType=mime_type)
            export_content = export_request.execute()

            # Save the content to file
            output_file = Path(output_path)
            output_file.write_bytes(export_content)

            return str(output_file)

        except HttpError as error:
            if error.resp.status == 404:
                raise FileNotFoundError(f"File with ID {file_id} not found.") from error
            if error.resp.status in (401, 403):
                raise PermissionError(
                    "Insufficient permissions to export the file."
                ) from error
            raise RuntimeError(f"Failed to export file: {error}") from error

    def _validate_format(self, format: str) -> None:
        """Validate that the specified format is supported.

        Args:
            format: The format to validate.

        Raises:
            ValueError: If the format is not supported.
        """
        supported_formats = ["html", "pdf", "xlsx", "csv"]
        if format not in supported_formats:
            raise ValueError(f"Unsupported format: {format}")

    def _get_smart_default_format(self, file_id: str) -> str:
        """Get the smart default format based on file type.

        Args:
            file_id: The ID of the file to check.

        Returns:
            The default format for the file type.
        """
        service = self.get_service()
        file_metadata = service.files().get(fileId=file_id, fields="mimeType").execute()
        mime_type = file_metadata["mimeType"]

        # Smart defaults based on MIME type
        format_mapping = {
            "application/vnd.google-apps.document": "html",
            "application/vnd.google-apps.spreadsheet": "xlsx",
            "application/vnd.google-apps.presentation": "pdf",
            "application/vnd.google-apps.drawing": "png",
            "application/vnd.google-apps.form": "zip",
        }

        # For non-native files, return the original format
        if mime_type not in format_mapping:
            # Extract format from MIME type (e.g., "application/pdf" -> "pdf")
            if "/" in mime_type:
                return mime_type.split("/")[-1]
            return "zip"  # Default fallback

        return format_mapping[mime_type]

    def _get_mime_type_for_format(self, format: str) -> str:
        """Get the MIME type for a given format.

        Args:
            format: The format to get MIME type for.

        Returns:
            The MIME type for the format.
        """
        mime_type_mapping = {
            "html": "application/zip",  # Google Docs HTML export is ZIP format
            "pdf": "application/pdf",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "csv": "text/csv",
        }
        return mime_type_mapping.get(format, "application/zip")

    def _get_file_extension_for_format(self, format: str) -> str:
        """Get the file extension for a given format.

        Args:
            format: The format to get extension for.

        Returns:
            The file extension for the format.
        """
        extension_mapping = {
            "html": "zip",  # HTML export comes as ZIP
            "pdf": "pdf",
            "xlsx": "xlsx",
            "csv": "csv",
        }
        return extension_mapping.get(format, "zip")
