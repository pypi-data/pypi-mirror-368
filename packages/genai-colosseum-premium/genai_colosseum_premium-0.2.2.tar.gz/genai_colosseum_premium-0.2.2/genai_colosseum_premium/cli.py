import click
from .license_client import validate_token, save_token

@click.group()
def cli():
    pass

@cli.command()
@click.argument("token")
def activate(token):
    """Activate the premium package with a license token."""
    save_token(token)
    click.echo("✅ Activation successful!")

@cli.command()
def list():
    """List available projects (requires activation)."""
    validate_token()
    click.echo("Here are the available templates...")

@cli.command()
@click.argument("usecase")
def install(usecase):
    """Install a specific project (requires activation)."""
    validate_token()
    click.echo(f"Installing {usecase}...")
