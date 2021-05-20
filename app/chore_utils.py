import time
from typing import *
from datetime import datetime as dt
import logging

from elasticsearch_utils import get_es_client
from redis_utils import get_redis_client
from utilities import write_log_entry_to_file


def get_valid_chore_names() -> List[str]:
    key = f"claremon-chore-logger::chores"
    redis_client = get_redis_client()

    if redis_client.exists(key):
        all_chores = redis_client.get(key).decode().split(",")
        return all_chores

    raise Exception(f"Key {key} does not exist.")


def is_chore_valid(
        chore_name: str
) -> bool:
    return chore_name.lower() in get_valid_chore_names()


def record_chore_completion_csv(
        chore_name: str,
        completed_by: str
):
    completion_date = dt.now().strftime("%B-%d-%YT%H:%M")
    completion_timestamp = int(time.time())

    return write_log_entry_to_file(chore_name, completed_by, completion_date, completion_timestamp)


def record_chore_completion_elastic(
        chore_name: str,
        completed_by: str
):
    es = get_es_client()
    document = {
        "completion_date": dt.now(),
        "timestamp": int(time.time()) * 1000, # convert to ms for elasticsearch
        "chore_name": chore_name,
        "completed_by": completed_by
    }

    return es.index(body=document, index="chore-logs")