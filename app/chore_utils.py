import time
from typing import *
from datetime import datetime as dt
import logging
import random

from elasticsearch import ElasticsearchException
from dateutil import parser

from elasticsearch_utils import get_es_client, chore_history_filter_query, get_document_count_for_query
from redis_utils import get_redis_client
from residents_utils import get_phone_number_resident, get_residents_names
from utilities import find_closest_match, validate_sms_action
from elasticsearch_utils import get_query_for_chore_history

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


def get_chore_history_sms_request(
        request_command: List[str],
        index: str = "chore-logs",
        *args,
        **kwargs
):
    command, name, count = request_command
    assert command.lower() == 'get', f"Invalid command {command}."
    es_field_for_name = _figure_out_query_field(name)
    es_query = get_query_for_chore_history(name, es_field_for_name, count=count)

    es_client = get_es_client()
    hits = es_client.search(index=index, body=es_query)['hits']['hits']
    hits = [h['_source'] for h in hits]

    message = ''

    if es_field_for_name == "chore_name":
        message = f"History ({count} most recent) for chore {name.capitalize()}.\n\n"
        for h in hits:
            completed_by = h['completed_by']
            completion_date = parser.parse(h['completion_date']).strftime('%B-%d %I:%M %p')
            message += f"{completed_by.capitalize()} @{completion_date}.\n"

    if es_field_for_name == "completed_by":
        message = f"History ({count} most recent) for {name.capitalize()}.\n\n"
        for h in hits:
            chore_name = h['chore_name']
            completion_date = parser.parse(h['completion_date']).strftime('%B-%d %I:%M %p')
            message += f"{chore_name.capitalize()} @{completion_date}.\n"

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
            response_message += f"There is a {match_score * 100: .2f}% chance you wanted to say {chore_name}.\n"

        chore_completion_message = _get_chore_completion_message(chore_name)
        response_message += f"{chore_completion_message}, {resident.capitalize()}!\n"
        if random.uniform(0, 1.0) > 0.95:
            response_message += f"They are plotting against you {resident.capitalize()}! Strike before they do!"
    else:
        logging.warning(str(result))
        status_code = 500
        response_message = f"Unfortunately, something went wrong. You should ask Daniel."

    return response_message, status_code


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


def _get_operation_for_chore_action(action):
    assert validate_sms_action(action), f"Invalid action {action}."

    action_op_map = {
        "get": get_chore_history_sms_request,
        "history": get_chore_history_sms_request
    }
    return action_op_map[action]


def _figure_out_query_field(
        name: str
) -> Union[str, None]:
    valid_chores = get_valid_chore_names()
    valid_resident_names = get_residents_names()

    if name.lower() in valid_chores:
        return "chore_name"

    if name.lower() in valid_resident_names:
        return "completed_by"

    return None


def _get_chore_completion_message(chore_name: str) -> Union[str, None]:
    hash_name = f"claremon-chore-logger::chore-completion-message"
    redis_client = get_redis_client()

    if redis_client.hexists(hash_name, chore_name):
        return redis_client.hget(hash_name, chore_name).decode()

    return f"Thank you for completing task {chore_name.capitalize()}"


def get_chore_history(
        filter_query: str,
        sort_field: str = "completed_by",
        sort_order: str = "desc",
        count: int = 20,
        offset: int = 0,
        index: str = "chore-logs"
):
    """

    :param filter_query:
    :param sort_field:
    :param sort_order:
    :param count:
    :param offset:
    :param index:
    :return:
    """

    def _filter_hits_by_query(hits_: List[dict], query_: str):
        if not query_:
            return hits_

        filter_fields_ = ['completed_by', 'chore_name']
        filtered_hits_ = []
        for hit_ in hits_:
            for filter_field_ in filter_fields_:
                value_: str = hit_.get(filter_field_)
                print(value_)
                if value_ and value_.__contains__(query_.lower().strip()):
                    filtered_hits_.append(hit_)
        return filtered_hits_

    query = chore_history_filter_query(sort_field, sort_order, count, offset)
    es = get_es_client()
    hits = es.search(index=index, body=query)['hits']['hits']
    hits = [h['_source'] for h in hits]
    data = {
        "documents": _filter_hits_by_query(hits, filter_query),
        "document_count": get_document_count_for_query(query, index)
    }
    return data

