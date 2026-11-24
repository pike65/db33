from fastapi import APIRouter, status

from app.database.db import DBSession
from app.modules.areas import service
from app.modules.areas.schemas import ExpertiseAreaResponse, ResearchAreaResponse

router = APIRouter(prefix="/areas", tags=["areas"])


@router.post("/populate-areas", status_code=201)
def populate_areas(db: DBSession):
    return service.populate_areas_in_db(db)


@router.get(
    "/research-areas",
    response_model=list[ResearchAreaResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_research_areas(db: DBSession):
    return service.get_all_research_areas_from_db(db)


@router.get(
    "/expertise-areas",
    response_model=list[ExpertiseAreaResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_expertise_areas(db: DBSession):
    return service.get_all_expertise_areas_from_db(db)
