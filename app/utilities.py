from typing import *
import re
from datetime import datetime as dt

from Levenshtein import jaro_winkler, jaro


VALID_ACTIONS = ['history', 'get']


def get_now_date_key():
    return dt.now().strftime("%B-%d-%Y").lower()


def find_closest_match(
    to_match: str,
    values: List[str],
    threshold: float = 0.93,
    method: str = "jaro_winkler"
) -> Tuple[Union[str, None], float]:
    if method not in ['jaro_winkler', 'jaro']:
        raise ValueError(f"Method must be one of ['jaro_winkler', 'jaro']")

    method_function_map = {
        "jaro_winkler": jaro_winkler,
        "jaro": jaro
    }
    f = method_function_map.get(method)

    match_scores = []
    for value in set(values):
        if f(value, to_match) >= threshold:
            match_scores.append({"value": value, "score": round(f(value, to_match), 4)})

    if not match_scores:
        return None, 0.0

    match_scores = sorted(match_scores, key=lambda blob: blob['score'], reverse=True)
    return match_scores[0]['value'], match_scores[0]['score']


def clean_and_split_string(s: str):
    return re.sub('[^A-Za-z0-9]+', ' ', s).lower().split()


def validate_sms_action(action):
    return action in VALID_ACTIONS



