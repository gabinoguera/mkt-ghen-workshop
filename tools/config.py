"""Shared configuration for af_seo CLI tools.

Reads .env from workspace root and exposes WordPress credentials.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from workspace root (two levels up from tools/)
_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_WORKSPACE_ROOT / ".env")

# WordPress configuration
WP_BASE_URL = os.getenv("WORDPRESS_BASE_URL", "https://archivofinal.com").rstrip("/")
WP_USERNAME = os.getenv("WORDPRESS_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WORDPRESS_APP_CREDENTIALS", "")
WP_API_URL = f"{WP_BASE_URL}/wp-json/wp/v2"


def get_wp_auth():
    """Return (username, app_password) tuple for requests Basic Auth.

    Exits with JSON error to stderr if credentials are missing.
    """
    if not WP_USERNAME or not WP_APP_PASSWORD:
        error = {
            "error": "missing_credentials",
            "message": "WORDPRESS_USERNAME and WORDPRESS_APP_CREDENTIALS must be set in .env",
            "env_file": str(_WORKSPACE_ROOT / ".env"),
        }
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    return (WP_USERNAME, WP_APP_PASSWORD)


def workspace_root():
    """Return the workspace root path."""
    return _WORKSPACE_ROOT
