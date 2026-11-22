from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


# -------------------- users -------------------- #
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))
    affiliation: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(100), unique=True)

    # Relationships
    author_profile: Mapped[Author | None] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reviewer_profile: Mapped[Reviewer | None] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Author(Base):
    __tablename__ = "authors"

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    orcid: Mapped[str | None] = mapped_column(String(19), nullable=True)

    # Relationships
    user: Mapped[User] = relationship(back_populates="author_profile")
    author_research_area: Mapped[list[AuthorResearchArea]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )


class AuthorResearchArea(Base):
    __tablename__ = "author_research_areas"

    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.author_id", ondelete="CASCADE"), primary_key=True
    )
    research_area_id: Mapped[int] = mapped_column(
        ForeignKey("research_areas.research_area_id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    author: Mapped[Author] = relationship(back_populates="author_research_area")
    research_area: Mapped[ResearchArea] = relationship(
        back_populates="author_research_area"
    )


class ResearchArea(Base):
    __tablename__ = "research_areas"

    research_area_id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(100), unique=True)

    # Relationships
    author_research_area: Mapped[list[AuthorResearchArea]] = relationship(
        back_populates="research_area"
    )


class Reviewer(Base):
    __tablename__ = "reviewers"

    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    years_of_experience: Mapped[int] = mapped_column(Integer)

    __table_args__ = (
        CheckConstraint(
            "years_of_experience >= 0",
            name="check_if_xp_years_is_nonnegative",
        ),
    )

    # Relationships
    user: Mapped[User] = relationship(back_populates="reviewer_profile")
    reviewer_expertise_area: Mapped[list[ReviewerExpertiseArea]] = relationship(
        back_populates="reviewer", cascade="all, delete-orphan"
    )


class ReviewerExpertiseArea(Base):
    __tablename__ = "reviewer_expertise_areas"

    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("reviewers.reviewer_id", ondelete="CASCADE"),
        primary_key=True,
    )
    expertise_area_id: Mapped[int] = mapped_column(
        ForeignKey("expertise_areas.expertise_area_id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    reviewer: Mapped[Reviewer] = relationship(back_populates="reviewer_expertise_area")
    expertise_area: Mapped[ExpertiseArea] = relationship(
        back_populates="reviewer_expertise_area"
    )


class ExpertiseArea(Base):
    __tablename__ = "expertise_areas"

    expertise_area_id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(100), unique=True)

    # Relationships
    reviewer_expertise_area: Mapped[list[ReviewerExpertiseArea]] = relationship(
        back_populates="expertise_area"
    )


# -------------------- conferences -------------------- #
class Conference(Base):
    __tablename__ = "conferences"

    conference_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    acronym: Mapped[str] = mapped_column(String(20))
    city: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))

    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)

    paper_submission_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    paper_review_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("start_date < end_date", name="check_start_earlier_than_end"),
    )

    # Relationships
    hosts: Mapped[list[Host]] = relationship(
        back_populates="conference", cascade="all, delete-orphan"
    )


class Host(Base):
    __tablename__ = "hosts"

    conference_id: Mapped[int] = mapped_column(
        ForeignKey("conferences.conference_id", ondelete="CASCADE"), primary_key=True
    )
    host_name: Mapped[str] = mapped_column(String(100), primary_key=True)

    # Relationships
    conference: Mapped[Conference] = relationship(back_populates="hosts")


# -------------------- papers -------------------- #
