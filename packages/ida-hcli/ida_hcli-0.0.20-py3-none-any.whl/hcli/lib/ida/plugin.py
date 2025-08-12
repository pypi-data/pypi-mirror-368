"""IDA plugin management utilities."""

import asyncio
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from hcli.lib.api.plugins import Plugin as APIPlugin
from hcli.lib.api.plugins import plugins
from hcli.lib.ida import get_ida_user_dir


class IdaPluginJson:
    """IDA plugin metadata representation."""

    def __init__(self, ida_metadata_descriptor_version: int, plugin: Dict[str, Any]):
        self.ida_metadata_descriptor_version = ida_metadata_descriptor_version
        self.plugin = plugin


class PluginCategory:
    """Plugin category representation."""

    def __init__(self, id: str, name: str, slug: str, description: str, icon: str):
        self.id = id
        self.name = name
        self.slug = slug
        self.description = description
        self.icon = icon


class DynamicMetadata:
    """Dynamic plugin metadata."""

    def __init__(
        self,
        stars: int = 0,
        forks: int = 0,
        watchers: int = 0,
        open_issues: int = 0,
        language: str = "",
        latest_update: str = "",
        release: Optional[Dict[str, Any]] = None,
    ):
        self.stars = stars
        self.forks = forks
        self.watchers = watchers
        self.open_issues = open_issues
        self.language = language
        self.latest_update = latest_update
        self.release = release


class Metadata:
    """Plugin metadata."""

    def __init__(
        self,
        repository_name: str,
        repository_description: str,
        repository_owner: str,
        entry_point: Optional[str] = None,
        install: Optional[str] = None,
        dynamic_metadata: Optional[DynamicMetadata] = None,
    ):
        self.repository_name = repository_name
        self.repository_description = repository_description
        self.repository_owner = repository_owner
        self.entry_point = entry_point
        self.install = install
        self.dynamic_metadata = dynamic_metadata


class Plugin:
    """Plugin representation."""

    def __init__(
        self,
        id: int,
        owner: str,
        name: str,
        slug: str,
        url: str,
        metadata: Metadata,
        updated_at: Optional[str] = None,
        categories: Optional[List[PluginCategory]] = None,
        disabled: bool = False,
    ):
        self.id = id
        self.owner = owner
        self.name = name
        self.slug = slug
        self.url = url
        self.metadata = metadata
        self.updated_at = updated_at
        self.categories = categories or []
        self.disabled = disabled


def _convert_api_plugin_to_local(api_plugin: APIPlugin) -> Plugin:
    """Convert API Plugin to local Plugin."""
    metadata = Metadata(
        repository_name=api_plugin.metadata.repository_name,
        repository_description=api_plugin.metadata.repository_description,
        repository_owner=api_plugin.metadata.repository_owner,
        entry_point=api_plugin.metadata.entryPoint,
        install=api_plugin.metadata.install,
    )

    categories = []
    if api_plugin.categories:
        for cat in api_plugin.categories:
            categories.append(
                PluginCategory(id=cat.id, name=cat.name, slug=cat.slug, description=cat.description, icon=cat.icon)
            )

    return Plugin(
        id=api_plugin.id,
        owner=api_plugin.owner,
        name=api_plugin.name,
        slug=api_plugin.slug,
        url=api_plugin.url,
        metadata=metadata,
        updated_at=api_plugin.updatedAt,
        categories=categories,
        disabled=api_plugin.disabled or False,
    )


# Global plugin cache
_PLUGINS_CACHE: Optional[List[Plugin]] = None


async def get_plugins() -> List[Plugin]:
    """Get all plugins from the API."""
    global _PLUGINS_CACHE

    if _PLUGINS_CACHE is None:
        results = await plugins.get_plugins()
        _PLUGINS_CACHE = [_convert_api_plugin_to_local(p) for p in results.hits]

    return _PLUGINS_CACHE


async def get_plugin(slug: str) -> Optional[Plugin]:
    """Get a specific plugin by slug."""
    api_plugin = await plugins.get_plugin(slug)
    return _convert_api_plugin_to_local(api_plugin) if api_plugin else None


async def get_plugin_by_name_or_title(name: str, title: Optional[str] = None) -> Optional[Plugin]:
    """Find a plugin by name or repository title."""
    plugins = await get_plugins()

    for plugin in plugins:
        if plugin.name == name:
            return plugin
        if title and plugin.metadata.repository_name == title:
            return plugin

    return None


def get_plugin_base_dir() -> Optional[str]:
    """Get the base directory for IDA plugins."""
    ida_user_dir = get_ida_user_dir()
    if ida_user_dir:
        plugin_dir = Path(ida_user_dir) / "plugins"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        return str(plugin_dir)
    return None


def get_plugin_install_dir(slug: str) -> str:
    """Get the installation directory for a specific plugin."""
    base_dir = get_plugin_base_dir()
    if base_dir:
        return str(Path(base_dir) / Path(slug).name)
    raise RuntimeError("Could not determine plugin base directory")


async def get_installed_plugins(include_disabled: bool = False) -> List[Plugin]:
    """Get all installed plugins."""
    base_dir = get_plugin_base_dir()
    if not base_dir:
        return []

    return await _find_ida_plugin_files(base_dir, include_disabled)


