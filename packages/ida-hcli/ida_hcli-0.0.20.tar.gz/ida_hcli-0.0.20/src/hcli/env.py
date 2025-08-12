import os
from typing import Optional


class ENV:
    """Environment configuration mirroring the Deno version."""

    HCLI_API_KEY: Optional[str] = os.getenv("HCLI_API_KEY")
    HCLI_DEBUG: bool = os.getenv("HCLI_DEBUG", "").lower() == "true"
    HCLI_API_URL: str = os.getenv("HCLI_API_URL", "https://api.eu.hex-rays.com")
    HCLI_CLOUD_URL: str = os.getenv("HCLI_CLOUD_URL", "https://api.hcli.run")
    HCLI_PORTAL_URL: str = os.getenv("HCLI_PORTAL_URL", "https://my.hex-rays.com")
    HCLI_RELEASE_URL: str = os.getenv("HCLI_RELEASE_URL", "https://hcli.apps.hex-rays.com")

    HCLI_SUPABASE_ANON_KEY: str = os.getenv(
        "HCLI_SUPABASE_ANON_KEY",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF0aGF3ZXRjYW9zb2Zyd29vaXhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjYxNDAxNzYsImV4cCI6MjA0MTcxNjE3Nn0.cOkB4DJ-jeT2aSItfSFsk2C6wtJ2f1UfErWzsf8144o",
    )
    HCLI_SUPABASE_URL: str = os.getenv("HCLI_SUPABASE_URL", "https://auth.hex-rays.com")

    HCLI_VERSION: str = "0.1.0"  # TODO: Get from version file
    HCLI_BINARY_NAME: str = "hcli"
    HCLI_MODE: str = os.getenv("HCLI_MODE", "user")
    QUIET: bool = False


# Constants
CONFIG_API_KEY = "apiKey"
OAUTH_REDIRECT_URL = "http://localhost:9999/callback"
OAUTH_SERVER_PORT = 9999
