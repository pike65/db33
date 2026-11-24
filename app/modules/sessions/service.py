from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import Conference, Reviewer
from app.database.models import Session as ConfSession
from app.modules.sessions.schemas import SessionCreate, SessionUpdate


def _check_conference_id(db: Session, conference_id: int) -> None:
    conference = db.scalar(
        select(Conference).where(Conference.conference_id == conference_id)
    )
    if not conference:
        raise NotFoundError("Conference not found.")


def _check_reviewer_id(db: Session, reviewer_id: int) -> None:
    reviewer = db.scalar(select(Reviewer).where(Reviewer.reviewer_id == reviewer_id))
    if not reviewer:
        raise NotFoundError("Reviewer not found.")


def add_new_session_to_db(db: Session, data: SessionCreate) -> ConfSession:
    conference_id, reviewer_id = data.conference_id, data.reviewer_id
    _check_conference_id(db, conference_id=conference_id)
    _check_reviewer_id(db, reviewer_id=reviewer_id)

    session = ConfSession(**data.model_dump())
    db.add(session)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(session)
    return session


def get_all_sessions_from_db(db: Session, skip: int, limit: int) -> list[ConfSession]:
    query = (
        select(ConfSession).order_by(ConfSession.session_id).offset(skip).limit(limit)
    )
    return list(db.scalars(query).all())


def get_session_by_id_from_db(db: Session, session_id: int) -> ConfSession:
    session = db.get(ConfSession, session_id)
    if not session:
        raise NotFoundError("Session not found.")
    return session


def update_session_in_db(
    db: Session, session_id: int, data: SessionUpdate
) -> ConfSession:
    session = db.get(ConfSession, session_id)
    if not session:
        raise NotFoundError("Session not found.")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return session

    if "conference_id" in updates:
        _check_conference_id(db, conference_id=updates["conference_id"])

    if "reviewer_id" in updates:
        _check_reviewer_id(db, reviewer_id=updates["reviewer_id"])

    for field, value in updates.items():
        setattr(session, field, value)

    if session.start_time >= session.end_time:
        raise ValueError("start_time must be earlier than end_time.")

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Invalid session update or constraint violation.") from None

    db.refresh(session)
    return session


def delete_session_from_db(db: Session, session_id: int) -> None:
    session = db.get(ConfSession, session_id)
    if not session:
        raise NotFoundError("Session not found.")

    db.delete(session)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Cannot delete session due to active references or constraint violation."
        ) from None