async def is_git_installed() -> bool:
    """Check if git is available in the system."""
    try:
        process = await asyncio.create_subprocess_exec(
            "git",
            "--version",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await process.communicate()
        return process.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def is_git_url(value: str) -> bool:
    """Check if a string is a git URL."""
    return value.lower().endswith(".git")


def get_plugin_from_git_url(value: str) -> Plugin:
    """Create a plugin object from a git URL."""
    if value.startswith("git@"):
        url = _convert_git_ssh_to_https(value)
    else:
        url = value

    parsed = urlparse(url)
    slug = parsed.path.replace(".git", "").strip("/")

    parts = slug.split("/")
    owner = parts[0] if len(parts) > 0 else ""
    name = parts[1] if len(parts) > 1 else ""

    metadata = Metadata(repository_name=slug, repository_description="", repository_owner=owner)

    return Plugin(id=slug, owner=owner, name=name, slug=slug, url=value, metadata=metadata)


def _convert_git_ssh_to_https(ssh_url: str) -> str:
    """Convert git SSH URL to HTTPS."""
    pattern = r"^git@([^:]+):(.+)\.git$"
    match = re.match(pattern, ssh_url)

    if not match:
        raise ValueError("Invalid SSH URL format")

    domain = match.group(1)
    repo_path = match.group(2)

    return f"https://{domain}/{repo_path}.git"


async def install_plugin(plugin: Plugin, install_path: str) -> bool:
    """Install a plugin to the specified path."""
    try:
        await _clone(plugin, install_path)

        # Check if ida-plugin.json file exists
        plugin_json_path = Path(install_path) / "ida-plugin.json"

        if not plugin_json_path.exists():
            plugin_metadata = _generate_plugin_metadata(plugin)
            plugin_json_path.write_text(json.dumps(plugin_metadata, indent=2))

        print(f"Plugin {plugin.slug} has been installed successfully in {install_path}")
        print("Restart IDA to see the plugin in action.")

        if plugin.metadata.install:
            print("-- Post installation instructions --")
            print(plugin.metadata.install)

        return True

    except Exception as e:
        print(f"Failed to install plugin: {e}")
        return False


def _generate_plugin_metadata(plugin: Plugin) -> Dict[str, Any]:
    """Generate IDA plugin metadata."""
    return {
        "IDAMetadataDescriptorVersion": 1,
        "plugin": {"name": plugin.name, "entryPoint": plugin.metadata.entry_point},
    }


async def update_plugin(plugin_id: str) -> bool:
    """Update an installed plugin."""
    try:
        install_path = get_plugin_install_dir(plugin_id)
        plugin = await get_plugin(plugin_id)

        if not plugin:
            print(f"Plugin {plugin_id} not found.")
            return False

        # Pull latest changes
        await _pull(plugin, install_path)

        # Update ida-plugin.json file
        plugin_json_path = Path(install_path) / "ida-plugin.json"
        plugin_metadata = _generate_plugin_metadata(plugin)
        plugin_json_path.write_text(json.dumps(plugin_metadata, indent=2))

        print(f"Plugin {plugin.id} has been updated successfully in {install_path}")
        print("Restart IDA to see the plugin in action.")

        return True

    except Exception as e:
        print(f"Failed to update plugin: {e}")
        return False


async def _clone(plugin: Plugin, install_path: str) -> None:
    """Clone a plugin repository."""
    url = plugin.url if plugin.url.endswith(".git") else f"{plugin.url}.git"

    process = await asyncio.create_subprocess_exec(
        "git",
        "clone",
        "--depth",
        "1",
        url,
        install_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(f"Git clone failed: {error_msg}")


async def _pull(plugin: Plugin, install_path: str) -> None:
    """Pull latest changes for a plugin repository."""
    process = await asyncio.create_subprocess_exec(
        "git",
        "pull",
        cwd=install_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(f"Git pull failed: {error_msg}")


async def toggle_plugin(plugin_id: str, enable: bool) -> bool:
    """Enable or disable a plugin."""
    try:
        base_dir = get_plugin_install_dir(plugin_id)
        disabled_file = Path(base_dir) / "ida-plugin.disabled.json"
        enabled_file = Path(base_dir) / "ida-plugin.json"

        if enable and disabled_file.exists():
            disabled_file.rename(enabled_file)
        elif not enable and enabled_file.exists():
            enabled_file.rename(disabled_file)

        return True

    except Exception as e:
        print(f"Failed to toggle plugin: {e}")
        return False


async def _find_ida_plugin_files(base_dir: str, include_disabled: bool = False) -> List[Plugin]:
    """Find all IDA plugin files in the base directory."""
    results: List[Plugin] = []
    base_path = Path(base_dir)

    if not base_path.exists():
        return results

    for entry in base_path.iterdir():
        if not (entry.is_dir() or entry.is_symlink()):
            continue

        # Handle symlinks
        if entry.is_symlink():
            target = entry.resolve()
            if not target.is_dir():
                continue

        sub_dir_path = entry
        for sub_entry in sub_dir_path.iterdir():
            if sub_entry.is_file() and re.match(r"^(ida-plugin|ida-plugin\.disabled)\.json$", sub_entry.name):
                disabled = "disabled" in sub_entry.name

                try:
                    plugin_data = json.loads(sub_entry.read_text())
                    plugin_id = entry.name
                    plugin_title = plugin_data.get("plugin", {}).get("name", plugin_id)

                    # Try to find the plugin in the registry
                    plugin = await get_plugin_by_name_or_title(plugin_id, plugin_title)

                    if plugin:
                        plugin.disabled = disabled
                        results.append(plugin)
                    else:
                        # Create a minimal plugin object for unknown plugins
                        metadata = Metadata(
                            repository_name=plugin_id,
                            repository_description="",
                            repository_owner="",
                        )

                        unknown_plugin = Plugin(
                            id=plugin_id,
                            owner=plugin_id,
                            name=plugin_id,
                            slug=plugin_id,
                            url=plugin_id,
                            metadata=metadata,
                            disabled=disabled,
                        )
                        results.append(unknown_plugin)

                except (json.JSONDecodeError, OSError):
                    continue

    # Filter based on disabled status
    if not include_disabled:
        results = [p for p in results if not p.disabled]

    return results
