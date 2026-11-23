from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class SessionBase(BaseModel):
    title: str = Field(..., max_length=100)
    room: str = Field(..., max_length=10)
    session_date: date
    start_time: datetime
    end_time: datetime


class SessionCreate(SessionBase):
    pass


class SessionResponse(SessionBase):
    model_config = ConfigDict(from_attributes=True)

    session_id: int
