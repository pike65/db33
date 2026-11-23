from pydantic import BaseModel, ConfigDict


class ResearchAreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    research_area_id: int
    label: str


class ExpertiseAreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    expertise_area_id: int
    label: str
