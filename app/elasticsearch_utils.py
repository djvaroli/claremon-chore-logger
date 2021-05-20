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

