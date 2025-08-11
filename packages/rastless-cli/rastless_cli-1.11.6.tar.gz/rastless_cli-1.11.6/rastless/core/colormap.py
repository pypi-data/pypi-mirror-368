import base64
from typing import List
from xml.dom import minidom

import numpy as np

from rastless.db.models import DiscreteColorMap, MplColorMap, SldColorMap


class Sld:
    def __init__(self, filename):
        self.xml_doc = minidom.parse(filename)
        self.items = self.xml_doc.getElementsByTagName("sld:ColorMapEntry")

    @staticmethod
    def _hex_to_rgb(hex_color) -> tuple:
        hex_value = hex_color.lstrip("#")
        return tuple(int(hex_value[i : i + 2], 16) for i in (0, 2, 4))

    @property
    def hex_colors(self) -> np.array:
        return np.array(
            [entry.attributes["color"].value for entry in self.items if float(entry.attributes["opacity"].value) > 0]
        )

    @property
    def rgb_colors(self) -> np.array:
        return np.array([self._hex_to_rgb(hex_color) for hex_color in self.hex_colors])

    @property
    def values(self) -> np.array:
        return np.array(
            [
                float(entry.attributes["quantity"].value)
                for entry in self.items
                if float(entry.attributes["opacity"].value) > 0
            ]
        )

    @property
    def no_data(self) -> List:
        return [
            float(entry.attributes["quantity"].value)
            for entry in self.items
            if float(entry.attributes["opacity"].value) == 0
        ]


def legend_png_to_base64(legend_filepath: str) -> bytes:
    with open(legend_filepath, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())
    return encoded_image


def create_sld_colormap(
    name: str, sld_filepath: str, description: str = None, legend_filepath: str = None
) -> SldColorMap:
    legend_base64 = None
    if legend_filepath:
        legend_base64 = legend_png_to_base64(legend_filepath)

    sld = Sld(sld_filepath)
    return SldColorMap(
        name=name,
        values=sld.values.tolist(),
        colors=sld.rgb_colors.tolist(),
        nodata=sld.no_data,
        description=description,
        legend_image=legend_base64,
    )


def create_mpl_colormap(
    name,
    description: str,
    cm_min: float,
    cm_max: float,
    log: bool,
    mpl_name: str,
    subtitle: str,
    transparent_bounds: bool = False,
) -> MplColorMap:
    return MplColorMap(
        name=name,
        description=description,
        min=cm_min,
        max=cm_max,
        log=log,
        cmap_name=mpl_name,
        subtitle=subtitle,
        transparent_bounds=transparent_bounds,
    )


def create_discrete_colormap(
    name: str, description: str, values: List[int], colors: List[tuple[int, int, int, int]], labels: List[str]
) -> DiscreteColorMap:
    return DiscreteColorMap(name=name, description=description, values=values, colors=colors, labels=labels)
