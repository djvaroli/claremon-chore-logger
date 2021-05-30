import logging
import os

from fastapi import FastAPI, Form, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from chore_utils import record_chore_completion, _get_operation_for_chore_action, get_chore_history
from utilities import clean_and_split_string, validate_sms_action

load_dotenv(".env")
logger = logging.getLogger("Claremon Chore Logger")
logger.setLevel(logging.INFO)
origins = os.environ.get("ORIGINS", "").split(";")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"]
)


@app.get("/", status_code=200)
async def home():
    return "Welcome to Claremon Chore logger!"


@app.post("/chore/record_from_sms", status_code=201)
async def record_chore_completion_from_sms(
    From: str = Form(default=None),
    Body: str = Form(default=None)
):
    resp = MessagingResponse()
    body = Body.lower()
    from_ = From.lower()

    request_command = clean_and_split_string(body)

    if len(request_command) in [2, 3]:
        try:
            action, name, count = request_command
        except ValueError as e:
            # the 5 is the default count
            request_command = request_command + [5]
            action, name, count = request_command

        if not validate_sms_action(action):
            resp.message(f"{action.capitalize()} is not a valid command.")
            return Response(content=str(resp), media_type="text/xml")

        op = _get_operation_for_chore_action(action)

    elif len(request_command) == 1:
        op = record_chore_completion

    else:
        resp.message("That command doesn't look right.")
        return Response(content=str(resp), media_type="text/xml")

    message, status_code = op(request_command=request_command, from_=from_)

    msg = resp.message(message)
    return Response(content=str(resp), media_type="text/xml")


@app.get("/chore/history")
async def search_chore_history(
        filterTerm: str,
        sortField: str = "completion_date",
        sortOrder: str = "desc",
        count: int = 20,
        offset: int = 0
):
    """

    :param filterTerm:
    :param sortField:
    :param sortOrder:
    :param count:
    :param offset:
    :return:
    """
    filter_term = str(filterTerm).lower()
    sort_field = str(sortField).lower()
    sort_order = str(sortOrder).lower()
    count = int(count)
    offset = int(offset)
    print(filter_term, sort_field, sort_order)
    return get_chore_history(filter_term, sort_field, sort_order, count, offset)




