"""Plugin install command."""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import rich_click as click

from hcli.lib.api.plugins import plugins
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


def extract_slug_from_github_url(url: str) -> str:
    """Extract owner/repo slug from GitHub URL."""
    if url.startswith("git@"):
        # Convert SSH URL: git@github.com:owner/repo.git -> owner/repo
        pattern = r"git@github\.com:(.+/[^/]+)(?:\.git)?$"
        match = re.match(pattern, url)
        if match:
            return match.group(1).rstrip(".git")
    else:
        # Parse HTTPS URL
        parsed = urlparse(url)
        if parsed.netloc == "github.com":
            path = parsed.path.strip("/")
            if path.endswith(".git"):
                path = path[:-4]
            return path

    raise ValueError(f"Invalid GitHub URL format: {url}")


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


async def clone_repository(url: str, target_dir: str) -> None:
    """Clone a git repository."""
    process = await asyncio.create_subprocess_exec(
        "git", "clone", "--depth", "1", url, target_dir, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(f"Git clone failed: {error_msg}")


def find_plugin_entrypoint(plugin_dir: Path) -> str | None:
    """Find the Python file containing PLUGIN_ENTRY() in the plugin directory."""
    # Search current directory
    for py_file in plugin_dir.glob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            if "PLUGIN_ENTRY()" in content:
                return py_file.name
        except Exception:
            continue

    # Search one level deep
    for py_file in plugin_dir.glob("*/*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            if "PLUGIN_ENTRY()" in content:
                return str(py_file.relative_to(plugin_dir))
        except Exception:
            continue

    # Default fallback
    return None


def create_plugin_json(plugin_dir: Path, slug: str) -> None:
    """Create ida-plugin.json file if it doesn't exist."""
    plugin_json = plugin_dir / "ida-plugin.json"

    if not plugin_json.exists():
        # Find the actual entrypoint file
        entrypoint = find_plugin_entrypoint(plugin_dir)

        if entrypoint is not None:
            # Create basic plugin metadata
            metadata = {
                "IDAMetadataDescriptorVersion": 1,
                "plugin": {
                    "name": slug.split("/")[-1],
                    "entryPoint": entrypoint,
                },
            }

            plugin_json.write_text(json.dumps(metadata, indent=2))
        else:
            console.print("[red]ida-plugin.json not found and not PLUGIN_ENTRY found either.[/red]")


async def install_plugin_by_slug(slug: str, quiet: bool = False) -> None:
    """Install plugin by slug from API."""
    try:
        plugin = await plugins.get_plugin(slug)
        if not plugin:
            console.print(f"[red]Plugin '{slug}' not found in repository[/red]")
            return

        await install_plugin_by_url(plugin.url, slug)

    except Exception as e:
        console.print(f"[red]Failed to install plugin '{slug}': {e}[/red]")


async def install_plugin_by_url(github_url: str, slug: str = None, quiet: bool = False) -> None:
    """Install plugin from GitHub URL."""
    try:
        if not await is_git_available():
            console.print("[red]Git is not available. Please install git to continue.[/red]")
            return

        # Extract slug from URL if not provided
        if not slug:
            slug = extract_slug_from_github_url(github_url)

        plugin_base_dir = get_plugin_base_dir()
        plugin_name = slug.split("/")[-1]  # Get repo name from slug
        target_dir = Path(plugin_base_dir) / plugin_name

        # Check if plugin already exists
        if target_dir.exists():
            console.print(f"[yellow]Plugin '{plugin_name}' already exists in {target_dir}[/yellow]")
            console.print("[yellow]Use 'hcli plugin update' to update existing plugins[/yellow]")
            return

        console.print(f"[bold]Installing plugin '{slug}'...[/bold]")
        console.print(f"Cloning from: {github_url}")
        console.print(f"Installing to: {target_dir}")

        # Clone the repository
        await clone_repository(github_url, str(target_dir))

        # Create ida-plugin.json if it doesn't exist
        create_plugin_json(target_dir, slug)

        console.print(f"[green]Plugin '{plugin_name}' installed successfully![/green]")
        console.print(f"[green]Location: {target_dir}[/green]")
        console.print("[yellow]Restart IDA Pro to load the plugin[/yellow]")

    except Exception as e:
        console.print(f"[red]Installation failed: {e}[/red]")


@click.command(help="Install a plugin")
@click.argument("plugin_identifier")
@async_command
@click.pass_context
async def install_plugin(_ctx, plugin_identifier: str) -> None:
    """Install a plugin by slug or GitHub URL.

    PLUGIN_IDENTIFIER can be either:
    - A plugin slug (e.g., 'kasperskylab/hrtng')
    - A GitHub URL (e.g., 'https://github.com/KasperskyLab/hrtng.git')
    """
    quiet = _ctx.obj["quiet"]

    # Check if it's a URL or slug
    if plugin_identifier.startswith(("https://", "http://", "git@")):
        await install_plugin_by_url(plugin_identifier, quiet=quiet)
    else:
        await install_plugin_by_slug(plugin_identifier, quiet=quiet)
