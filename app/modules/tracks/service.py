from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import Conference, ResearchArea, Reviewer, Track
from app.modules.tracks.schemas import TrackUpdate


def get_all_tracks_from_db(db: Session, skip: int = 0, limit: int = 100) -> list[Track]:
    query = select(Track).order_by(Track.track_id).offset(skip).limit(limit)
    return list(db.scalars(query).all())


def get_track_by_id_from_db(db: Session, track_id: int) -> Track:
    track = db.get(Track, track_id)
    if not track:
        raise NotFoundError("Track not found.")
    return track


def update_track_in_db(db: Session, track_id: int, data: TrackUpdate) -> Track:
    track = db.get(Track, track_id)
    if not track:
        raise NotFoundError("Track not found.")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return track

    if "research_area_id" in updates and not db.get(
        ResearchArea, updates["research_area_id"]
    ):
        raise NotFoundError("Research area not found.")

    if "conference_id" in updates and not db.get(Conference, updates["conference_id"]):
        raise NotFoundError("Conference not found.")

    if "reviewer_id" in updates and not db.get(Reviewer, updates["reviewer_id"]):
        raise NotFoundError("Reviewer not found.")

    for field, value in updates.items():
        setattr(track, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Invalid track update or constraint violation.") from None

    db.refresh(track)
    return track


def delete_track_from_db(db: Session, track_id: int) -> None:
    track = db.get(Track, track_id)
    if not track:
        raise NotFoundError("Track not found.")

    db.delete(track)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Cannot delete track due to active references or constraint violation."
        ) from None
