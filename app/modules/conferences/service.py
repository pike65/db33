from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import (
    Conference,
    Host,
    ResearchArea,
    Reviewer,
    ReviewerMaintainsConference,
    Track,
)
from app.modules.conferences.schemas import ConferenceCreate, ConferenceUpdate


def _sync_conference_hosts(db: Session, conference_id: int, hosts: list[str]) -> None:
    unique_hosts = list(dict.fromkeys(hosts))
    db.execute(delete(Host).where(Host.conference_id == conference_id))
    for host_name in unique_hosts:
        db.add(Host(conference_id=conference_id, host_name=host_name))


def add_new_conference_to_db(db: Session, data: ConferenceCreate) -> Conference:
    maintainer_ids = list(dict.fromkeys(data.reviewer_ids))
    track_reviewer_ids = [t.reviewer_id for t in data.tracks]
    all_reviewer_ids = list(dict.fromkeys(maintainer_ids + track_reviewer_ids))
    research_area_ids = list(dict.fromkeys(t.research_area_id for t in data.tracks))

    existing_reviewer_ids = set(
        db.scalars(
            select(Reviewer.reviewer_id).where(
                Reviewer.reviewer_id.in_(all_reviewer_ids)
            )
        ).all()
    )
    missing_reviewers = [
        rid for rid in all_reviewer_ids if rid not in existing_reviewer_ids
    ]
    if missing_reviewers:
        raise NotFoundError(f"Reviewers not found: {missing_reviewers}")

    existing_area_ids = set(
        db.scalars(
            select(ResearchArea.research_area_id).where(
                ResearchArea.research_area_id.in_(research_area_ids)
            )
        ).all()
    )
    missing_areas = [aid for aid in research_area_ids if aid not in existing_area_ids]
    if missing_areas:
        raise NotFoundError(f"Research areas not found: {missing_areas}")

    conference = Conference(
        **data.model_dump(exclude={"hosts", "reviewer_ids", "tracks"})
    )
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

        for reviewer_id in maintainer_ids:
            db.add(
                ReviewerMaintainsConference(
                    conference_id=conference.conference_id,
                    reviewer_id=reviewer_id,
                )
            )

        for track_data in data.tracks:
            db.add(
                Track(
                    conference_id=conference.conference_id,
                    name=track_data.name,
                    description=track_data.description,
                    research_area_id=track_data.research_area_id,
                    reviewer_id=track_data.reviewer_id,
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
    conference = db.get(Conference, conference_id)
    if not conference:
        raise NotFoundError("Conference not found.")
    return conference


def update_conference_in_db(
    db: Session, conference_id: int, data: ConferenceUpdate
) -> Conference:
    conference = db.get(Conference, conference_id)
    if not conference:
        raise NotFoundError("Conference not found.")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return conference

    hosts = updates.pop("hosts", None)

    for field, value in updates.items():
        setattr(conference, field, value)

    if conference.start_date > conference.end_date:
        raise ValueError("start_date cannot be after end_date.")

    if hosts is not None:
        _sync_conference_hosts(db, conference_id=conference_id, hosts=hosts)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Invalid conference data or constraint violation.") from None

    db.refresh(conference)
    return conference


def delete_conference_from_db(db: Session, conference_id: int) -> None:
    conference = db.get(Conference, conference_id)
    if not conference:
        raise NotFoundError("Conference not found.")

    db.delete(conference)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Cannot delete conference due to active references or constraint violation."
        ) from None
