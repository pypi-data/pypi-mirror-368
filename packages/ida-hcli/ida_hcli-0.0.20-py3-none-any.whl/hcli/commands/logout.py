from __future__ import annotations

import rich_click as click

from hcli.lib.auth import get_auth_service
from hcli.lib.console import console


@click.command()
def logout() -> None:
    """Logout from hex-rays portal."""
    auth_service = get_auth_service()

    # Initialize auth service
    auth_service.init()

    # Check authentication type
    auth_type = auth_service.get_auth_type()

    if auth_type["type"] == "key":
        console.print("[yellow]You are currently authenticated using an API key.[/yellow]")
        console.print("To remove API key authentication, use: [bold]hcli auth key uninstall[/bold]")
        return

    try:
        auth_service.logout()
        console.print("[green]Successfully logged out.[/green]")
    except Exception as e:
        console.print(f"[red]Error during logout: {e}[/red]")
