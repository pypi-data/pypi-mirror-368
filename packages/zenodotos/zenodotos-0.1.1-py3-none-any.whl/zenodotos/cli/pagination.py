"""Pagination state management for CLI commands."""

from typing import Optional, Dict, Any


class PaginationState:
    """Manages pagination state for interactive file listing."""

    def __init__(self, page_size: int, query: Optional[str]):
        self.page_size = page_size
        self.query = query
        self.page_number = 1
        self.page_token: Optional[str] = None
        self.current_result: Optional[Dict[str, Any]] = None

    def has_next_page(self) -> bool:
        """Check if there's a next page available."""
        return bool(self.current_result and self.current_result.get("next_page_token"))

    def has_previous_page(self) -> bool:
        """Check if there's a previous page available."""
        return self.page_number > 1

    def go_to_next_page(self) -> None:
        """Move to the next page."""
        if self.has_next_page():
            self.page_token = self.current_result["next_page_token"]
            self.page_number += 1

    def reset_to_first_page(self) -> None:
        """Reset to the first page."""
        self.page_token = None
        self.page_number = 1
