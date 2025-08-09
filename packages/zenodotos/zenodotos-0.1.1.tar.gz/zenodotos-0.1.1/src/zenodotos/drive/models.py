"""Google Drive data models."""

from datetime import datetime
from typing import Dict, Any, List, Optional

from dateutil.parser import parse


class DriveFile:
    """Represents a Google Drive file."""

    def __init__(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        mime_type: Optional[str] = None,
        size: Optional[int] = None,
        created_time: Optional[datetime] = None,
        modified_time: Optional[datetime] = None,
        description: Optional[str] = None,
        owners: Optional[List[Dict[str, str]]] = None,
        web_view_link: Optional[str] = None,
    ):
        """Initialize a DriveFile instance.

        Args:
            id: The file's unique identifier.
            name: The file's name.
            mime_type: The file's MIME type.
            size: The file's size in bytes.
            created_time: When the file was created.
            modified_time: When the file was last modified.
            description: The file's description.
            owners: List of file owners with their details.
            web_view_link: URL to view the file in a web browser.
        """
        self.id = id
        self.name = name or "N/A"
        self.mime_type = mime_type or "N/A"
        self.size = size
        self.created_time = created_time
        self.modified_time = modified_time
        self.description = description
        self.owners = owners
        self.web_view_link = web_view_link

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "DriveFile":
        """Create a DriveFile instance from API response data.

        Args:
            data: Dictionary containing file data from the API.

        Returns:
            A new DriveFile instance.
        """
        # Convert size to integer if present
        size = int(data["size"]) if data.get("size") else None

        # Parse timestamps if present
        created_time = parse(data["createdTime"]) if data.get("createdTime") else None
        modified_time = (
            parse(data["modifiedTime"]) if data.get("modifiedTime") else None
        )

        return cls(
            id=data.get("id"),
            name=data.get("name"),
            mime_type=data.get("mimeType"),
            size=size,
            created_time=created_time,
            modified_time=modified_time,
            description=data.get("description"),
            owners=data.get("owners"),
            web_view_link=data.get("webViewLink"),
        )

    def __str__(self) -> str:
        """Return a string representation of the file."""
        return f"{self.name} ({self.mime_type})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the file."""
        attrs = []
        if self.id is not None:
            attrs.append(f"id='{self.id}'")
        if self.name is not None:
            attrs.append(f"name='{self.name}'")
        if self.mime_type is not None:
            attrs.append(f"mime_type='{self.mime_type}'")
        if self.size is not None:
            attrs.append(f"size={self.size}")
        if self.created_time is not None:
            attrs.append(f"created_time={self.created_time}")
        if self.modified_time is not None:
            attrs.append(f"modified_time={self.modified_time}")
        if self.description is not None:
            attrs.append(f"description='{self.description}'")
        if self.owners is not None:
            attrs.append(f"owners={self.owners}")
        if self.web_view_link is not None:
            attrs.append(f"web_view_link='{self.web_view_link}'")
        return f"DriveFile({', '.join(attrs)})"
