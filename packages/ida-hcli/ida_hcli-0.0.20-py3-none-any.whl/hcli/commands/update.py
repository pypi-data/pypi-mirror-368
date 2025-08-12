from __future__ import annotations

import rich_click as click

from hcli import __version__
from hcli.lib.commands import async_command
from hcli.lib.console import console
from hcli.lib.util.version import compare_versions, get_latest_pypi_version


@click.command()
@click.option("-f", "--force", is_flag=True, help="Force update.")
@click.option(
    "--check-only",
    is_flag=True,
    help="Only check for updates, do not suggest installation.",
)
@async_command
async def update(force: bool, check_only: bool) -> None:
    """Check for updates to the CLI."""
    console.print("[bold]Checking for updates...[/bold]")

    latest_version = await get_latest_pypi_version("ida-hcli")

    if latest_version is None:
        console.print("[red]Failed to check for updates from PyPI[/red]")
        return

    current_version = __version__
    update_available = compare_versions(current_version, latest_version)

    if update_available:
        console.print("[green]Update available![/green]")
        console.print(f"Current version: [yellow]{current_version}[/yellow]")
        console.print(f"Latest version: [green]{latest_version}[/green]")

        if not check_only:
            console.print("\nTo update, run:")
            console.print("[bold cyan]uv tool upgrade ida-hcli[/bold cyan]")
            console.print("or")
            console.print("[bold cyan]pipx upgrade ida-hcli[/bold cyan]")
    else:
        console.print(f"[green]You are using the latest version ({current_version})[/green]")
