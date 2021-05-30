from typing import *

from pydantic import BaseModel, Field


class ChoreHistorySearchRequest(BaseModel):
    """
    Model for chore history search request
    """
    filter_term: str
    filter_field: Optional[str] = Field(default="completed_by", example="completed_by")
    sort_direction: Optional[str] = Field(default="desc")
    count: Optional[int] = Field(default=20)
    offset: Optional[int] = Field(default=0)
