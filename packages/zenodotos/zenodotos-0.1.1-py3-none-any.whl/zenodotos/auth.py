"""Authentication handling for Google Drive API."""

import os
import json
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .config import Config


class Auth:
    """Handle Google Drive API authentication."""

    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

    def __init__(self, credentials_path: Optional[str] = None):
        self.config = Config()
        if credentials_path:
            self.config.set("credentials_path", credentials_path)
        self.credentials = None

    def get_credentials(self):
        """Get valid credentials for Google Drive API.

        The authentication flow is:
        1. Try to load credentials from token file
        2. If token exists and is valid, use it
        3. If token exists but is expired, refresh it
        4. If no token exists, start OAuth flow using credentials file
        5. Save new token after OAuth flow
        """
        # Try to load credentials from token file
        if os.path.exists(self.config.get_token_path()):
            with open(self.config.get_token_path(), "r") as token:
                self.credentials = Credentials.from_authorized_user_info(
                    json.load(token), self.SCOPES
                )

        # If we have valid credentials, return them
        if self.credentials and self.credentials.valid:
            return self.credentials

        # If we have expired credentials with refresh token, refresh them
        if (
            self.credentials
            and self.credentials.expired
            and self.credentials.refresh_token
        ):
            self.credentials.refresh(Request())
            self._save_token()
            return self.credentials

        # If we get here, we need to start a new OAuth flow
        if not os.path.exists(self.config.get_credentials_path()):
            raise FileNotFoundError(
                f"Credentials file not found at {self.config.get_credentials_path()}. "
                "Please download it from Google Cloud Console and place it in the config directory."
            )

        self.config.ensure_config_dir()
        flow = InstalledAppFlow.from_client_secrets_file(
            self.config.get_credentials_path(), self.SCOPES
        )
        self.credentials = flow.run_local_server(port=0)
        self._save_token()
        return self.credentials

    def _save_token(self):
        """Save the current credentials to the token file."""
        if self.credentials:
            with open(self.config.get_token_path(), "w") as token:
                token.write(self.credentials.to_json())
