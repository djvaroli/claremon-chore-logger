import os
from typing import *
import logging
from urllib.parse import urlparse

import redis
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = urlparse(os.environ.get("REDIS_URL"))


def get_redis_client():
    return redis.Redis(
        host=REDIS_URL.hostname,
        port=REDIS_URL.port,
        username=REDIS_URL.username,
        password=REDIS_URL.password,
        ssl=False,
        ssl_cert_reqs=None
    )


def set_keys_in_redis_hash(
        hash_name: str,
        key_values: dict
):
    redis_client = get_redis_client()
    pipeline = redis_client.pipeline()
    for key, value in key_values.items():
        pipeline.hset(hash_name, key, value)

    result = pipeline.execute()
    redis_client.close()
    return result


def set_value_in_redis(
        key: str,
        value: str
):
    redis_client = get_redis_client()
    result = redis_client.set(key, value)
    redis_client.close()
    return result
