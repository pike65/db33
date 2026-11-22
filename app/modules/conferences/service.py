from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import Conference, Host, Reviewer, ReviewerMaintainsConference
from app.modules.conferences.schemas import ConferenceCreate


def add_new_conference_to_db(db: Session, data: ConferenceCreate) -> Conference:
    reviewer_ids = list(dict.fromkeys(data.reviewer_ids))

    existing_reviewer_ids = set(
        db.scalars(
            select(Reviewer.reviewer_id).where(Reviewer.reviewer_id.in_(reviewer_ids))
        ).all()
    )
    missing_ids = [rid for rid in reviewer_ids if rid not in existing_reviewer_ids]
    if missing_ids:
        raise NotFoundError(f"Reviewers not found: {missing_ids}")

    conference = Conference(**data.model_dump(exclude={"hosts", "reviewer_ids"}))
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

        for reviewer_id in reviewer_ids:
            db.add(
                ReviewerMaintainsConference(
                    conference_id=conference.conference_id,
                    reviewer_id=reviewer_id,
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
