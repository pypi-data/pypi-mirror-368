import os
from typing import Optional

import typer
from yaspin import yaspin

from .sync_client import Client


app = typer.Typer(help="CLI for the BanGuard API.")

def get_client(token: Optional[str] = None, check_token: Optional[bool] = True) -> Client:
    """Helper to initialize the API client with a token."""
    token = token or os.getenv("BANGUARD_TOKEN")
    if not token and check_token:
        typer.echo("Error: No token provided. Use --token or set BANGUARD_TOKEN env var.")
        raise typer.Exit(1)
    return Client(token, check_token)

@app.command(help="Check if your token is valid.")
def check_token(token: Optional[str] = typer.Option(None, help="API token for BanGuard.")):
    client = get_client(token, check_token=False)
    valid = client.is_token_valid()
    if valid:
        typer.echo("Token is valid.")
    else:
        typer.echo("Token is invalid.")

@app.command(help="Get total ban count from BanGuard.")
def ban_count():
    client = get_client(check_token=False)
    count = client.get_ban_count()
    typer.echo(f"Total bans: {count}")

@app.command(help="Ban a player by UUID.")
def ban_player(
        player_uuid: str, category: str, token: str):
    client = get_client(token)
    player = client.get_player(player_uuid)
    with yaspin(text=f"Banning {player.latest_name}...") as spinner:
        ban = client.ban_player(player, category)
        spinner.ok("✔")
    typer.echo(f"Player {player.latest_name} banned with ID {ban.id} for '{category}'.")

@app.command(help="Unban a player by ban ID.")
def unban_player(ban_id: str, token: Optional[str] = typer.Option(None, help="API token for BanGuard.")):
    client = get_client(token)
    with yaspin(text=f"Unbanning ban ID {ban_id}...") as spinner:
        try:
            client.unban_player(ban_id)
            spinner.ok("✔")
            typer.echo(f"Ban ID {ban_id} has been successfully removed.")
        except Exception as e:
            spinner.fail("✘")
            typer.echo(f"Failed to unban: {e}")

@app.command(help="Get list of ban categories.")
def ban_categories():
    client = get_client(check_token=False)
    categories = client.get_ban_categories()
    typer.echo("Ban categories:")
    for category in categories:
        typer.echo(f" - {category}")

@app.command(help="Get player info by Terraria UUID.")
def get_player(player_uuid: str, token: Optional[str] = typer.Option(None, help="API token for BanGuard.")):
    client = get_client(token)
    player = client.get_player(player_uuid)
    typer.echo(f"Player: {player.latest_name}")

@app.command(help="Get bans for a player.")
def player_bans(
        player_uuid: str,
        ip: Optional[str] = typer.Option(None, help="Optional player IP."),
        name: Optional[str] = typer.Option(None, help="Optional player name."),
        token: Optional[str] = typer.Option(None, help="API token for BanGuard.")
):
    client = get_client(token)
    player = client.get_player(player_uuid)
    bans = client.get_player_bans(player, ip=ip, name=name)
    if not bans:
        typer.echo("No bans found for this player.")
        return
    typer.echo("Player bans:")
    for b in bans:
        typer.echo(f" - ID: {b.id}, Category: {b.category}, Server: {b.server or 'N/A'}")

if __name__ == "__main__":
    app()
