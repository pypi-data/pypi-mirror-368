from typing import List

from rastless.config import Cfg
from rastless.custom_exceptions import ColorMapDoesNotExistError, ColorMapParseError


def validate_list_lengths(values: List[int], colors: List[tuple[int, int, int, int]], labels: List[str]):
    if not len(values) == len(colors) == len(labels):
        raise ColorMapParseError("values, colors and labels list need to be of same length")


def validate_colormap_exists(cfg: Cfg, **kwargs):
    if kwargs.get("colormap"):
        if not cfg.db.get_color_map(kwargs["colormap"]):
            raise ColorMapDoesNotExistError(
                f"Error when creating layer as colormap with name {kwargs['colormap']} "
                f"does not exist. Create colormap first."
            )
