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


def get_phone_number_resident(
        phone_number: str
) -> str:
    hash_name = f"claremon-chore-logger::phone_number>resident"
    redis_client = get_redis_client()

    resident = None
    if redis_client.hexists(hash_name, key=phone_number):
        resident = redis_client.hget(name=hash_name, key=phone_number).decode()

    return resident


def set_keys_in_redis_hash(
        hash_name: str,
        key_values: dict
):
    redis_client = get_redis_client()
    pipeline = redis_client.pipeline()
    for key, value in key_values.items():
        pipeline.hset(hash_name, key, value)

    return pipeline.execute()


def set_value_in_redis(
        key: str,
        value: str
):
    redis_client = get_redis_client()
    return redis_client.set(key, value)
