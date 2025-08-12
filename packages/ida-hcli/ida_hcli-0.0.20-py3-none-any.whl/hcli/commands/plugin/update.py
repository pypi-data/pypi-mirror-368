"""Plugin update command."""

from __future__ import annotations

import asyncio
from pathlib import Path

import rich_click as click

from hcli.lib.commands import async_command
from hcli.lib.console import console
from hcli.lib.ida import get_ida_user_dir


def get_plugin_base_dir() -> str:
    """Get the base directory for IDA plugins."""
    ida_user_dir = get_ida_user_dir()
    if not ida_user_dir:
        raise RuntimeError("Could not determine IDA user directory")

    plugin_dir = Path(ida_user_dir) / "plugins"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    return str(plugin_dir)


def list_installed_plugins() -> list[str]:
    """List all installed plugin directories."""
    plugins = []
    plugin_base_dir = Path(get_plugin_base_dir())

    if not plugin_base_dir.exists():
        return plugins

    for plugin_dir in plugin_base_dir.iterdir():
        if not plugin_dir.is_dir():
            continue

        # Check if it has git repository
        git_dir = plugin_dir / ".git"
        if git_dir.exists():
            plugins.append(plugin_dir.name)

    return plugins


async def is_git_available() -> bool:
    """Check if git is available."""
    try:
        process = await asyncio.create_subprocess_exec(
            "git", "--version", stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
        )
        await process.communicate()
        return process.returncode == 0
    except FileNotFoundError:
        return False


async def update_plugin_repository(plugin_dir: Path) -> bool:
    """Update a plugin's git repository."""
    try:
        console.print(f"  Updating {plugin_dir.name}...")

        # Check if directory has git repository
        git_dir = plugin_dir / ".git"
        if not git_dir.exists():
            console.print(f"    [yellow]Skipping {plugin_dir.name} - not a git repository[/yellow]")
            return False

        # Pull latest changes
        process = await asyncio.create_subprocess_exec(
            "git", "pull", cwd=plugin_dir, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            output = stdout.decode("utf-8", errors="ignore").strip()
            if "Already up to date" in output or "Already up-to-date" in output:
                console.print("    [dim]Already up to date[/dim]")
            else:
                console.print("    [green]Updated successfully[/green]")
            return True
        else:
            error_msg = stderr.decode("utf-8", errors="ignore")
            console.print(f"    [red]Update failed: {error_msg}[/red]")
            return False

    except Exception as e:
        console.print(f"    [red]Update failed: {e}[/red]")
        return False


@click.command(help="Update a plugin.")
@click.argument("plugin_name", required=False)
@click.option("--all", is_flag=True, help="Update all installed plugins")
@async_command
async def update_plugin(plugin_name: str, all: bool) -> None:
    """Update an installed plugin using git pull.

    PLUGIN_NAME: The name of the plugin directory to update (optional if --all is used)
    """

    if not await is_git_available():
        console.print("[red]Git is not available. Please install git to continue.[/red]")
        return

    try:
        plugin_base_dir = Path(get_plugin_base_dir())

        if all:
            # Update all plugins
            installed_plugins = list_installed_plugins()

            if not installed_plugins:
                console.print("[yellow]No git-based plugins found to update[/yellow]")
                return

            console.print(f"[bold]Updating {len(installed_plugins)} plugin(s)...[/bold]")

            success_count = 0
            for plugin in installed_plugins:
                plugin_dir = plugin_base_dir / plugin
                if await update_plugin_repository(plugin_dir):
                    success_count += 1

            console.print()
            console.print(f"[green]Updated {success_count}/{len(installed_plugins)} plugins successfully[/green]")

        elif plugin_name:
            # Update specific plugin
            plugin_dir = plugin_base_dir / plugin_name

            if not plugin_dir.exists():
                console.print(f"[red]Plugin '{plugin_name}' not found[/red]")
                available_plugins = list_installed_plugins()
                if available_plugins:
                    console.print("[dim]Available plugins:[/dim]")
                    for p in available_plugins:
                        console.print(f"  • {p}")
                return

            console.print(f"[bold]Updating plugin '{plugin_name}'...[/bold]")

            if await update_plugin_repository(plugin_dir):
                console.print(f"[green]Plugin '{plugin_name}' updated successfully![/green]")
            else:
                console.print(f"[red]Failed to update plugin '{plugin_name}'[/red]")
        else:
            console.print("[red]Please specify a plugin name or use --all flag[/red]")
            console.print("Usage: hcli plugin update <plugin_name>")
            console.print("       hcli plugin update --all")

        if plugin_name or all:
            console.print("[yellow]Restart IDA Pro to load updated plugins[/yellow]")

    except Exception as e:
        console.print(f"[red]Update failed: {e}[/red]")
