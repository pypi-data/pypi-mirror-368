import click
from rich.console import Console


def get_console() -> Console:
    """Get console instance with quiet mode support."""
    try:
        ctx = click.get_current_context(silent=True)
        if ctx and ctx.obj and ctx.obj.get("quiet", False):
            return Console(quiet=True)
    except RuntimeError:
        # No context available, return default console
        pass
    return Console()


# Create a proxy class that always gets the current console
class ConsoleProxy:
    def __getattr__(self, name):
        return getattr(get_console(), name)


# Global instance for convenience
console = ConsoleProxy()
