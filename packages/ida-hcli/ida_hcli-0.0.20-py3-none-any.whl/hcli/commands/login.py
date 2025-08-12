from __future__ import annotations

import questionary
import rich_click as click

from hcli.commands.common import safe_ask_async
from hcli.lib.auth import get_auth_service
from hcli.lib.commands import async_command
from hcli.lib.config import config_store
from hcli.lib.console import console
from hcli.lib.constants import cli


@click.command()
@click.option("-f", "--force", is_flag=True, help="Force account selection.")
@async_command
async def login(force: bool) -> None:
    """Login to hex-rays portal."""
    auth_service = get_auth_service()

    # Check if already logged in
    if auth_service.is_logged_in() and not force:
        console.print("[green]You are already logged in.[/green]")
        return

    # Get the last used email for suggestions
    current_email = config_store.get_string("login.email", "")

    # Choose authentication method
    choices = ["Google OAuth", "Email (OTP)"]
    selected = await safe_ask_async(
        questionary.select("Choose login method:", choices=choices, default="Google OAuth", style=cli.SELECT_STYLE)
    )

    if selected == "Google OAuth":
        # Google OAuth login
        await auth_service.login(force)
    elif selected == "Email (OTP)":
        # Email OTP login
        email = await safe_ask_async(questionary.text("Email address", default=current_email if current_email else ""))

        try:
            console.print(f"[blue]Sending OTP to {email}...[/blue]")
            auth_service.send_otp(email, force)

            otp = await safe_ask_async(questionary.text("Enter the code received by email"))

            if auth_service.check_otp(email, otp):
                config_store.set_string("login.email", email)
                console.print("[green]Login successful![/green]")
            else:
                console.print("[red]Login failed. Invalid OTP.[/red]")
        except Exception as e:
            console.print(f"[red]Login failed: {e}[/red]")

    # Show login status
    if auth_service.is_logged_in():
        auth_service.show_login_info()
