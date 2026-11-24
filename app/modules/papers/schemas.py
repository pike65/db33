from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

PaperStatus = Literal[
    "submitted",
    "under review",
    "accepted",
    "rejected",
    "withdrawn",
]


# -------------------- input -------------------- #
class PaperAuthorInput(BaseModel):
    author_id: int = Field(..., ge=1)
    author_order: int = Field(..., ge=1)
    is_corresponding: bool = False


class PaperVersionInput(BaseModel):
    version_number: int = Field(default=1, ge=1)
    file_location: str = Field(..., max_length=500)
    upload_datetime: datetime
    note: str | None = Field(default=None, max_length=500)


# -------------------- base classes -------------------- #
class PaperBase(BaseModel):
    title: str = Field(..., max_length=500)
    abstract: str = Field(..., max_length=500)
    submission_date: date
    track_id: int = Field(..., ge=1)
    session_id: int | None = Field(default=None, ge=1)
    keywords: list[str] = Field(..., min_length=1)


# -------------------- create -------------------- #
class PaperCreate(PaperBase):
    status: PaperStatus = "submitted"
    authors: list[PaperAuthorInput] = Field(..., min_length=1)
    version: PaperVersionInput


# -------------------- update -------------------- #
class PaperUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    abstract: str | None = Field(default=None, min_length=1, max_length=500)
    status: PaperStatus | None = None
    submission_date: date | None = None
    track_id: int | None = Field(default=None, ge=1)
    session_id: int | None = Field(default=None, ge=1)
    keywords: list[str] | None = Field(default=None, min_length=1)
    authors: list[PaperAuthorInput] | None = Field(default=None, min_length=1)
    version: PaperVersionInput | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_nulls(cls, data: object) -> object:
        if isinstance(data, dict):
            non_nullable_fields = (
                "title",
                "abstract",
                "status",
                "submission_date",
                "track_id",
                "keywords",
                "authors",
            )
            for field in non_nullable_fields:
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null.")
        return data

    @field_validator("title", "abstract", mode="before")
    @classmethod
    def strip_and_reject_blank_str(cls, value: object, info) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError(f"{info.field_name} cannot be blank.")
            return stripped
        return value

    @field_validator("keywords", mode="before")
    @classmethod
    def clean_keywords(cls, value: object) -> object:
        if isinstance(value, list):
            cleaned: list[str] = []
            for kw in value:
                if not isinstance(kw, str) or not kw.strip():
                    raise ValueError("Keywords cannot be blank.")
                cleaned.append(kw.strip())
            return cleaned
        return value


# -------------------- response -------------------- #
class PaperVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version_number: int
    file_location: str
    upload_datetime: datetime
    note: str | None


class PaperAuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    author_id: int
    author_order: int
    is_corresponding: bool


class PaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    paper_id: int
    title: str
    abstract: str
    status: PaperStatus
    submission_date: date
    track_id: int
    session_id: int | None
    keywords: list[str]
    authors: list[PaperAuthorResponse]
    versions: list[PaperVersionResponse]

    @field_validator("keywords", mode="before")
    @classmethod
    def extract_keywords(cls, value):
        if isinstance(value, list) and value and hasattr(value[0], "keyword"):
            return [item.keyword for item in value]
        return value
