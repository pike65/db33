from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.database.models import AuthorHasPaper, Paper, Review, Reviewer
from app.modules.reviews.schemas import ReviewCreate, ReviewUpdate


def _check_reviewer_id(db: Session, reviewer_id: int) -> None:
    reviewer = db.scalar(select(Reviewer).where(Reviewer.reviewer_id == reviewer_id))
    if not reviewer:
        raise NotFoundError("Reviewer not found.")


def _check_paper_id(db: Session, paper_id: int) -> Paper:
    paper = db.scalar(select(Paper).where(Paper.paper_id == paper_id))
    if not paper:
        raise NotFoundError("Paper not found.")
    return paper


def _check_not_self_review(db: Session, reviewer_id: int, paper_id: int) -> None:
    is_author = db.scalar(
        select(AuthorHasPaper).where(
            AuthorHasPaper.paper_id == paper_id,
            AuthorHasPaper.author_id == reviewer_id,
        )
    )
    if is_author is not None:
        raise ValueError("A reviewer cannot review their own paper.")


def add_new_review_to_db(db: Session, data: ReviewCreate) -> Review:
    _check_reviewer_id(db, reviewer_id=data.reviewer_id)
    _check_paper_id(db, paper_id=data.paper_id)
    _check_not_self_review(db, reviewer_id=data.reviewer_id, paper_id=data.paper_id)

    review = Review(**data.model_dump())
    db.add(review)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(review)
    return review


def get_all_reviews_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> list[Review]:
    query = select(Review).order_by(Review.review_id).offset(skip).limit(limit)
    return list(db.scalars(query).all())


def get_review_by_id_from_db(db: Session, review_id: int) -> Review:
    review = db.get(Review, review_id)
    if not review:
        raise NotFoundError("Review not found.")
    return review


def update_review_in_db(db: Session, review_id: int, data: ReviewUpdate) -> Review:
    review = db.scalar(select(Review).where(Review.review_id == review_id))
    if not review:
        raise NotFoundError("Review not found.")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return review

    target_reviewer_id = updates.get("reviewer_id", review.reviewer_id)
    target_paper_id = updates.get("paper_id", review.paper_id)

    if "reviewer_id" in updates:
        _check_reviewer_id(db, reviewer_id=target_reviewer_id)
    if "paper_id" in updates:
        _check_paper_id(db, paper_id=target_paper_id)

    _check_not_self_review(db, reviewer_id=target_reviewer_id, paper_id=target_paper_id)

    for field, value in updates.items():
        setattr(review, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Invalid review update or constraint violation.") from None

    db.refresh(review)
    return review


def delete_review_from_db(db: Session, review_id: int) -> None:
    review = db.scalar(select(Review).where(Review.review_id == review_id))
    if not review:
        raise NotFoundError("Review not found.")

    db.delete(review)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Cannot delete review due to active references or constraint violation."
        ) from None
