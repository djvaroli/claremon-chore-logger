from typing import *
import os, re, logging

from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

# Log transport details
logging.basicConfig(level=logging.INFO)

# Parse the auth and host from env:
BONSAI_URL = os.environ['BONSAI_URL']


def get_es_client():
    auth = re.search('https\:\/\/(.*)\@', BONSAI_URL).group(1).split(':')
    host = BONSAI_URL.replace('https://%s:%s@' % (auth[0], auth[1]), '')

    match = re.search('(:\d+)', host)
    if match:
        p = match.group(0)
        host = host.replace(p, '')
        port = int(p.split(':')[1])
    else:
        port = 443

    # Connect to cluster over SSL using auth for best security:
    es_header = [{
        'host': host,
        'port': port,
        'use_ssl': True,
        'http_auth': (auth[0], auth[1])
    }]

    return Elasticsearch(es_header)


def get_query_for_chore_history(
        filter_term: str,
        filter_field: str = "completed_by",
        sort_direction: str = "desc",
        count: int = 20,
        offset: int = 0
):

    base_query = {
        "size": count,
        "from": offset,
        "sort": [
            {"completion_date": {"order": sort_direction}}
        ]
    }

    if filter_field is not None:
        base_query['query'] = {
            "bool": {
                "must": [
                    {
                        "term": {
                            filter_field: filter_term
                        }
                    }
                ]
            }
        }

    else:
        base_query['query'] = {
            "match_all": {}
        }

    return base_query


def chore_history_filter_query(
        sort_field: str = "completion_date",
        sort_order: str = "desc",
        count: int = 20,
        offset: int = 0
):
    """

    :param sort_field:
    :param sort_order:
    :param count:
    :param offset:
    :return:
    """
    query = {
        "size": count,
        "from": offset,
        "sort": [
            {sort_field: {"order": sort_order}}
        ],
        "query": {
            "match_all": {}
        }
    }

    return query


def get_document_count_for_query(
        query: dict,
        index: str
):
    """

    :param query:
    :param index:
    :return:
    """
    fields_to_strip = ['size', 'from', 'sort', 'source']
    es = get_es_client()
    query_stripped = query.copy()
    for field in fields_to_strip:
        query_stripped.pop(field, None)

    count = es.count(body=query_stripped, index=index)
    if count:
        return count['count']
    return 0

