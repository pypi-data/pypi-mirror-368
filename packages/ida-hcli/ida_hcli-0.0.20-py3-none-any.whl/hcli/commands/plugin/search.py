"""Plugin search command."""

from __future__ import annotations

import questionary
import rich_click as click

from hcli.commands.common import safe_ask_async
from hcli.lib.api.plugins import plugins
from hcli.lib.commands import async_command
from hcli.lib.console import console
from hcli.lib.constants import cli


@click.command()
@click.argument("query", required=False)
@click.option("--limit", default=20, help="Maximum number of results to show")
@async_command
async def search_plugins(query: str, limit: int) -> None:
    """Search for plugins in the repository."""

    if not query:
        query = await safe_ask_async(questionary.text("Enter search query:", style=cli.SELECT_STYLE))

    if not query.strip():
        console.print("[red]Search query cannot be empty[/red]")
        return

    console.print(f"[bold]Searching for plugins matching '{query}'...[/bold]")

    try:
        response = await plugins.search(query, limit=limit)

        if not response.plugins:
            console.print(f"[yellow]No plugins found matching '{query}'[/yellow]")
            return

        # Ask user if they want to install any plugin
        choices = [
            f"{plugin.slug} - {plugin.repository_description or 'No description'}" for plugin in response.plugins
        ]
        choices.append("Exit without installing")

        selection = await safe_ask_async(
            questionary.select(
                "Select a plugin to install:",
                choices=choices,
                use_jk_keys=False,
                use_search_filter=True,
                style=cli.SELECT_STYLE,
            )
        )

        if selection != "Exit without installing":
            selected_slug = selection.split(" - ")[0]

            console.print(f"[green]Installing plugin '{selected_slug}'...[/green]")
            # Import and call install command
            from .install import install_plugin_by_slug

            await install_plugin_by_slug(selected_slug)

    except Exception as e:
        console.print(f"[red]Search failed: {e}[/red]")
