import os
import tempfile
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Set

import boto3
from pyproj import Transformer
from rio_cogeo.cogeo import cog_info, cog_translate, cog_validate
from rio_cogeo.profiles import cog_profiles

from rastless.core.schemas import CompressionTypes
from rastless.core.utils import merge_bbox_extent
from rastless.custom_exceptions import FileUploadError
from rastless.db.models import CogFile, LayerStepModel

if TYPE_CHECKING:
    from rastless.config import Cfg


@dataclass
class S3Cog:
    filename: str
    bucket_name: str
    s3_object_name: str
    s3_path: str
    filepath: str = None

    @property
    def identifier(self):
        return os.path.splitext(self.filename)[0]


@dataclass
class LayerInfo:
    bbox_wgs84: tuple[float, float, float, float]
    resolution: float
    minzoom: int
    maxzoom: int


def create_s3_cog_info(bucket_name: str, layer_id: str, datetime: str, filepath: str) -> S3Cog:
    filename = os.path.basename(filepath)
    object_name = f"layer/{layer_id}/{datetime}/{filename}"
    s3_path = f"s3://{bucket_name}/{object_name}"
    return S3Cog(
        s3_object_name=object_name, s3_path=s3_path, bucket_name=bucket_name, filename=filename, filepath=filepath
    )


def get_s3_cog_info_from_s3_path(s3_file_path: str) -> S3Cog:
    parts = s3_file_path.split("/")
    object_name = "/".join(parts[3:])
    return S3Cog(s3_object_name=object_name, s3_path=s3_file_path, bucket_name=parts[2], filename=parts[-1])


def upload_cog_file(s3_cog: S3Cog) -> bool:
    s3_client = boto3.client("s3")

    try:
        s3_client.upload_file(s3_cog.filepath, s3_cog.bucket_name, s3_cog.s3_object_name)
    except Exception:
        return False
    return True


def transform_upload_cog(s3_cog: S3Cog, cog_profile: str) -> bool:
    s3_client = boto3.client("s3")
    dst_profile = cog_profiles.get(cog_profile)
    if cog_profile == CompressionTypes.WEBP.value:
        dst_profile["webp_level"] = 95

    temp_dst = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)

    try:
        cog_translate(s3_cog.filepath, temp_dst.name, dst_profile)
        temp_dst.seek(0)
        s3_client.upload_file(temp_dst.name, s3_cog.bucket_name, s3_cog.s3_object_name)
    except Exception:
        return False
    finally:
        temp_dst.close()
        os.remove(temp_dst.name)

    return True


def layer_is_valid_cog(filepath: str) -> bool:
    result = cog_validate(filepath, quiet=True)
    return result == (True, [], [])


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a, strict=True)


def transform_bbox(bbox, in_proj: str, out_proj: str = "EPSG:4326") -> List[float]:
    transformer = Transformer.from_crs(in_proj, out_proj, always_xy=True)

    if in_proj == "EPSG:4326":
        bbox_wgs84_array = bbox
    else:
        bbox_wgs84 = [transformer.transform(x, y) for x, y in pairwise(bbox)]
        bbox_wgs84_array = list(sum(bbox_wgs84, ()))

    return bbox_wgs84_array


def get_layer_info(filename: str) -> LayerInfo:
    result = cog_info(filename)
    geo_info = result["GEO"]
    bbox_wgs84 = transform_bbox(geo_info["BoundingBox"], geo_info["CRS"])
    bbox_wgs84 = tuple([round(x, 6) for x in bbox_wgs84])
    max_zoom = geo_info["MaxZoom"] + 2 if geo_info["MaxZoom"] < 21 else geo_info["MaxZoom"]

    return LayerInfo(
        bbox_wgs84=bbox_wgs84,
        resolution=float(geo_info["Resolution"][0]),
        maxzoom=max_zoom,
        minzoom=geo_info["MinZoom"],
    )


def upload_files(
    cfg: "Cfg",
    filenames: Set[str],
    layer_id: str,
    datetime: str,
    profile: str,
    cog_layers: dict,
    bboxes: List,
    resolutions: List,
    min_zoom: List,
    max_zoom: List,
) -> (Set[str], List[float], float):
    for filename in filenames:
        s3_cog = create_s3_cog_info(cfg.s3.bucket_name, layer_id, datetime, filename)
        layer_info = get_layer_info(filename)

        if layer_is_valid_cog(filename):
            uploaded = upload_cog_file(s3_cog)
        else:
            uploaded = transform_upload_cog(s3_cog, profile)

        if uploaded:
            cog_layers[s3_cog.identifier] = CogFile(s3_filepath=s3_cog.s3_path, bbox=layer_info.bbox_wgs84)
            bboxes.append(tuple(layer_info.bbox_wgs84))
            resolutions.append(layer_info.resolution)
            min_zoom.append(layer_info.minzoom)
            max_zoom.append(layer_info.maxzoom)
        else:
            raise FileUploadError(f"File {filename} could not be uploaded. Please try again.")

    bbox_extent = merge_bbox_extent(bboxes)

    return cog_layers, bbox_extent, min(resolutions), min(min_zoom), max(max_zoom)


def create_new_timestep(
    cfg: "Cfg", filenames: Set[str], layer_id: str, datetime: str, profile: str, temporal_resolution: str, sensor: str
):
    cog_layers = {}
    bboxes = []
    resolutions = []
    min_zoom = []
    max_zoom = []

    cog_layers, bbox_extent, resolution, min_zoom, max_zoom = upload_files(
        cfg, filenames, layer_id, datetime, profile, cog_layers, bboxes, resolutions, min_zoom, max_zoom
    )

    layer_step = LayerStepModel(
        layer_id=layer_id,
        cog_layers=cog_layers,
        datetime=datetime,
        sensor=sensor,
        temporal_resolution=temporal_resolution,
        maxzoom=22,
        minzoom=0,
        bbox=bbox_extent,
        resolution=round(resolution, 6),
    )

    cfg.db.add_layer_step(layer_step)


def append_to_timestep(cfg: "Cfg", layer_step: LayerStepModel, filenames: Set[str], profile: str):
    if layer_step.cog_filepath:
        raise ValueError("Appending to old format is not allowed")

    bboxes = [layer_step.bbox]
    resolutions = [layer_step.resolution]
    min_zoom = [layer_step.minzoom]
    max_zoom = [layer_step.maxzoom]

    cog_layers, bbox_extent, resolution, min_zoom, max_zoom = upload_files(
        cfg,
        filenames,
        layer_step.layer_id,
        layer_step.datetime,
        profile,
        layer_step.cog_layers,
        bboxes,
        resolutions,
        min_zoom,
        max_zoom,
    )

    layer_step = LayerStepModel(
        layer_id=layer_step.layer_id,
        cog_layers=cog_layers,
        datetime=layer_step.datetime,
        sensor=layer_step.sensor,
        temporal_resolution=layer_step.temporal_resolution,
        maxzoom=max_zoom,
        minzoom=min_zoom,
        bbox=bbox_extent,
        resolution=round(resolution, 6),
    )
    cfg.db.add_layer_step(layer_step)
