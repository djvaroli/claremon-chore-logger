import time
from datetime import datetime as dt

from redis_utils import get_valid_chore_names

from utilities import write_log_entry_to_file


def is_chore_valid(
        chore_name: str
) -> bool:
    valid_chore_names = get_valid_chore_names()
    return chore_name in valid_chore_names


def record_chore_completion(
        chore_name: str,
        completed_by: str
):
    completion_date = dt.now().strftime("%B-%d-%YT%H:%M")
    completion_timestamp = int(time.time())

    return write_log_entry_to_file(chore_name, completed_by, completion_date, completion_timestamp)