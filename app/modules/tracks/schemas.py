from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# -------------------- base classes -------------------- #
class TrackBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    research_area_id: int = Field(..., ge=1)
    conference_id: int = Field(..., ge=1)
    reviewer_id: int = Field(..., ge=1)


# -------------------- update -------------------- #
class TrackUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    research_area_id: int | None = Field(default=None, ge=1)
    conference_id: int | None = Field(default=None, ge=1)
    reviewer_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="before")
    @classmethod
    def reject_explicit_nulls(cls, data: object) -> object:
        if isinstance(data, dict):
            required_fields = (
                "name",
                "description",
                "research_area_id",
                "conference_id",
                "reviewer_id",
            )
            for field in required_fields:
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null.")
        return data

    @field_validator("name", "description", mode="before")
    @classmethod
    def strip_and_reject_blank(cls, value: object, info) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError(f"{info.field_name} cannot be blank.")
            return stripped
        return value


# -------------------- response -------------------- #
class TrackResponse(TrackBase):
    model_config = ConfigDict(from_attributes=True)

    track_id: int
