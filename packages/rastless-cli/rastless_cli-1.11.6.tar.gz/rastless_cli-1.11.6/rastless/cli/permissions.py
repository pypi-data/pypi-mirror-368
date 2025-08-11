import click
import simplejson

from rastless.commands import permissions as cmd_permissions
from rastless.config import Cfg


@click.command()
@click.option(
    "-p", "--permission", required=True, type=str, help="Role e.g role#<client>:<client_role>, user#<username>"
)
@click.option("-l", "--layer_ids", help="Layer id", required=True, type=str, multiple=True)
@click.pass_obj
def add_permission(cfg: Cfg, permission, layer_ids):
    """Add a role to one or multiple layers."""
    cmd_permissions.add_permission(cfg, permission, layer_ids)
    click.echo("Role was successfully added to layers")


@click.command()
@click.option(
    "-p",
    "--permissions",
    help="Permission name e.g role#<client>:<client_role>, user#<username>",
    required=True,
    type=str,
    multiple=True,
)
@click.pass_obj
def delete_permission(cfg: Cfg, permissions):
    """Delete one or multiple permissions."""
    cmd_permissions.delete_permission_asdf(cfg, permissions)
    click.echo("Roles were successfully deleted")


@click.command()
@click.option(
    "-p",
    "--permission",
    help="Permission name e.g role#<client>:<client_role>, user#<username>",
    required=True,
    type=str,
)
@click.option("-l", "--layer_ids", help="Layer ids", type=str, required=True, multiple=True)
@click.pass_obj
def delete_layer_permission(cfg: Cfg, permission, layer_ids):
    """Delete one or multiple layer permissions."""
    cmd_permissions.delete_layer_permission(cfg, permission, layer_ids)
    click.echo("Layer permission was successfully deleted")


@click.command()
@click.option("-l", "--layer_id", help="Layer id", type=str)
@click.option("-p", "--permission", type=str, help="Role e.g role#<client>:<client_role>, user#<username>")
@click.pass_obj
def get_permissions(cfg: Cfg, layer_id, permission):
    """Get layer ids for a role or get all permissions for a layer id."""
    items = cmd_permissions.get_permissions(cfg, layer_id, permission)

    click.echo(simplejson.dumps(items, indent=4, sort_keys=True))


@click.command()
@click.option("-a", "--access_token", help="Access token", type=str)
@click.option("-l", "--layer_ids", help="Layer ids", type=str, required=True, multiple=True)
@click.pass_obj
def add_access_token(cfg: Cfg, access_token, layer_ids):
    """Create access token for project eoapp"""
    access_token_id = cmd_permissions.create_access_token(cfg, layer_ids, access_token)
    click.echo(f"Access token: {access_token_id}")


@click.command()
@click.option("-a", "--access_token", help="Access token", type=str)
@click.pass_obj
def delete_access_token(cfg: Cfg, access_token: str):
    cmd_permissions.delete_access_token(cfg, access_token)
    click.echo(f"Access token {access_token} was successfully deleted")
