import click
import simplejson

from rastless.cli.validate import parse_string_colors, parse_string_labels, parse_string_values
from rastless.commands import colormaps
from rastless.config import Cfg


@click.command()
@click.pass_obj
@click.argument("sld_file", type=click.Path(exists=True))
@click.option("-n", "--name", help="Name of the colormap, otherwise take the filename")
@click.option("-d", "--description", help="Add description")
@click.option("-l", "--legend-image", help="Filepath to png legend image")
def add_sld_colormap(cfg: Cfg, sld_file, name, description, legend_image):
    """Add a SLD file"""
    try:
        colormaps.add_sld_colormap(
            cfg=cfg, sld_file=sld_file, name=name, description=description, legend_image=legend_image
        )
    except Exception as e:
        click.echo(f"SLD File could not be converted. Reason: {e}")


@click.command()
@click.pass_obj
@click.option("-n", "--name", required=True, help="Name of the colormap")
@click.option("-d", "--description", help="Add description")
@click.option("-min", "--cm-min", required=True, help="Min colormap value")
@click.option("-max", "--cm-max", required=True, help="Max colormap value")
@click.option("-cm-name", "--mpl-cm-name", required=True, help="Matplotlib colormap name to be used")
@click.option(
    "-l",
    "--log",
    is_flag=True,
    help=("Boolean to indicate whether default scale should be logarithmic or not, default is false"),
)
@click.option(
    "-tb",
    "--transparent-bounds",
    is_flag=True,
    default=False,
    help="Make values outside [min,max] transparent (default: False)",
)
@click.option("-st", "--subtitle", help="Subtitle e.g unit written beneath the colormap")
def add_mpl_colormap(cfg: Cfg, name, description, cm_min, cm_max, mpl_cm_name, log, subtitle, transparent_bounds):
    """Add a custom colormap based on matplotlib colormaps"""
    try:
        colormaps.add_mpl_colormap(
            cfg=cfg,
            name=name,
            description=description,
            cm_min=cm_min,
            cm_max=cm_max,
            mpl_name=mpl_cm_name,
            log=log,
            subtitle=subtitle,
            transparent_bounds=transparent_bounds,
        )
    except Exception as e:
        click.echo(f"Error when adding colormap: {e}")


@click.command()
@click.pass_obj
@click.option("-n", "--name", required=True, help="Name of the colormap")
@click.option("-d", "--description", help="Add description")
@click.option(
    "-c",
    "--colors",
    required=True,
    help='colormap colors (rgba) as string list: "[[0,255,0,255],[255,0,0,255]]". Byte values.',
)
@click.option("-v", "--values", required=True, help='colormap values as string list: "[1,2]". Integer values.')
@click.option("-l", "--labels", required=True, help='colormap labels as string list: "[low, high]"')
def add_discrete_colormap(cfg: Cfg, name, description, colors, values, labels):
    """Add a discrete colormap based on matplotlib colormaps"""
    try:
        colors = parse_string_colors(colors)
        values = parse_string_values(values)
        labels = parse_string_labels(labels)

        colormaps.add_discrete_colormap(
            cfg=cfg, name=name, description=description, colors=colors, values=values, labels=labels
        )
    except Exception as e:
        click.echo(f"Error when adding colormap: {e}")


@click.command()
@click.option("-n", "--name", help="Name of the colormap", required=True)
@click.pass_obj
def delete_colormap(cfg: Cfg, name):
    """Remove a SLD file"""
    colormaps.delete_colormap(cfg, name)


@click.command()
@click.pass_obj
def list_colormaps(cfg: Cfg):
    """List all colormaps"""
    cms = colormaps.list_colormaps(cfg)
    click.echo(simplejson.dumps(cms, indent=4, sort_keys=True))
    return cms
