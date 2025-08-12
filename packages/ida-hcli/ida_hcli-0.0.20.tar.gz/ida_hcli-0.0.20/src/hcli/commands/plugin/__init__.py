from __future__ import annotations

import rich_click as click


@click.group()
@click.pass_context
def plugin(_ctx) -> None:
    """Manage IDA Pro plugins."""
    pass


from .enable import enable_plugin, list_plugins  # noqa: E402
from .install import install_plugin  # noqa: E402
from .search import search_plugins  # noqa: E402
from .update import update_plugin  # noqa: E402

plugin.add_command(search_plugins, name="search")
plugin.add_command(install_plugin, name="install")
plugin.add_command(enable_plugin, name="enable")
plugin.add_command(list_plugins, name="list")
plugin.add_command(update_plugin, name="update")
