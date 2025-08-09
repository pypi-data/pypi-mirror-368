"""Tests for the navigation module."""

from unittest.mock import Mock, patch, call

from zenodotos.cli.navigation import (
    fetch_page,
    display_page,
    get_navigation_options,
    handle_user_input,
    navigate_to_previous_page,
    interactive_pagination,
)
from zenodotos.cli.pagination import PaginationState
from zenodotos import Zenodotos
from zenodotos.drive.models import DriveFile


class TestFetchPage:
    """Tests for fetch_page function."""

    def test_fetch_page_calls_client_with_correct_parameters(self):
        """Test that fetch_page calls client.list_files_with_pagination with correct parameters."""
        mock_zenodotos = Mock(spec=Zenodotos)
        expected_result = {
            "files": [{"id": "123", "name": "test.txt"}],
            "next_page_token": "token123",
        }
        mock_zenodotos.list_files_with_pagination.return_value = expected_result

        state = PaginationState(20, "query test")
        state.page_token = "current_token"
        fields = ["id", "name", "size"]

        result = fetch_page(mock_zenodotos, state, fields)

        mock_zenodotos.list_files_with_pagination.assert_called_once_with(
            page_size=20, page_token="current_token", query="query test", fields=fields
        )
        assert result == expected_result
        assert state.current_result == expected_result

    def test_fetch_page_with_no_query(self):
        """Test fetch_page when no query is provided."""
        mock_zenodotos = Mock(spec=Zenodotos)
        expected_result = {"files": [], "next_page_token": None}
        mock_zenodotos.list_files_with_pagination.return_value = expected_result

        state = PaginationState(10, None)
        fields = ["id", "name"]

        result = fetch_page(mock_zenodotos, state, fields)

        mock_zenodotos.list_files_with_pagination.assert_called_once_with(
            page_size=10, page_token=None, query=None, fields=fields
        )
        assert result == expected_result


class TestDisplayPage:
    """Tests for display_page function."""

    @patch("zenodotos.cli.navigation.click.echo")
    @patch("zenodotos.cli.navigation.click.clear")
    @patch("zenodotos.cli.navigation.format_file_list")
    def test_display_page_clears_and_shows_formatted_files(
        self, mock_format, mock_clear, mock_echo
    ):
        """Test that display_page clears screen and displays formatted file list."""
        # Setup mock data
        files = [
            DriveFile(id="123", name="test1.txt", mime_type="text/plain", size=100),
            DriveFile(id="456", name="test2.txt", mime_type="text/plain", size=200),
        ]
        result = {"files": files}
        requested_fields = ["id", "name", "size"]
        formatted_output = "ID                Name      Size\n123               test1.txt 100\n456               test2.txt 200"
        mock_format.return_value = formatted_output

        # Call function
        display_page(result, requested_fields)

        # Verify behavior
        mock_clear.assert_called_once()
        mock_format.assert_called_once_with(files, requested_fields)
        mock_echo.assert_called_once_with(formatted_output)

    @patch("zenodotos.cli.navigation.click.echo")
    @patch("zenodotos.cli.navigation.click.clear")
    @patch("zenodotos.cli.navigation.format_file_list")
    def test_display_page_with_none_requested_fields(
        self, mock_format, mock_clear, mock_echo
    ):
        """Test display_page when requested_fields is None."""
        files = [DriveFile(id="123", name="test.txt", mime_type="text/plain", size=100)]
        result = {"files": files}
        formatted_output = "Default formatted output"
        mock_format.return_value = formatted_output

        display_page(result, None)

        mock_clear.assert_called_once()
        mock_format.assert_called_once_with(files, None)
        mock_echo.assert_called_once_with(formatted_output)


