from rastless import settings
from rastless.core.s3 import S3Bucket
from rastless.db.handler import Database


class Cfg:
    def __init__(self, table_name, bucket_name, cache_bucket_name=None):
        self.db = Database(table_name)
        self.s3 = S3Bucket(bucket_name)
        self.bucket_name = bucket_name
        self.cache_s3 = S3Bucket(cache_bucket_name)


def create_config(dev: bool = False, test: bool = False) -> Cfg:
    if dev:
        table_name = settings.RASTLESS_TABLE_NAME_DEV
        bucket_name = settings.RASTLESS_BUCKET_NAME_DEV
        cache_bucket_name = settings.RASTLESS_BUCKET_NAME_CACHE_DEV
    elif test:
        table_name = settings.RASTLESS_TABLE_NAME_TEST
        bucket_name = settings.RASTLESS_BUCKET_NAME_TEST
        cache_bucket_name = settings.RASTLESS_BUCKET_NAME_CACHE_TEST
    else:
        table_name = settings.RASTLESS_TABLE_NAME
        bucket_name = settings.RASTLESS_BUCKET_NAME
        cache_bucket_name = settings.RASTLESS_BUCKET_NAME_CACHE
    return Cfg(table_name=table_name, bucket_name=bucket_name, cache_bucket_name=cache_bucket_name)
