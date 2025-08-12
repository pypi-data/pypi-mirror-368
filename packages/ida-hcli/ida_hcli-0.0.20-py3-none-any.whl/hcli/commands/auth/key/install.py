from __future__ import annotations

import sys

import questionary
import rich_click as click

from hcli.commands.common import safe_ask_async
from hcli.lib.auth import get_auth_service
from hcli.lib.commands import async_command
from hcli.lib.console import console


@click.command(name="install")
@click.option("-k", "--key", help="API key to install")
@async_command
async def install_key(key: str | None) -> None:
    """Install an API key locally."""
    auth_service = get_auth_service()

    # Get key from option or prompt
    if not key:
        key = await safe_ask_async(questionary.password("Enter API key"))

    if not key:
        console.print("[red]No API key provided[/red]")
        sys.exit(1)

    try:
        # Install the API key
        auth_service.set_api_key(key)
        console.print("[green]API key installed successfully[/green]")

        # Show confirmation with auth info
        auth_service.show_login_info()

    except Exception as e:
        console.print(f"[red]Failed to install API key: {e}[/red]")
        sys.exit(1)
