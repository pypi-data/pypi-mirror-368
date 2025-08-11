import os
from pathlib import Path

ROOT_DIR = Path(os.path.abspath(__file__)).parent.parent

RASTLESS_TABLE_NAME = os.getenv("RASTLESS_TABLE_NAME", "rastless-prod")
RASTLESS_TABLE_NAME_DEV = os.getenv("RASTLESS_TABLE_NAME_DEV", "rastless-dev")
RASTLESS_TABLE_NAME_TEST = os.getenv("RASTLESS_TABLE_NAME_TEST", "rastless-end2end-test")

RASTLESS_BUCKET_NAME = os.getenv("RASTLESS_BUCKET_NAME", "rastless-prod")
RASTLESS_BUCKET_NAME_DEV = os.getenv("RASTLESS_BUCKET_NAME_DEV", "rastless-dev")
RASTLESS_BUCKET_NAME_TEST = os.getenv("RASTLESS_BUCKET_NAME_TEST", "rastless-end2end-test")

RASTLESS_BUCKET_NAME_CACHE = os.getenv("RASTLESS_BUCKET_NAME_CACHE", "rastless-cache-prod")
RASTLESS_BUCKET_NAME_CACHE_DEV = os.getenv("RASTLESS_BUCKET_NAME_CACHE_DEV", "rastless-cache-dev")
RASTLESS_BUCKET_NAME_CACHE_TEST = os.getenv("RASTLESS_BUCKET_NAME_CACHE_TEST", "rastless-cache-end2end-test")
