from typing import *
import logging
import random

from fastapi import FastAPI, Form, Response, HTTPException
from twilio.twiml.messaging_response import MessagingResponse

from redis_utils import get_phone_number_resident
from chore_utils import is_chore_valid, record_chore_completion_elastic, get_valid_chore_names

logger = logging.getLogger("Claremon Chore Logger")
logger.setLevel(logging.INFO)

app = FastAPI()


@app.get("/", status_code=200)
async def home():
    return "Welcome to Claremon Chore logger!"


@app.post("/chore/record_from_sms")
async def record_chore_completion_from_sms(
    From: str = Form(default=None),
    Body: str = Form(default=None)
):
    # TODO refactor to remove duplicating code
    logger.info(f"From: {From}, Body: {Body}.")
    # set up the messaging response
    resp = MessagingResponse()
    response_message = "If you are seeing this, something went horribly wrong :(."

    # get the name of
    resident = get_phone_number_resident(str(From))
    logger.info(f"Resident: {resident}")
    if resident is None:
        raise HTTPException(status_code=403, detail="You do not have access to this resource.")

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
    else:
        logger.warning(str(result))
        response_message = f"Unfortunately, something went wrong. You should ask Daniel."

    msg = resp.message(response_message)
    return Response(content=str(resp), media_type="text/xml")

