from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.database.models import ExpertiseArea, ResearchArea

RESEARCH_AREAS = [
    "Machine Learning",
    "Distributed Systems",
    "Databases",
    "Cybersecurity",
    "Software Engineering",
]

EXPERTISE_AREAS = [
    "Peer Review",
    "Data Systems",
    "Databases",
    "Cloud & Infrastructure",
    "Algorithms",
    "Applied AI",
]


def populate_areas_in_db(db: Session) -> dict:
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

    research = db.scalars(
        select(ResearchArea).order_by(ResearchArea.research_area_id)
    ).all()
    expertise = db.scalars(
        select(ExpertiseArea).order_by(ExpertiseArea.expertise_area_id)
    ).all()
    return {
        "research_areas": [
            {"research_area_id": r.research_area_id, "label": r.label} for r in research
        ],
        "expertise_areas": [
            {"expertise_area_id": e.expertise_area_id, "label": e.label}
            for e in expertise
        ],
    }


def get_all_research_areas_from_db(db: Session) -> list[ResearchArea]:
    return list(db.scalars(select(ResearchArea)).all())


def get_all_expertise_areas_from_db(db: Session) -> list[ExpertiseArea]:
    return list(db.scalars(select(ExpertiseArea)).all())
