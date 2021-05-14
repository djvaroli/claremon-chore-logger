from typing import *
import logging

from fastapi import FastAPI

from utilities import write_log_entry_to_file
from models import ChoreCompletionPostRequest

logger = logging.getLogger("Claremon Chore Logger")
logger.setLevel(logging.INFO)

app = FastAPI()


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/chore/record")
def record_chore_completion(request: ChoreCompletionPostRequest):
    try:
        write_log_entry_to_file(request.dict())
        status_code = 200
    except Exception as e:
        logger.error(e)
        status_code = 500

    return status_code
