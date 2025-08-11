# cli.py
import click
from .license_client import validate_with_server, save_local_license, load_local_license
from .installer import install_template, list_templates

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
        return
    email = data.get("email")
    save_local_license(token, email)
    click.echo("✅ Activation successful. You can now use list/install.")

@cli.command()
def list():
    """List templates (requires activation)"""
    lic = load_local_license()
    if not lic:
        click.echo("❌ Not activated. Run: genai-premium activate <TOKEN>")
        return
    templates = list_templates()
    click.echo("📦 Available templates:")
    for t in templates:
        click.echo(f" - {t}")

@cli.command()
@click.argument("template")
def install(template):
    """Install a project template"""
    lic = load_local_license()
    if not lic:
        click.echo("❌ Not activated. Run: genai-premium activate <TOKEN>")
        return
    install_template(template)