class TestHandleUserInput:
    """Tests for handle_user_input function."""

    @patch("zenodotos.cli.navigation.click.echo")
    @patch("zenodotos.cli.navigation.click.getchar")
    def test_handle_user_input_quit_choice(self, mock_getchar, mock_echo):
        """Test handle_user_input when user chooses to quit."""
        mock_getchar.return_value = "q"
        state = PaginationState(10, None)
        state.current_result = {"next_page_token": "token123"}

        result = handle_user_input(state)

        assert result == "quit"
        # First page with next available shows [N]ext [Q]uit
        mock_echo.assert_called_with("\n[N]ext [Q]uit: ", nl=False)

    @patch("zenodotos.cli.navigation.click.echo")
    @patch("zenodotos.cli.navigation.click.getchar")
    def test_handle_user_input_next_choice(self, mock_getchar, mock_echo):
        """Test handle_user_input when user chooses next."""
        mock_getchar.return_value = "n"
        state = PaginationState(10, None)
        state.current_result = {"next_page_token": "token123"}

        result = handle_user_input(state)

        assert result == "next"

    @patch("zenodotos.cli.navigation.click.echo")
    @patch("zenodotos.cli.navigation.click.getchar")
    def test_handle_user_input_previous_choice(self, mock_getchar, mock_echo):
        """Test handle_user_input when user chooses previous."""
        mock_getchar.return_value = "p"
        state = PaginationState(10, None)
        state.page_number = 3
        state.current_result = {"next_page_token": "token123"}

        result = handle_user_input(state)

        assert result == "previous"

    @patch("zenodotos.cli.navigation.click.echo")
    @patch("zenodotos.cli.navigation.click.getchar")
    def test_handle_user_input_invalid_then_valid_choice(self, mock_getchar, mock_echo):
        """Test handle_user_input with invalid choice followed by valid choice."""
        # First return invalid choice, then valid choice
        mock_getchar.side_effect = ["x", "q"]
        state = PaginationState(10, None)
        state.current_result = {"next_page_token": None}

        result = handle_user_input(state)

        assert result == "quit"
        # Should show error message and prompt again
        assert mock_echo.call_count >= 3  # Initial prompt + error + retry prompt

    @patch("zenodotos.cli.navigation.click.echo")
    @patch("zenodotos.cli.navigation.click.getchar")
    def test_handle_user_input_keyboard_interrupt(self, mock_getchar, mock_echo):
        """Test handle_user_input when KeyboardInterrupt is raised."""
        mock_getchar.side_effect = KeyboardInterrupt()
        state = PaginationState(10, None)
        state.current_result = {"next_page_token": None}

        result = handle_user_input(state)

        assert result == "quit"

    @patch("zenodotos.cli.navigation.click.echo")
    @patch("zenodotos.cli.navigation.click.getchar")
    def test_handle_user_input_case_insensitive(self, mock_getchar, mock_echo):
        """Test that handle_user_input accepts uppercase letters."""
        mock_getchar.return_value = "Q"  # Uppercase Q
        state = PaginationState(10, None)
        state.current_result = {"next_page_token": None}

        result = handle_user_input(state)

        assert result == "quit"


class TestInteractivePagination:
    """Tests for interactive_pagination function."""

    @patch("zenodotos.cli.navigation.handle_user_input")
    @patch("zenodotos.cli.navigation.display_page")
    @patch("zenodotos.cli.navigation.fetch_page")
    @patch("zenodotos.cli.navigation.click.echo")
    def test_interactive_pagination_quit_immediately(
        self, mock_echo, mock_fetch, mock_display, mock_handle
    ):
        """Test interactive_pagination when user quits immediately."""
        mock_zenodotos = Mock(spec=Zenodotos)
        mock_fetch.return_value = {"files": [], "next_page_token": None}
        mock_handle.return_value = "quit"

        interactive_pagination(
            zenodotos=mock_zenodotos,
            page_size=10,
            query=None,
            all_fields=["id", "name"],
            requested_fields=["id", "name"],
        )

        # Should fetch and display once, then quit
        assert mock_fetch.call_count == 1
        assert mock_display.call_count == 1
        mock_echo.assert_called_with("\nGoodbye!")

    @patch("zenodotos.cli.navigation.handle_user_input")
    @patch("zenodotos.cli.navigation.display_page")
    @patch("zenodotos.cli.navigation.fetch_page")
    @patch("zenodotos.cli.navigation.click.echo")
    def test_interactive_pagination_next_then_quit(
        self, mock_echo, mock_fetch, mock_display, mock_handle
    ):
        """Test interactive_pagination with next navigation then quit."""
        mock_zenodotos = Mock(spec=Zenodotos)
        mock_fetch.return_value = {"files": [], "next_page_token": "token123"}
        mock_handle.side_effect = ["next", "quit"]  # Go next, then quit

        interactive_pagination(
            zenodotos=mock_zenodotos,
            page_size=10,
            query=None,
            all_fields=["id", "name"],
            requested_fields=["id", "name"],
        )

        # Should fetch and display twice (initial + after next)
        assert mock_fetch.call_count == 2
        assert mock_display.call_count == 2
        mock_echo.assert_called_with("\nGoodbye!")

    @patch("zenodotos.cli.navigation.navigate_to_previous_page")
    @patch("zenodotos.cli.navigation.handle_user_input")
    @patch("zenodotos.cli.navigation.display_page")
    @patch("zenodotos.cli.navigation.fetch_page")
    @patch("zenodotos.cli.navigation.click.echo")
    def test_interactive_pagination_previous_then_quit(
        self, mock_echo, mock_fetch, mock_display, mock_handle, mock_navigate
    ):
        """Test interactive_pagination with previous navigation then quit."""
        mock_zenodotos = Mock(spec=Zenodotos)
        mock_fetch.return_value = {"files": [], "next_page_token": None}
        mock_handle.side_effect = ["previous", "quit"]  # Go previous, then quit

        interactive_pagination(
            zenodotos=mock_zenodotos,
            page_size=10,
            query="test query",
            all_fields=["id", "name", "size"],
            requested_fields=["id", "name"],
        )

        # Should call navigate_to_previous_page
        mock_navigate.assert_called_once()
        # Should fetch and display twice (initial + after previous)
        assert mock_fetch.call_count == 2
        assert mock_display.call_count == 2

    @patch("zenodotos.cli.navigation.handle_user_input")
    @patch("zenodotos.cli.navigation.display_page")
    @patch("zenodotos.cli.navigation.fetch_page")
    @patch("zenodotos.cli.navigation.click.echo")
    def test_interactive_pagination_keyboard_interrupt(
        self, mock_echo, mock_fetch, mock_display, mock_handle
    ):
        """Test interactive_pagination when KeyboardInterrupt is raised."""
        mock_zenodotos = Mock(spec=Zenodotos)
        mock_fetch.side_effect = KeyboardInterrupt()

        interactive_pagination(
            zenodotos=mock_zenodotos,
            page_size=10,
            query=None,
            all_fields=["id", "name"],
            requested_fields=["id", "name"],
        )

        mock_echo.assert_called_with("\n\nGoodbye!")


