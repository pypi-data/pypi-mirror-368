from __future__ import annotations

import sys

import rich_click as click

from hcli.lib.auth import get_auth_service
from hcli.lib.commands import async_command
from hcli.lib.console import console


@click.command(name="uninstall", help="Remove locally installed API key.")
@async_command
async def uninstall_key() -> None:
    """Remove zae aze locally installed API key."""
    auth_service = get_auth_service()

    # Check current auth type
    auth_type = auth_service.get_auth_type()

    if auth_type["type"] != "key":
        console.print("[yellow]No API key is currently installed.[/yellow]")
        return

    try:
        # Remove the API key
        auth_service.unset_api_key()

        # Show appropriate message based on auth source
        if auth_type["source"] == "env":
            console.print("[yellow]Note: API key was set via HCLI_API_KEY environment variable.[/yellow]")
            console.print(
                "[yellow]Please unset the HCLI_API_KEY environment variable to completely remove it.[/yellow]"
            )
        else:
            console.print("[green]API key removed successfully from hcli configuration.[/green]")

    except Exception as e:
        console.print(f"[red]Failed to remove API key: {e}[/red]")
        sys.exit(1)
