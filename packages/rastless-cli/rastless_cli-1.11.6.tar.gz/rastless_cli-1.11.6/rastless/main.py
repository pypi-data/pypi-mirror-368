import click

from rastless.cli import colormaps, layers, management, permissions
from rastless.config import create_config


@click.group()
@click.option("--dev", is_flag=True)
@click.option("--test", is_flag=True)
@click.version_option(package_name="rastless-cli")
@click.pass_context
def cli(ctx, dev, test):
    if dev and test:
        raise click.UsageError("DEV and TEST can not both be true, choose one environment.")
    ctx.obj = create_config(dev, test)


# Management
cli.add_command(management.check_aws_connection)

# Layers
cli.add_command(layers.create_layer)
cli.add_command(layers.create_timestep)
cli.add_command(layers.list_layers)
cli.add_command(layers.delete_layer)
cli.add_command(layers.layer_exists)
cli.add_command(layers.delete_layer_timestep)
cli.add_command(layers.delete_cache)

# Colormaps
cli.add_command(colormaps.add_sld_colormap)
cli.add_command(colormaps.add_mpl_colormap)
cli.add_command(colormaps.add_discrete_colormap)
cli.add_command(colormaps.delete_colormap)
cli.add_command(colormaps.list_colormaps)

# Permissions
cli.add_command(permissions.add_permission)
cli.add_command(permissions.delete_permission)
cli.add_command(permissions.delete_layer_permission)
cli.add_command(permissions.get_permissions)
cli.add_command(permissions.add_access_token)
cli.add_command(permissions.delete_access_token)


if __name__ == "__main__":
    cli()
