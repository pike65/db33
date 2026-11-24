from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SessionBase(BaseModel):
    title: str = Field(..., max_length=100)
    room: str = Field(..., max_length=10)
    session_date: date
    start_time: datetime
    end_time: datetime

    conference_id: int = Field(..., ge=1)
    reviewer_id: int = Field(..., ge=1)


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    room: str | None = Field(default=None, min_length=1, max_length=10)
    session_date: date | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None

    conference_id: int | None = Field(default=None, ge=1)
    reviewer_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_nulls(cls, data: object) -> object:
        if isinstance(data, dict):
            required_fields = (
                "title",
                "room",
                "session_date",
                "start_time",
                "end_time",
                "conference_id",
                "reviewer_id",
            )
            for field in required_fields:
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null.")
        return data

    @field_validator("title", "room", mode="before")
    @classmethod
    def strip_and_reject_blank(cls, value: object, info) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError(f"{info.field_name} cannot be blank.")
            return stripped
        return value


class SessionResponse(SessionBase):
    model_config = ConfigDict(from_attributes=True)

    session_id: int
