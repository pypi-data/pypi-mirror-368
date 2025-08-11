"""Tests for the authentication module."""

import json
from unittest.mock import patch, mock_open, MagicMock

import pytest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from zenodotos.auth import Auth


@pytest.fixture
def mock_config():
    """Create a mock config object."""
    config = MagicMock()
    config.get_credentials_path.return_value = "/path/to/credentials.json"
    config.get_token_path.return_value = "/path/to/token.json"
    config.ensure_config_dir.return_value = None
    return config


@pytest.fixture
def mock_credentials():
    """Create mock credentials."""
    creds = MagicMock(spec=Credentials)
    creds.valid = True
    creds.expired = False
    creds.refresh_token = "refresh_token"
    creds.to_json.return_value = '{"token": "test_token"}'
    return creds


@pytest.fixture
def mock_flow(mock_credentials):
    """Create a mock OAuth flow."""
    flow = MagicMock(spec=InstalledAppFlow)
    flow.run_local_server.return_value = mock_credentials
    return flow


def test_get_credentials_from_token_file(mock_config, mock_credentials):
    """Test getting credentials from existing token file."""
    token_data = {
        "token": "test_token",
        "refresh_token": "refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "scopes": ["https://www.googleapis.com/auth/drive.readonly"],
    }

    with patch("os.path.exists") as mock_exists, patch(
        "builtins.open", mock_open(read_data=json.dumps(token_data))
    ), patch("zenodotos.auth.Credentials.from_authorized_user_info") as mock_from_info:
        mock_exists.return_value = True
        mock_from_info.return_value = mock_credentials

        auth = Auth()
        auth.config = mock_config
        creds = auth.get_credentials()

        assert creds == mock_credentials
        mock_exists.assert_called_once_with("/path/to/token.json")
        mock_from_info.assert_called_once_with(token_data, auth.SCOPES)


def test_get_credentials_refresh_token(mock_config, mock_credentials):
    """Test refreshing expired credentials."""
    mock_credentials.valid = False
    mock_credentials.expired = True

    with patch("os.path.exists") as mock_exists, patch(
        "builtins.open", mock_open(read_data='{"token": "old_token"}')
    ), patch(
        "zenodotos.auth.Credentials.from_authorized_user_info"
    ) as mock_from_info, patch("zenodotos.auth.Request") as mock_request:
        mock_exists.return_value = True
        mock_from_info.return_value = mock_credentials

        auth = Auth()
        auth.config = mock_config
        creds = auth.get_credentials()

        assert creds == mock_credentials
        mock_credentials.refresh.assert_called_once_with(mock_request.return_value)


def test_get_credentials_new_oauth_flow(mock_config, mock_flow, mock_credentials):
    """Test starting new OAuth flow when no token exists."""
    with patch("os.path.exists") as mock_exists, patch(
        "zenodotos.auth.InstalledAppFlow.from_client_secrets_file"
    ) as mock_flow_class, patch("builtins.open", mock_open()):
        mock_exists.return_value = False
        mock_flow_class.return_value = mock_flow

        auth = Auth()
        auth.config = mock_config

        with pytest.raises(FileNotFoundError) as exc_info:
            auth.get_credentials()

        assert "Credentials file not found" in str(exc_info.value)


def test_get_credentials_missing_credentials_file(mock_config):
    """Test error when credentials file is missing."""
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False

        auth = Auth()
        auth.config = mock_config

        with pytest.raises(FileNotFoundError) as exc_info:
            auth.get_credentials()

        assert "Credentials file not found" in str(exc_info.value)


def test_save_token(mock_config, mock_credentials):
    """Test saving credentials to token file."""
    with patch("builtins.open", mock_open()) as mock_file:
        auth = Auth()
        auth.config = mock_config
        auth.credentials = mock_credentials
        auth._save_token()

        mock_file.assert_called_with("/path/to/token.json", "w")
        mock_file.return_value.write.assert_called_once_with('{"token": "test_token"}')
