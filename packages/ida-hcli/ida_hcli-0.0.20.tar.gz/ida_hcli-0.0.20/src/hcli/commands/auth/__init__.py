from __future__ import annotations

import rich_click as click


@click.group()
def auth() -> None:
    """Authentication commands."""
    pass


# Subcommands placeholders
from .key import key  # noqa: E402

auth.add_command(key)
