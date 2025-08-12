"""Navigation helper functions for interactive CLI commands."""

import click
from typing import List, Dict, Any, Optional
from zenodotos import Zenodotos
from zenodotos.formatters.display import format_file_list
from .pagination import PaginationState


def fetch_page(
    zenodotos: Zenodotos, state: PaginationState, fields: List[str]
) -> Dict[str, Any]:
    """Fetch a page of files from the API."""
    result = zenodotos.list_files_with_pagination(
        page_size=state.page_size,
        page_token=state.page_token,
        query=state.query,
        fields=fields,
    )
    state.current_result = result
    return result


def display_page(result: Dict[str, Any], requested_fields: Optional[List[str]]) -> None:
    """Display the current page of files."""
    click.clear()
    click.echo(format_file_list(result["files"], requested_fields))


def get_navigation_options(state: PaginationState) -> List[str]:
    """Get available navigation options based on current state."""
    options = []
    if state.has_previous_page():
        options.append("[P]rev")
    if state.has_next_page():
        options.append("[N]ext")
    options.append("[Q]uit")
    return options


def handle_user_input(state: PaginationState) -> str:
    """Handle user input and return the chosen action."""
    options = get_navigation_options(state)
    click.echo(f"\n{' '.join(options)}: ", nl=False)

    while True:
        try:
            choice = click.getchar().lower()
            if choice == "q":
                return "quit"
            elif choice == "n" and state.has_next_page():
                return "next"
            elif choice == "p" and state.has_previous_page():
                return "previous"
            else:
                click.echo("\nInvalid choice. Please try again.")
                click.echo(f"{' '.join(options)}: ", nl=False)
                continue
        except KeyboardInterrupt:
            return "quit"


def navigate_to_previous_page(
    zenodotos: Zenodotos, state: PaginationState, fields: List[str]
) -> None:
    """Navigate to the previous page by rebuilding the path from the beginning."""
    if state.page_number == 2:
        # Simple case: go back to first page
        state.reset_to_first_page()
    else:
        # Complex case: rebuild path to previous page
        target_page = state.page_number - 1
        state.reset_to_first_page()

        # Navigate to target page by going through all pages
        for _ in range(target_page - 1):
            temp_result = zenodotos.list_files_with_pagination(
                page_size=state.page_size,
                page_token=state.page_token,
                query=state.query,
                fields=fields,
            )
            state.page_token = temp_result.get("next_page_token")
            if not state.page_token:
                break

        state.page_number = target_page


def interactive_pagination(
    zenodotos: Zenodotos,
    page_size: int,
    query: Optional[str],
    all_fields: List[str],
    requested_fields: Optional[List[str]],
) -> None:
    """Handle interactive pagination for file listing."""
    state = PaginationState(page_size, query)

    try:
        while True:
            # Fetch and display current page
            result = fetch_page(zenodotos, state, all_fields)
            display_page(result, requested_fields)

            # Handle user navigation
            action = handle_user_input(state)

            if action == "quit":
                click.echo("\nGoodbye!")
                return
            elif action == "next":
                state.go_to_next_page()
            elif action == "previous":
                navigate_to_previous_page(zenodotos, state, all_fields)

    except KeyboardInterrupt:
        click.echo("\n\nGoodbye!")
        return
