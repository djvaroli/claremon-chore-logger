import time
import datetime
from enum import Enum

from pydantic import BaseModel

class ChoreCompletionPostRequest(BaseModel):
    chore_name: str
    completed_by: str
    date: str = datetime.datetime.now().strftime("%B %d %Y %H:%M %p")
    timestamp: int = int(time.time())

