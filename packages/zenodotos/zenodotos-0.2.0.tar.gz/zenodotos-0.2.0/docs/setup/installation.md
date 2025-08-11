# Installation Guide

This guide will help you install and set up Zenodotos.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Google Cloud Platform account with Drive API enabled

## Installation Steps

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install Zenodotos:
   ```bash
   pip install -e ".[dev]"
   ```

3. Set up Google Drive API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials
   - Download the credentials JSON file

4. Configure Zenodotos:
- Place the credentials file in `~/.config/zenodotos/credentials.json`
- Run `zenodotos list-files` to authenticate with Google Drive

## Verifying Installation

To verify your installation, run:
```bash
zenodotos --version
```

You should see the current version of Zenodotos displayed.
