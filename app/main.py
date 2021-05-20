from typing import *
import logging
import random

from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse

from redis_utils import get_phone_number_resident
from chore_utils import is_chore_valid, record_chore_completion_elastic, get_valid_chore_names


logger = logging.getLogger("Claremon Chore Logger")
logger.setLevel(logging.INFO)

app = FastAPI()


@app.get("/")
async def home():
    return {"status": "ok"}


@app.post("/chore/record_from_sms")
async def record_chore_completion_from_sms(
    From: str = Form(default=None),
    Body: str = Form(default=None)
):
    # TODO refactor to remove duplicating code

    # set up the messaging response
    resp = MessagingResponse()
    response_message = "If you are seeing this, something went horribly wrong :(."

    # get the name of
    resident = get_phone_number_resident(str(From))
    if resident is None:
        raise Exception("User authentication failed.")

    # verify that the body is a valid chore
    if not is_chore_valid(Body):
        valid_chores = [chore_.capitalize() for chore_ in get_valid_chore_names()]
        valid_chores = ", ".join(valid_chores)
        response_message = f"{Body} is not a valid chore name. Should be one of {valid_chores}"
        msg = resp.message(response_message)
        return Response(content=str(resp), media_type="text/xml")

    # if the user is verified and the chore is valid, record that the chore was completed by this user
    result = record_chore_completion_elastic(Body.lower(), resident)['result']
    if result == "created":
        response_message = f"Thank you for {Body.capitalize()}, {resident.capitalize()}!"
        if random.uniform(0, 1.0) > 0.95:
            response_message += f"\n. They are plotting against you {resident.capitalize()}! Strike before they do!"

    msg = resp.message(response_message)
    return Response(content=str(resp), media_type="text/xml")

