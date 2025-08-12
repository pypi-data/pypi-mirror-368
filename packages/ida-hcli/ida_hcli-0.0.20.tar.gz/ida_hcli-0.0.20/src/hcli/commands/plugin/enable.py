"""Plugin enable/disable command."""

from __future__ import annotations

from pathlib import Path

import questionary
import rich_click as click

from hcli.commands.common import safe_ask_async
from hcli.lib.commands import async_command
from hcli.lib.console import console
from hcli.lib.constants import cli
from hcli.lib.ida import get_ida_user_dir


def get_plugin_base_dir() -> str:
    """Get the base directory for IDA plugins."""
    ida_user_dir = get_ida_user_dir()
    if not ida_user_dir:
        raise RuntimeError("Could not determine IDA user directory")

    plugin_dir = Path(ida_user_dir) / "plugins"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    return str(plugin_dir)


def list_installed_plugins() -> list[tuple[str, bool]]:
    """List all installed plugins and their status."""
    plugins = []
    plugin_base_dir = Path(get_plugin_base_dir())

    if not plugin_base_dir.exists():
        return plugins

    for plugin_dir in plugin_base_dir.iterdir():
        if not plugin_dir.is_dir():
            continue

        enabled_json = plugin_dir / "ida-plugin.json"
        disabled_json = plugin_dir / "ida-plugin.json.disabled"

        if enabled_json.exists():
            plugins.append((plugin_dir.name, True))
        elif disabled_json.exists():
            plugins.append((plugin_dir.name, False))

    return plugins


def toggle_plugin_status(plugin_name: str, enable: bool) -> bool:
    """Enable or disable a plugin by renaming its config file."""
    try:
        plugin_base_dir = Path(get_plugin_base_dir())
        plugin_dir = plugin_base_dir / plugin_name

        if not plugin_dir.exists():
            console.print(f"[red]Plugin '{plugin_name}' not found[/red]")
            return False

        enabled_json = plugin_dir / "ida-plugin.json"
        disabled_json = plugin_dir / "ida-plugin.json.disabled"

        if enable:
            if disabled_json.exists():
                disabled_json.rename(enabled_json)
                console.print(f"[green]Plugin '{plugin_name}' enabled[/green]")
                return True
            elif enabled_json.exists():
                console.print(f"[yellow]Plugin '{plugin_name}' is already enabled[/yellow]")
                return True
            else:
                console.print(f"[red]No plugin configuration found for '{plugin_name}'[/red]")
                return False
        else:
            if enabled_json.exists():
                enabled_json.rename(disabled_json)
                console.print(f"[yellow]Plugin '{plugin_name}' disabled[/yellow]")
                return True
            elif disabled_json.exists():
                console.print(f"[yellow]Plugin '{plugin_name}' is already disabled[/yellow]")
                return True
            else:
                console.print(f"[red]No plugin configuration found for '{plugin_name}'[/red]")
                return False

    except Exception as e:
        console.print(f"[red]Failed to toggle plugin status: {e}[/red]")
        return False


async def interactive_plugin_selection() -> None:
    """Show interactive checkbox interface for plugin enable/disable."""
    try:
        plugins = list_installed_plugins()

        if not plugins:
            console.print("[yellow]No plugins found[/yellow]")
            console.print(f"[dim]Plugin directory: {get_plugin_base_dir()}[/dim]")
            return

        # Create choices for questionary checkbox
        choices = []
        current_enabled = {}

        for plugin_name, enabled in sorted(plugins):
            choices.append(questionary.Choice(plugin_name, checked=enabled))
            current_enabled[plugin_name] = enabled

        console.print("[bold]Select plugins to enable/disable:[/bold]")
        console.print("[dim]Use space to toggle, enter to confirm[/dim]")

        selected = await safe_ask_async(
            questionary.checkbox(
                "Plugins:",
                choices=choices,
                style=cli.SELECT_STYLE,
            )
        )

        # Compare current state with selected state and make changes
        changes_made = False
        for plugin_name, currently_enabled in current_enabled.items():
            should_be_enabled = plugin_name in selected

            if currently_enabled != should_be_enabled:
                success = toggle_plugin_status(plugin_name, should_be_enabled)
                if success:
                    changes_made = True

        if changes_made:
            console.print("[yellow]Restart IDA Pro for changes to take effect[/yellow]")
        else:
            console.print("[dim]No changes made[/dim]")

    except Exception as e:
        console.print(f"[red]Failed to manage plugins: {e}[/red]")


@click.command(help="Enable or disable a plugin")
@click.argument("plugin_name", required=False)
@click.option("--disable", is_flag=True, help="Disable the plugin instead of enabling it")
@async_command
async def enable_plugin(plugin_name: str | None, disable: bool) -> None:
    """Enable or disable plugins.

    If no plugin name is provided, shows an interactive checkbox interface
    where you can select which plugins to enable/disable.

    This command enables/disables plugins by renaming the ida-plugin.json file
    to ida-plugin.json.disabled (or vice versa).

    PLUGIN_NAME: Optional name of the plugin directory to enable/disable
    """

    if plugin_name is None:
        await interactive_plugin_selection()
        return

    enable = not disable
    action = "enable" if enable else "disable"

    console.print(f"[bold]Attempting to {action} plugin '{plugin_name}'...[/bold]")

    success = toggle_plugin_status(plugin_name, enable)

    if success:
        console.print("[yellow]Restart IDA Pro for changes to take effect[/yellow]")


@click.command(help="List installed plugins and their status")
@async_command
async def list_plugins() -> None:
    """List all installed plugins and their status."""

    try:
        plugins = list_installed_plugins()

        if not plugins:
            console.print("[yellow]No plugins found[/yellow]")
            console.print(f"[dim]Plugin directory: {get_plugin_base_dir()}[/dim]")
            return

        console.print("[bold]Installed Plugins:[/bold]")
        console.print()

        for plugin_name, enabled in sorted(plugins):
            status = "[green]enabled[/green]" if enabled else "[red]disabled[/red]"
            console.print(f"  • {plugin_name} - {status}")

        console.print()
        console.print(f"[dim]Plugin directory: {get_plugin_base_dir()}[/dim]")

    except Exception as e:
        console.print(f"[red]Failed to list plugins: {e}[/red]")
