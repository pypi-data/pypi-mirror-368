from __future__ import annotations

import sys

import questionary
import rich_click as click

from hcli.commands.common import safe_ask_async
from hcli.lib.api.keys import keys
from hcli.lib.auth import get_auth_service
from hcli.lib.commands import async_command, require_auth
from hcli.lib.console import console


@click.command()
@click.argument("name", required=False)
@require_auth
@async_command
async def create(name: str | None) -> None:
    """Create a new API key."""
    console.print("[yellow]The key will be displayed only once, so make sure to save it in a secure place.[/yellow]")

    # Get the key name from argument or prompt
    key_name = name or await safe_ask_async(questionary.text("Enter the name for this key", default="hcli"))
    if not key_name:
        console.print("[red]Key name is required[/red]")
        return

    try:
        # Check if a key with the same name already exists
        existing_keys = await keys.get_keys()
        if any(k.name == key_name for k in existing_keys):
            console.print(f"[red]An API key with name [underline]{key_name}[/underline] already exists.[/red]")
            sys.exit(1)

        # Confirm key creation
        if not await safe_ask_async(questionary.confirm(f"Do you want to create a new API key {key_name}?")):
            console.print("[yellow]Key creation cancelled.[/yellow]")
            return

        # Create the key
        console.print(f"[blue]Creating API key '[bold]{key_name}[/bold]'...[/blue]")
        key_value = await keys.create_key(key_name)
        console.print(f"[green]API key created:[/green] [bold]{key_value}[/bold]")

        # Ask if user wants to install this key for hcli
        if await safe_ask_async(questionary.confirm("Do you want to use this key for hcli?")):
            auth_service = get_auth_service()
            auth_service.set_api_key(key_value)
            console.print("[green]API key installed successfully for hcli.[/green]")

    except Exception as e:
        console.print(f"[red]Failed to create API key: {e}[/red]")
        sys.exit(1)
