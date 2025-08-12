import asyncio
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, Dict, Optional

from supabase import Client, create_client
from supabase.lib.client_options import SyncClientOptions

from hcli.env import CONFIG_API_KEY, ENV, OAUTH_REDIRECT_URL, OAUTH_SERVER_PORT
from hcli.lib.config import config_store

AuthType = Dict[str, Any]  # {"type": "key"|"interactive", "source": "config"|"env"}


class AuthService:
    """Singleton authentication service handling both API key and OAuth authentication."""

    _instance: Optional["AuthService"] = None

    def __init__(self):
        if AuthService._instance is not None:
            raise Exception("AuthService is a singleton. Use AuthService.instance")

        # Create custom storage class for Supabase
        class SyncSupportedStorage:
            def get_item(self, key: str) -> Optional[str]:
                return config_store.get_string(key) or None

            def set_item(self, key: str, value: str) -> None:
                config_store.set_string(key, value)

            def remove_item(self, key: str) -> None:
                config_store.remove_string(key)

        # Create Supabase client with custom storage
        options = SyncClientOptions(
            auto_refresh_token=False, persist_session=True, storage=SyncSupportedStorage(), flow_type="implicit"
        )

        self.supabase: Client = create_client(ENV.HCLI_SUPABASE_URL, ENV.HCLI_SUPABASE_ANON_KEY, options)

        self.session: Optional[Any] = None
        self.user: Optional[Any] = None
        self._server_thread: Optional[Thread] = None
        self._oauth_result: Optional[Dict[str, str]] = None

    @classmethod
    def instance(cls) -> "AuthService":
        """Get singleton instance of AuthService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def init(self) -> None:
        """Initialize the auth service and restore session."""
        try:
            user_response = self.supabase.auth.get_user()
            if user_response.user:
                self.user = user_response.user
                self.session = self.supabase.auth.get_session()
        except Exception:
            # Ignore errors during initialization - auth may not be configured
            pass

    def logout(self) -> None:
        """Log out from both API key and interactive sessions."""
        try:
            self.supabase.auth.sign_out()
            config_store.remove_string("supabase.auth.token")
        except Exception:
            # Ignore logout errors - session may already be invalid
            pass
        self.session = None
        self.user = None

    async def login(self, force: bool = False) -> bool:
        """Login using OAuth flow."""
        if force:
            self.logout()

        if not self.is_logged_in():
            await self._login_flow(force)

        return self.is_logged_in()

    def send_otp(self, email: str, force: bool = False) -> bool:
        """Send OTP to email for authentication."""
        if force:
            self.logout()

        if not self.is_logged_in():
            self.supabase.auth.sign_in_with_otp({"email": email})

        return True

    def check_otp(self, email: str, otp: str) -> bool:
        """Verify OTP token."""
        self.supabase.auth.verify_otp({"email": email, "token": otp, "type": "email"})

        # Refresh session after OTP verification
        user_response = self.supabase.auth.get_user()
        if user_response.user:
            self.user = user_response.user
            self.session = self.supabase.auth.get_session()

        return self.is_logged_in()

    def get_user(self) -> Optional[Dict[str, str]]:
        """Get current user information."""
        if self.get_api_key():
            # TODO: Call API to get user info from API key
            return {"email": "api-key-user"}  # Placeholder

        if self.session and self.session.user:
            return {"email": self.session.user.email or ""}

        return None

    def is_logged_in(self) -> bool:
        """Check if user is authenticated via any method."""
        if self.get_api_key():
            return True

        return self.session is not None and self.session.user is not None

    def get_auth_type(self) -> AuthType:
        """Get the type of authentication being used."""
        if self.get_api_key():
            if ENV.HCLI_API_KEY:
                return {"type": "key", "source": "env"}
            elif config_store.has(CONFIG_API_KEY):
                return {"type": "key", "source": "config"}

        return {"type": "interactive", "source": "config"}

    def get_api_key(self) -> Optional[str]:
        """Get API key from environment then config."""
        if ENV.HCLI_API_KEY:
            return ENV.HCLI_API_KEY
        elif config_store.has(CONFIG_API_KEY):
            return config_store.get_string(CONFIG_API_KEY)
        return None

    def set_api_key(self, key: str):
        """Set API key in config."""
        config_store.set_string(CONFIG_API_KEY, key)

    def unset_api_key(self):
        """Remove API key from config."""
        config_store.remove_string(CONFIG_API_KEY)

    def get_access_token(self) -> Optional[str]:
        """Get access token from current session."""
        return self.session.access_token if self.session else None

    async def _login_flow(self, prompt: bool = False):
        """Handle OAuth login flow with local HTTP server."""
        print(f"Starting Google OAuth login{'with prompt' if prompt else ''}...")

        # Build OAuth URL with optional prompt parameter
        query_params = {}
        if prompt:
            query_params["prompt"] = "login"

        # Start OAuth flow
        auth_response = self.supabase.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {
                    "redirect_to": OAUTH_REDIRECT_URL,
                    "query_params": query_params,
                },
            }
        )

        oauth_url = auth_response.url
        if not oauth_url:
            print("No OAuth URL received")
            return

        print(f"Open this URL in your browser to continue login: {oauth_url}")
        webbrowser.open(oauth_url)

        # Start local HTTP server to handle callback
        await self._start_oauth_server()

    async def _start_oauth_server(self):
        """Start local HTTP server to handle OAuth callback."""
        self._oauth_result = None

        class OAuthHandler(BaseHTTPRequestHandler):
            def do_GET(handler_self):
                if handler_self.path.startswith("/callback"):
                    # Serve HTML page to extract tokens from URL hash
                    handler_self.send_response(200)
                    handler_self.send_header("Content-Type", "text/html")
                    handler_self.end_headers()
                    handler_self.wfile.write(HTML_PAGE.encode())
                else:
                    handler_self.send_response(404)
                    handler_self.end_headers()

            def do_POST(handler_self):
                if handler_self.path == "/token":
                    # Handle token submission from browser
                    content_length = int(handler_self.headers["Content-Length"])
                    post_data = handler_self.rfile.read(content_length)

                    try:
                        token_data = json.loads(post_data.decode())
                        access_token = token_data.get("access_token")
                        refresh_token = token_data.get("refresh_token")

                        if access_token:
                            self._oauth_result = {
                                "access_token": access_token,
                                "refresh_token": refresh_token,
                            }

                            handler_self.send_response(200)
                            handler_self.send_header("Content-Type", "text/plain")
                            handler_self.end_headers()
                            handler_self.wfile.write(b"Token received and saved.")
                        else:
                            handler_self.send_response(400)
                            handler_self.end_headers()
                    except Exception as e:
                        print(f"Failed to process token: {e}")
                        handler_self.send_response(500)
                        handler_self.end_headers()
                else:
                    handler_self.send_response(404)
                    handler_self.end_headers()

            def log_message(self, format, *args):
                pass  # Suppress server logs

        # Start server in a separate thread
        server = HTTPServer(("localhost", OAUTH_SERVER_PORT), OAuthHandler)
        self._server_thread = Thread(target=server.serve_forever)
        self._server_thread.daemon = True
        self._server_thread.start()

        # Wait for OAuth result
        max_wait = 120  # 2 minutes timeout
        wait_count = 0
        while wait_count < max_wait and self._oauth_result is None:
            await asyncio.sleep(1)
            wait_count += 1

        server.shutdown()
        server.server_close()

        if self._oauth_result:
            # Set session with received tokens
            self.supabase.auth.set_session(self._oauth_result["access_token"], self._oauth_result["refresh_token"])

            # Refresh user and session info
            user_response = self.supabase.auth.get_user()
            if user_response.user:
                self.user = user_response.user
                self.session = self.supabase.auth.get_session()
                print(f"{self.user.email} logged in successfully!")
        else:
            print("Login timeout or failed")

    def show_login_info(self):
        """Display current login status and user information."""
        if self.is_logged_in():
            user = self.get_user()
            auth_type = self.get_auth_type()

            suffix = ""
            if auth_type["type"] == "key":
                if auth_type["source"] == "env":
                    suffix = " using an API key from HCLI_API_KEY env var"
                else:
                    suffix = " using an API key defined in hcli config"
            else:
                suffix = " using your email."

            print(f"You are logged in as {user['email'] if user else 'unknown'}{suffix}")
        else:
            print("You are not logged in.")


# Global auth service instance accessor
def get_auth_service() -> AuthService:
    """Get the global AuthService instance."""
    return AuthService.instance()


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Login</title>
</head>
<body>
  <script>
    // Extract token from hash
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    const accessToken = hashParams.get("access_token");
    const refreshToken = hashParams.get("refresh_token");

    if (accessToken) {
      // Send token back to server
      fetch("http://localhost:9999/token", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ access_token: accessToken, refresh_token: refreshToken }),
      })
      .then(() => {
        document.body.innerHTML = "Login successful! You can close this tab.";
      })
      .catch((e) => {
        console.error("Error saving token:", e);
        document.body.innerHTML = "Error saving token.";
      });
    } else {
      document.body.innerHTML = "No token found in URL.";
    }
  </script>
</body>
</html>
"""
