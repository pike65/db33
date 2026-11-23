from fastapi import APIRouter, status
from sqlalchemy.dialects.postgresql import insert

from app.database.db import DBSession
from app.database.models import ExpertiseArea, ResearchArea
from app.modules.admin import service
from app.modules.admin.data import EXPERTISE_AREAS, RESEARCH_AREAS
from app.modules.admin.schemas import ExpertiseAreaResponse, ResearchAreaResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/seed/areas", status_code=status.HTTP_201_CREATED)
def seed_areas(db: DBSession):
    db.execute(
        insert(ResearchArea)
        .values([{"label": label} for label in RESEARCH_AREAS])
        .on_conflict_do_nothing(index_elements=["label"])
    )
    db.execute(
        insert(ExpertiseArea)
        .values([{"label": label} for label in EXPERTISE_AREAS])
        .on_conflict_do_nothing(index_elements=["label"])
    )
    db.commit()
    return {"status": "seeded"}


@router.get("/research-areas", response_model=list[ResearchAreaResponse])
def get_all_research_areas(db: DBSession):
    return service.get_all_research_areas_from_db(db)


@router.get("/expertise-areas", response_model=list[ExpertiseAreaResponse])
def get_all_expertise_areas(db: DBSession):
    return service.get_all_expertise_areas_from_db(db)
