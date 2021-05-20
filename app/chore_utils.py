import time
from typing import *
from datetime import datetime as dt
import logging
import random

from elasticsearch import ElasticsearchException
from dateutil import parser

from elasticsearch_utils import get_es_client
from redis_utils import get_redis_client
from residents_utils import get_phone_number_resident
from utilities import find_closest_match, figure_out_query_field

logging.basicConfig(level=logging.INFO)


def get_valid_chore_names(

) -> List[str]:
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


def get_chore_history(
        request_command: List[str],
        index: str = "chore-logs",
        *args,
        **kwargs
):
    command, name, count = request_command
    assert command.lower() == 'get', f"Invalid command {command}."
    es_field_for_name = figure_out_query_field(name)
    es_query = {
        "size": count,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            es_field_for_name: name
                        }
                    }
                ]
            }
        }
    }

    es_client = get_es_client()
    hits = es_client.search(index=index, body=es_query)['hits']['hits']
    hits = [h['_source'] for h in hits]

    message = ''

    if es_field_for_name == "chore_name":
        message = f"History for chore {name}.\n"
        for h in hits:
            completed_by = h['completed_by']
            completion_date = parser.parse(h['completion_date']).strftime('%B-%d-%Y')
            message += f"{completed_by} @{completion_date}.\n"

    if es_field_for_name == "completed_by":
        message = f"History for {name}.\n"
        for h in hits:
            chore_name = h['chore_name']
            completion_date = parser.parse(h['completion_date']).strftime('%B-%d-%Y')
            message += f"{chore_name} @{completion_date}.\n"

    return message, 200


def record_chore_completion(
        request_command: List[str],
        from_: str
) -> Tuple[str, int]:
    logging.info(f"From: {from_}, Command: {request_command}.")

    response_message = ""

    # get the name of the user with the incoming phone number
    resident = get_phone_number_resident(from_)
    if resident is None:
        return "You are not authorized to use this resource.", 403

    # verify that the body is a valid chore
    chore_name = request_command[0]
    is_valid_chore, best_match, match_score = is_chore_valid(chore_name)

    if not is_valid_chore:
        valid_chores = [chore_.capitalize() for chore_ in get_valid_chore_names()]
        valid_chores = ", ".join(valid_chores)
        return f"{chore_name.capitalize()} is not a valid chore name. Should be one of {valid_chores}", 422

    # if the user is verified and the chore is valid, record that the chore was completed by this user
    if match_score < 1.0:
        chore_name = best_match

    # try storing the entry in ElasticSearch
    result = record_chore_completion_elastic(chore_name, resident)['result']

    if result == "created":
        status_code = 201

        if match_score < 1.0:
            response_message += f"There is a {match_score * 100: .2f}% chance you wanted to say {chore_name}."

        response_message += f"\n Thank you for {chore_name}, {resident.capitalize()}!"
        if random.uniform(0, 1.0) > 0.95:
            response_message += f"\n They are plotting against you {resident.capitalize()}! Strike before they do!"
    else:
        logging.warning(str(result))
        status_code = 500
        response_message = f"Unfortunately, something went wrong. You should ask Daniel."

    return response_message, status_code
