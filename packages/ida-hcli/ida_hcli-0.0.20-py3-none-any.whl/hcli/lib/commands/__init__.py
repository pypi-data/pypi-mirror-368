import asyncio
import sys
from functools import wraps
from typing import Callable

import rich_click as click

from hcli.lib.auth import get_auth_service
from hcli.lib.console import console


def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication before executing a command."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_service = get_auth_service()
        auth_service.init()

        # Check if user is logged in
        if not auth_service.is_logged_in():
            console.print("[red]You are not logged in. Use 'hcli login'.[/red]")
            sys.exit(1)

        return f(*args, **kwargs)

    return wrapper


def async_command(f: Callable) -> Callable:
    """Decorator to run async functions in Click commands."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Running inside an existing loop (e.g. inside another async click command)
            return f(*args, **kwargs)  # returns coroutine; the caller must await
        else:
            return asyncio.run(f(*args, **kwargs))  # standalone CLI entrypoint

    return wrapper


def enforce_login() -> bool:
    """Check if user is logged in, exit if not."""
    auth_service = get_auth_service()

    if not auth_service.is_logged_in():
        console.print("[red]You are not logged in. Use 'hcli login'.[/red]")
        sys.exit(1)

    return True


class BaseCommand(click.RichCommand):
    """Base command class with optional authentication."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AuthCommand(BaseCommand):
    """Command class that requires authentication."""

    def invoke(self, ctx: click.Context):
        """Override invoke to check authentication before execution."""
        # Initialize auth service
        auth_service = get_auth_service()
        auth_service.init()

        # Enforce login
        enforce_login()

        # Call parent invoke
        return super().invoke(ctx)


# Click command decorators
def base_command(*args, **kwargs):
    """Decorator for creating a base command."""
    kwargs.setdefault("cls", BaseCommand)
    return click.command(*args, **kwargs)


def auth_command(*args, **kwargs):
    """Decorator for creating an authenticated command."""
    kwargs.setdefault("cls", AuthCommand)
    return click.command(*args, **kwargs)
