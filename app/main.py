import logging

from fastapi import FastAPI, Form, Response, HTTPException
from twilio.twiml.messaging_response import MessagingResponse

from chore_utils import record_chore_completion, _get_operation_for_chore_action
from utilities import clean_and_split_string, validate_sms_action

logger = logging.getLogger("Claremon Chore Logger")
logger.setLevel(logging.INFO)

app = FastAPI()


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

