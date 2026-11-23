from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import Track


def get_all_tracks_from_db(db: Session, skip: int = 0, limit: int = 100) -> list[Track]:
    query = select(Track).order_by(Track.track_id).offset(skip).limit(limit)
    return list(db.scalars(query).all())


def get_track_by_id_from_db(db: Session, track_id: int) -> Track:
    track = db.scalar(select(Track).where(Track.track_id == track_id))
    if not track:
        raise NotFoundError("Track not found.")
    return track
