from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import Conference, Host
from app.modules.conferences.schemas import ConferenceCreate


def add_new_conference_to_db(db: Session, data: ConferenceCreate) -> Conference:
    conference = Conference(**data.model_dump(exclude={"hosts"}))
    db.add(conference)

    try:
        db.flush()

        for host_name in dict.fromkeys(data.hosts):
            db.add(
                Host(
                    conference_id=conference.conference_id,
                    host_name=host_name,
                )
            )

        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(conference)
    return conference


def get_all_conferences_from_db(db: Session, skip: int, limit: int) -> list[Conference]:
    query = (
        select(Conference).order_by(Conference.conference_id).offset(skip).limit(limit)
    )
    return list(db.scalars(query).all())


def get_conference_by_id_from_db(db: Session, conference_id: int) -> Conference:
    conference = db.scalar(
        select(Conference).where(Conference.conference_id == conference_id)
    )
    if not conference:
        raise NotFoundError("Conference not found.")
    return conference
