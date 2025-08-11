import boto3

from rastless.core.cog import get_s3_cog_info_from_s3_path
from rastless.db.models import LayerStepModel


class S3Bucket:
    def __init__(self, bucket_name, region="eu-central-1"):
        self.bucket_name = bucket_name
        self.s3 = boto3.resource("s3", region_name=region)
        self.s3_client = boto3.client("s3")
        self.bucket = self.s3.Bucket(bucket_name)

    def list_bucket_entries(self, prefix=None):
        bucket = self.s3.Bucket(self.bucket_name)
        if prefix:
            files = bucket.objects.filter(Prefix=prefix)
        else:
            files = bucket.objects.all()

        return list(files)

    def delete_cache(self, layer_id=None, datetime=None):
        """Deletes objects based on layer ID and/or datetime, or all cache if no parameters are given."""
        if layer_id and datetime:
            prefix = f"{layer_id}/{datetime}/"
        elif layer_id:
            prefix = f"{layer_id}/"
        else:
            prefix = ""

        cache_objects = self.bucket.objects.filter(Prefix=prefix)

        for items in by_chunk(cache_objects):
            delete_keys = {"Objects": [{"Key": obj.key} for obj in items]}
            if len(delete_keys["Objects"]):
                self.bucket.delete_objects(Delete=delete_keys)

        return True


def delete_object_by_s3_path(s3_path, region="eu-central-1"):
    s3 = boto3.resource("s3", region_name=region)

    s3_cog_info = get_s3_cog_info_from_s3_path(s3_path)
    s3.Object(s3_cog_info.bucket_name, s3_cog_info.s3_object_name).delete()


def delete_layer_step_files(layer_step: LayerStepModel, cfg):
    if layer_step.cog_filepath and cfg.bucket_name in layer_step.cog_filepath:
        delete_object_by_s3_path(layer_step.cog_filepath)

    if layer_step.cog_layers:
        for _, value in layer_step.cog_layers.items():
            if cfg.bucket_name in value.s3_filepath:
                delete_object_by_s3_path(value.s3_filepath)


def by_chunk(items, chunk_size=1000):
    """
    Separate iterable objects by chunks

    For example:
    >>> by_chunk([1, 2, 3, 4, 5], chunk_size=2)
    >>> [[1, 2], [3, 4], [5]]

    Parameters
    ----------
    chunk_size: int
    items: Iterable

    Returns
    -------
    List
    """
    item_list = []
    for item in items:
        if len(item_list) >= chunk_size:
            yield item_list
            item_list = []
        item_list.append(item)
    yield item_list
