from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import Session as ConfSession
from app.modules.sessions.schemas import SessionCreate


def add_new_session_to_db(db: Session, data: SessionCreate) -> ConfSession:
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
