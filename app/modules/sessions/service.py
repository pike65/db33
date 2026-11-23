from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import Conference, Reviewer
from app.database.models import Session as ConfSession
from app.modules.sessions.schemas import SessionCreate


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
    session = db.scalar(select(ConfSession).where(ConfSession.session_id == session_id))
    if not session:
        raise NotFoundError("Session not found.")
    return session
