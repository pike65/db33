from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import ExpertiseArea, ResearchArea


def get_all_research_areas_from_db(db: Session) -> list[ResearchArea]:
    return list(db.scalars(select(ResearchArea)).all())


def get_all_expertise_areas_from_db(db: Session) -> list[ExpertiseArea]:
    return list(db.scalars(select(ExpertiseArea)).all())
