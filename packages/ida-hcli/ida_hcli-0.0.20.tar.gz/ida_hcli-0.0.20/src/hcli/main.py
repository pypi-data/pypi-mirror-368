from __future__ import annotations

from importlib.metadata import entry_points

import rich_click as click

from hcli import __version__
from hcli.commands import register_commands
from hcli.env import ENV
from hcli.lib.console import console
from hcli.lib.util.version import BackgroundUpdateChecker

# Configure rich-click styling
click.rich_click.USE_RICH_MARKUP = True

# Global update checker instance
update_checker: BackgroundUpdateChecker | None = None


def load_extensions():
    eps = entry_points()
    return [ep.load() for ep in eps.select(group="hcli.extensions")]


def get_help_text():
    """Generate help text with extensions information."""
    base_help = f"[bold blue]HCLI[/bold blue] [dim](v{__version__})[/dim]\n\n[yellow]Hex-Rays Command-line interface for managing IDA installation, licenses and more.[/yellow]"

    # Check for available extensions
    eps = entry_points()
    extension_eps = list(eps.select(group="hcli.extensions"))

    if extension_eps:
        extensions_list = ", ".join([ep.name for ep in extension_eps])
        base_help += f"\n\n[bold green]Extensions:[/bold green] [cyan]{extensions_list}[/cyan]"

    return base_help


class MainGroup(click.Group):
    """Custom Click Group with global exception handling."""

    def main(self, *args, **kwargs):
        """Override main to add global exception handling."""
        try:
            return super().main(*args, **kwargs)
        except Exception as e:
            # Import here to avoid circular imports
            from hcli.lib.api.common import APIError, AuthenticationError, NotFoundError, RateLimitError

            if isinstance(e, AuthenticationError):
                console.print("[red]Authentication failed. Please check your credentials or use 'hcli login'.[/red]")
            elif isinstance(e, NotFoundError):
                console.print(f"[red]Resource not found: {e}[/red]")
            elif isinstance(e, RateLimitError):
                console.print("[red]Rate limit exceeded. Please try again later.[/red]")
            elif isinstance(e, APIError):
                console.print(f"[red]API Error: {e}[/red]")
            elif isinstance(e, KeyboardInterrupt):
                console.print("\n[yellow]Operation cancelled by user[/yellow]")
            else:
                console.print(f"[red]Unexpected error: {e}[/red]")
                # Optionally include debug info in debug mode
                if ENV.HCLI_DEBUG:
                    import traceback

                    console.print(f"[dim]{traceback.format_exc()}[/dim]")
            # raise click.Abort()


@click.group(help=get_help_text(), cls=MainGroup)
@click.version_option(version=__version__, package_name="ida-hcli")
@click.option("--quiet", "-q", is_flag=True, help="Run without prompts")
@click.pass_context
def cli(_ctx, quiet):
    """Main CLI entry point with background update checking."""
    global update_checker

    # Initialize update checker
    update_checker = BackgroundUpdateChecker()

    # Start background check (non-blocking)
    update_checker.start_check()

    _ctx.ensure_object(dict)
    _ctx.obj["quiet"] = quiet


@cli.result_callback()
@click.pass_context
def handle_command_completion(_ctx, _result, **_kwargs):
    """Handle command completion and show update notifications."""
    # Show update message if available (result callback only runs on success)
    update_msg = update_checker.get_result(timeout=2.0) if update_checker else None
    if update_msg:
        console.print(update_msg, markup=True)


# register subcommands
register_commands(cli)

# Register plugins dynamically
for extension in load_extensions():
    extension(cli)

if __name__ == "__main__":
    cli()
