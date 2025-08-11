# cli.py
import sys
import click
from .license_client import validate_with_server, save_local_license, load_local_license
from .installer import install_template, list_templates

def check_activation():
    lic = load_local_license()
    if not lic:
        click.echo("❌ Not activated. Run: genai-premium activate <TOKEN>")
        sys.exit(1)
    token = lic.get("token")
    ok, data = validate_with_server(token)
    if not ok:
        click.echo(f"❌ Activation token invalid or expired. Please reactivate: genai-premium activate <TOKEN>")
        sys.exit(1)
    # If needed, you can refresh/save license info here

@click.group()
def cli():
    pass

@cli.command()
@click.argument("token")
def activate(token):
    """Activate using the token emailed to you"""
    ok, data = validate_with_server(token)
    if not ok:
        click.echo(f"❌ Token invalid or error: {data}")
        sys.exit(1)
    email = data.get("email")
    save_local_license(token, email)
    click.echo("✅ Activation successful. You can now use list/install.")

@cli.command()
def list():
    """List templates (requires activation)"""
    check_activation()
    templates = list_templates()
    click.echo("📦 Available templates:")
    for t in templates:
        click.echo(f" - {t}")

@cli.command()
@click.argument("template")
def install(template):
    """Install a project template"""
    check_activation()
    install_template(template)
