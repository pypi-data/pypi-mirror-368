import os
from typing import List, Optional

from rastless.commands.validate import validate_list_lengths
from rastless.config import Cfg
from rastless.core.colormap import create_discrete_colormap, create_mpl_colormap, create_sld_colormap


def add_sld_colormap(cfg, sld_file: str, name: str, description: str, legend_image: str):
    """Add a SLD file"""

    if not name:
        name = os.path.basename(sld_file.split(".")[0])
    color_map = create_sld_colormap(name, sld_file, description, legend_image)
    cfg.db.add_color_map(color_map)


def add_mpl_colormap(
    cfg,
    name: str,
    description: str,
    cm_min: float,
    cm_max: float,
    mpl_name: str,
    log: bool,
    subtitle: str = None,
    transparent_bounds: bool = False,
):
    if log and float(cm_min) == 0:
        raise ValueError("Min must be greater than 0, when log is True.")

    color_map = create_mpl_colormap(name, description, cm_min, cm_max, log, mpl_name, subtitle, transparent_bounds)
    cfg.db.add_color_map(color_map)


def add_discrete_colormap(
    cfg,
    name: str,
    description: Optional[str],
    values: List[int],
    colors: List[tuple[int, int, int, int]],
    labels: List[str],
):
    validate_list_lengths(values, colors, labels)
    color_map = create_discrete_colormap(
        name=name, description=description, values=values, colors=colors, labels=labels
    )
    cfg.db.add_color_map(color_map)


def delete_colormap(cfg: Cfg, name):
    """Remove a SLD file"""
    cfg.db.delete_color_map(name)


def list_colormaps(cfg: Cfg):
    """List all colormaps"""
    return cfg.db.get_color_maps()
