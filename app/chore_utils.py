import time
from typing import *
from datetime import datetime as dt
import logging

from elasticsearch import ElasticsearchException


from elasticsearch_utils import get_es_client
from redis_utils import get_redis_client
from utilities import find_closest_match


def get_valid_chore_names() -> List[str]:
    key = f"claremon-chore-logger::chores"
    redis_client = get_redis_client()

    if redis_client.exists(key):
        all_chores = redis_client.get(key).decode().split(",")
        return all_chores

    raise Exception(f"Key {key} does not exist.")


def is_chore_valid(
        chore_name: str,
        threshold: float = 0.93
) -> Tuple[bool, str, float]:
    # clean data
    chore_name = chore_name.lower().strip()

    # set the threshold to 0.99 for bathroom cases, because those are very similar
    if "bathroom" in chore_name:
        threshold = 0.99

    # perform string matching, in case someone made a typo
    best_match, sim_score = find_closest_match(chore_name, get_valid_chore_names(), threshold=threshold)
    is_valid_chore_name = best_match is not None
    return is_valid_chore_name, best_match, sim_score


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

    try:
        result = es.index(body=document, index="chore-logs")
    except ElasticsearchException as e:
        result = {"result": "failed", "error": e}

    return result
