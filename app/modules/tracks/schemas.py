from pydantic import BaseModel, ConfigDict, Field


class TrackBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    research_area_id: int = Field(..., ge=1)
    conference_id: int = Field(..., ge=1)
    reviewer_id: int = Field(..., ge=1)


class TrackResponse(TrackBase):
    model_config = ConfigDict(from_attributes=True)

    track_id: int
