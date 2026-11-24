from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidAreaError, NotFoundError
from app.database.models import (
    Author,
    AuthorResearchArea,
    ExpertiseArea,
    ResearchArea,
    Reviewer,
    ReviewerExpertiseArea,
    User,
)
from app.modules.users.schemas import (
    AuthorUpdate,
    ReviewerUpdate,
    UserCreate,
    UserUpdate,
)


def _validate_area_ids(
    db: Session, model: type[ResearchArea | ExpertiseArea], id_col, ids: list[int]
) -> None:
    if not ids:
        return
    unique_ids = set(ids)
    found_ids = set(db.scalars(select(id_col).where(id_col.in_(unique_ids))).all())
    missing = unique_ids - found_ids
    if missing:
        raise InvalidAreaError(
            f"Unknown area IDs for {model.__tablename__}: {sorted(missing)}"
        )


def _sync_author_research_areas(
    db: Session, author_id: int, research_area_ids: list[int]
) -> None:
    unique_ids = list(dict.fromkeys(research_area_ids))
    if unique_ids:
        found_ids = set(
            db.scalars(
                select(ResearchArea.research_area_id).where(
                    ResearchArea.research_area_id.in_(unique_ids)
                )
            ).all()
        )
        missing = [area_id for area_id in unique_ids if area_id not in found_ids]
        if missing:
            raise ValueError(f"Unknown research_area_id(s): {missing}.")

    db.execute(
        delete(AuthorResearchArea).where(AuthorResearchArea.author_id == author_id)
    )
    for area_id in unique_ids:
        db.add(AuthorResearchArea(author_id=author_id, research_area_id=area_id))


def _sync_reviewer_expertise_areas(
    db: Session, reviewer_id: int, expertise_area_ids: list[int]
) -> None:
    unique_ids = list(dict.fromkeys(expertise_area_ids))
    if unique_ids:
        found_ids = set(
            db.scalars(
                select(ExpertiseArea.expertise_area_id).where(
                    ExpertiseArea.expertise_area_id.in_(unique_ids)
                )
            ).all()
        )
        missing = [area_id for area_id in unique_ids if area_id not in found_ids]
        if missing:
            raise ValueError(f"Unknown expertise_area_id(s): {missing}.")

    db.execute(
        delete(ReviewerExpertiseArea).where(
            ReviewerExpertiseArea.reviewer_id == reviewer_id
        )
    )
    for area_id in unique_ids:
        db.add(
            ReviewerExpertiseArea(reviewer_id=reviewer_id, expertise_area_id=area_id)
        )


def create_user_with_specializations(db: Session, data: UserCreate) -> User:
    if data.author is not None:
        _validate_area_ids(
            db,
            ResearchArea,
            ResearchArea.research_area_id,
            data.author.research_area_ids,
        )
    if data.reviewer is not None:
        _validate_area_ids(
            db,
            ExpertiseArea,
            ExpertiseArea.expertise_area_id,
            data.reviewer.expertise_area_ids,
        )

    user_data = data.model_dump(exclude={"author", "reviewer"})
    user = User(**user_data)
    db.add(user)

    try:
        db.flush()

        if data.author is not None:
            author = Author(author_id=user.user_id, orcid=data.author.orcid)
            db.add(author)
            for area_id in set(data.author.research_area_ids):
                db.add(
                    AuthorResearchArea(
                        author_id=user.user_id,
                        research_area_id=area_id,
                    )
                )

        if data.reviewer is not None:
            reviewer = Reviewer(
                reviewer_id=user.user_id,
                years_of_experience=data.reviewer.years_of_experience,
            )
            db.add(reviewer)
            for area_id in set(data.reviewer.expertise_area_ids):
                db.add(
                    ReviewerExpertiseArea(
                        reviewer_id=user.user_id,
                        expertise_area_id=area_id,
                    )
                )

        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(user)
    return user


def get_all_users_from_db(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    query = select(User).order_by(User.user_id).offset(skip).limit(limit)
    return list(db.scalars(query).all())


def get_user_by_id_from_db(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found.")
    return user


def update_user_in_db(db: Session, user_id: int, data: UserUpdate) -> User:
    user = db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found.")

    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)

    if not updates:
        return user

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "A user with this email or phone number already exists."
        ) from None

    db.refresh(user)
    return user


def update_author_in_db(db: Session, author_id: int, data: AuthorUpdate) -> Author:
    author = db.get(Author, author_id)
    if not author:
        raise NotFoundError("Author not found.")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return author

    research_area_ids = updates.pop("research_area_ids", None)

    for field, value in updates.items():
        setattr(author, field, value)

    if research_area_ids is not None:
        _sync_author_research_areas(
            db, author_id=author_id, research_area_ids=research_area_ids
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("An author with this ORCID already exists.") from None

    db.refresh(author)
    return author


def update_reviewer_in_db(
    db: Session, reviewer_id: int, data: ReviewerUpdate
) -> Reviewer:
    reviewer = db.get(Reviewer, reviewer_id)
    if not reviewer:
        raise NotFoundError("Reviewer not found.")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return reviewer

    expertise_area_ids = updates.pop("expertise_area_ids", None)

    for field, value in updates.items():
        setattr(reviewer, field, value)

    if expertise_area_ids is not None:
        _sync_reviewer_expertise_areas(
            db, reviewer_id=reviewer_id, expertise_area_ids=expertise_area_ids
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Could not update reviewer due to invalid reference."
        ) from None

    db.refresh(reviewer)
    return reviewer


def delete_user_from_db(db: Session, user_id: int) -> None:
    user = db.get(User, user_id)
    if not user:
        raise NotFoundError("User not found.")

    db.delete(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Cannot delete user because they are referenced by active records "
            "(such as coordinated tracks or chaired sessions)."
        ) from None


def delete_author_from_db(db: Session, author_id: int) -> None:
    author = db.get(Author, author_id)
    if not author:
        raise NotFoundError("Author profile not found.")

    if author.user.reviewer_profile is None:
        raise ValueError(
            "Cannot delete author profile because the user must remain at least an author or a reviewer."
        )

    db.delete(author)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Cannot delete author profile due to active references."
        ) from None


def delete_reviewer_from_db(db: Session, reviewer_id: int) -> None:
    reviewer = db.get(Reviewer, reviewer_id)
    if not reviewer:
        raise NotFoundError("Reviewer profile not found.")

    if reviewer.user.author_profile is None:
        raise ValueError(
            "Cannot delete reviewer profile because the user must remain at least an author or a reviewer."
        )

    db.delete(reviewer)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Cannot delete reviewer profile because they are still referenced (such as coordinating tracks or chairing sessions)."
        ) from None