class TestNavigateToPreviousPage:
    """Tests for navigate_to_previous_page function."""

    def test_navigate_to_previous_page_from_page_2(self):
        """Test navigate_to_previous_page simple case from page 2 to page 1."""
        mock_zenodotos = Mock(spec=Zenodotos)
        state = PaginationState(10, "test query")
        state.page_number = 2
        state.page_token = "current_token"
        fields = ["id", "name"]

        navigate_to_previous_page(mock_zenodotos, state, fields)

        # Should reset to first page without calling client.list_files
        assert state.page_number == 1
        assert state.page_token is None
        mock_zenodotos.list_files_with_pagination.assert_not_called()

    def test_navigate_to_previous_page_from_page_3_complex_case(self):
        """Test navigate_to_previous_page complex case from page 3+ by rebuilding path."""
        mock_zenodotos = Mock(spec=Zenodotos)
        # Mock client to return successive page tokens for path reconstruction
        mock_zenodotos.list_files_with_pagination.side_effect = [
            {"files": [], "next_page_token": "token_to_page_2"},
            {"files": [], "next_page_token": "token_to_page_3"},
        ]

        state = PaginationState(10, "test query")
        state.page_number = 4  # Navigate from page 4 to page 3
        state.page_token = "current_token_page_4"
        fields = ["id", "name", "size"]

        navigate_to_previous_page(mock_zenodotos, state, fields)

        # Should make 2 calls to rebuild path to page 3 (target_page - 1 = 3 - 1 = 2 calls)
        assert mock_zenodotos.list_files_with_pagination.call_count == 2
        # Verify calls were made correctly for path reconstruction
        expected_calls = [
            call(page_size=10, page_token=None, query="test query", fields=fields),
            call(
                page_size=10,
                page_token="token_to_page_2",
                query="test query",
                fields=fields,
            ),
        ]
        mock_zenodotos.list_files_with_pagination.assert_has_calls(expected_calls)

        # Should end up on page 3 with the correct token
        assert state.page_number == 3
        assert state.page_token == "token_to_page_3"

    def test_navigate_to_previous_page_with_early_break(self):
        """Test navigate_to_previous_page when next_page_token becomes None during reconstruction."""
        mock_zenodotos = Mock(spec=Zenodotos)
        # First call returns token, second call returns None (end of results)
        mock_zenodotos.list_files_with_pagination.side_effect = [
            {"files": [], "next_page_token": "token_to_page_2"},
            {"files": [], "next_page_token": None},  # No more pages
        ]

        state = PaginationState(10, None)
        state.page_number = 5  # Try to navigate from page 5 to page 4
        fields = ["id", "name"]

        navigate_to_previous_page(mock_zenodotos, state, fields)

        # Should make 2 calls but break early when next_page_token is None
        assert mock_zenodotos.list_files_with_pagination.call_count == 2
        assert state.page_number == 4  # Target page
        assert state.page_token is None  # Should be None due to early break


class TestGetNavigationOptions:
    """Tests for get_navigation_options function (additional coverage)."""

    def test_get_navigation_options_first_page_no_next(self):
        """Test get_navigation_options on first page with no next page."""
        state = PaginationState(10, None)
        state.current_result = {"next_page_token": None}

        options = get_navigation_options(state)

        assert options == ["[Q]uit"]

    def test_get_navigation_options_with_both_prev_and_next(self):
        """Test get_navigation_options when both previous and next are available."""
        state = PaginationState(10, None)
        state.page_number = 2
        state.current_result = {"next_page_token": "token123"}

        options = get_navigation_options(state)

        assert options == ["[P]rev", "[N]ext", "[Q]uit"]
