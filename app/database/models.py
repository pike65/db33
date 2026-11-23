from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


# -------------------- users -------------------- #
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    affiliation: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

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
    author_research_areas: Mapped[list[AuthorResearchArea]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    authored_papers: Mapped[list[AuthorHasPaper]] = relationship(
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
    author: Mapped[Author] = relationship(back_populates="author_research_areas")
    research_area: Mapped[ResearchArea] = relationship(
        back_populates="author_research_areas"
    )


class ResearchArea(Base):
    __tablename__ = "research_areas"

    research_area_id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relationships
    author_research_areas: Mapped[list[AuthorResearchArea]] = relationship(
        back_populates="research_area", cascade="all, delete-orphan"
    )
    tracks: Mapped[list[Track]] = relationship(
        back_populates="research_area", cascade="all, delete-orphan"
    )


class Reviewer(Base):
    __tablename__ = "reviewers"

    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    years_of_experience: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "years_of_experience >= 0",
            name="check_if_xp_years_is_nonnegative",
        ),
    )

    # Relationships
    user: Mapped[User] = relationship(back_populates="reviewer_profile")
    reviewer_expertise_areas: Mapped[list[ReviewerExpertiseArea]] = relationship(
        back_populates="reviewer", cascade="all, delete-orphan"
    )
    maintained_conferences: Mapped[list[ReviewerMaintainsConference]] = relationship(
        back_populates="reviewer", cascade="all, delete-orphan"
    )
    chairs_sessions: Mapped[list[Session]] = relationship(
        back_populates="reviewer", cascade="all, delete-orphan"
    )
    coordinated_tracks: Mapped[list[Track]] = relationship(
        back_populates="reviewer", cascade="all, delete-orphan"
    )
    submitted_reviews: Mapped[list[Review]] = relationship(
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
    reviewer: Mapped[Reviewer] = relationship(back_populates="reviewer_expertise_areas")
    expertise_area: Mapped[ExpertiseArea] = relationship(
        back_populates="reviewer_expertise_areas"
    )


class ExpertiseArea(Base):
    __tablename__ = "expertise_areas"

    expertise_area_id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relationships
    reviewer_expertise_areas: Mapped[list[ReviewerExpertiseArea]] = relationship(
        back_populates="expertise_area", cascade="all, delete-orphan"
    )


# -------------------- conferences -------------------- #
class Conference(Base):
    __tablename__ = "conferences"

    conference_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    acronym: Mapped[str] = mapped_column(String(20), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    paper_submission_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    paper_review_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        CheckConstraint("start_date <= end_date", name="check_start_not_after_end"),
    )

    # Relationships
    hosts: Mapped[list[Host]] = relationship(
        back_populates="conference", cascade="all, delete-orphan"
    )
    maintaining_reviewers: Mapped[list[ReviewerMaintainsConference]] = relationship(
        back_populates="conference", cascade="all, delete-orphan"
    )
    holds_sessions: Mapped[list[Session]] = relationship(
        back_populates="conference", cascade="all, delete-orphan"
    )
    has_tracks: Mapped[list[Track]] = relationship(
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


# -------------------- sessions -------------------- #
class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[int] = mapped_column(primary_key=True)
    conference_id: Mapped[int] = mapped_column(
        ForeignKey("conferences.conference_id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("reviewers.reviewer_id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    room: Mapped[str] = mapped_column(String(10), nullable=False)

    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint("start_time < end_time", name="check_start_earlier_than_end"),
    )

    # Relationships
    conference: Mapped[Conference] = relationship(back_populates="holds_sessions")
    reviewer: Mapped[Reviewer] = relationship(back_populates="chairs_sessions")
    assigned_papers: Mapped[list[Paper]] = relationship(back_populates="session")


# -------------------- tracks -------------------- #
class Track(Base):
    __tablename__ = "tracks"

    track_id: Mapped[int] = mapped_column(primary_key=True)
    research_area_id: Mapped[int] = mapped_column(
        ForeignKey("research_areas.research_area_id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    conference_id: Mapped[int] = mapped_column(
        ForeignKey("conferences.conference_id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("reviewers.reviewer_id", ondelete="CASCADE"),
        nullable=False,
    )

    # Relationships
    research_area: Mapped[ResearchArea] = relationship(back_populates="tracks")
    conference: Mapped[Conference] = relationship(back_populates="has_tracks")
    reviewer: Mapped[Reviewer] = relationship(back_populates="coordinated_tracks")
    papers: Mapped[list[Paper]] = relationship(
        back_populates="track", cascade="all, delete-orphan"
    )


# -------------------- papers -------------------- #
class Paper(Base):
    __tablename__ = "papers"

    paper_id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(
        ForeignKey("tracks.track_id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="SET NULL"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    abstract: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="submitted", nullable=False)
    submission_date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('submitted', 'under review', 'accepted', 'rejected', 'withdrawn')",
            name="check_paper_status",
        ),
    )

    # Relationships
    track: Mapped[Track] = relationship(back_populates="papers")
    session: Mapped[Session | None] = relationship(back_populates="assigned_papers")
    keywords: Mapped[list[Keyword]] = relationship(
        back_populates="paper", cascade="all, delete-orphan"
    )
    authors: Mapped[list[AuthorHasPaper]] = relationship(
        back_populates="paper", cascade="all, delete-orphan"
    )
    versions: Mapped[list[PaperVersion]] = relationship(
        back_populates="paper", cascade="all, delete-orphan"
    )
    reviews: Mapped[list[Review]] = relationship(
        back_populates="paper", cascade="all, delete-orphan"
    )


class Keyword(Base):
    __tablename__ = "keywords"

    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.paper_id", ondelete="CASCADE"), primary_key=True
    )
    keyword: Mapped[str] = mapped_column(String(100), primary_key=True)

    # Relationships
    paper: Mapped[Paper] = relationship(back_populates="keywords")


class PaperVersion(Base):
    __tablename__ = "paper_versions"

    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.paper_id", ondelete="CASCADE"), primary_key=True
    )
    version_number: Mapped[int] = mapped_column(Integer, primary_key=True)

    file_location: Mapped[str] = mapped_column(String(500), nullable=False)
    upload_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        CheckConstraint("version_number >= 1", name="check_version_number_positive"),
    )

    # Relationships
    paper: Mapped[Paper] = relationship(back_populates="versions")


# -------------------- reviews -------------------- #
class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[int] = mapped_column(primary_key=True)
    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("reviewers.reviewer_id", ondelete="CASCADE"),
        nullable=False,
    )
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.paper_id", ondelete="CASCADE"),
        nullable=False,
    )

    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(50), nullable=False)

    comments_for_authors: Mapped[str] = mapped_column(String(500), nullable=False)
    confidential_comments: Mapped[str] = mapped_column(String(500), nullable=False)

    submission_date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "overall_score >= 1 AND overall_score <= 5",
            name="check_overall_score",
        ),
        CheckConstraint(
            "recommendation IN ('accept', 'reject')",
            name="check_recommendation",
        ),
        UniqueConstraint("reviewer_id", "paper_id", name="uq_review_reviewer_paper"),
    )

    # Relationships
    reviewer: Mapped[Reviewer] = relationship(back_populates="submitted_reviews")
    paper: Mapped[Paper] = relationship(back_populates="reviews")


# -------------------- junction tables -------------------- #
class ReviewerMaintainsConference(Base):
    __tablename__ = "maintained_conferences"

    reviewer_id: Mapped[int] = mapped_column(
        ForeignKey("reviewers.reviewer_id", ondelete="CASCADE"), primary_key=True
    )
    conference_id: Mapped[int] = mapped_column(
        ForeignKey("conferences.conference_id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    reviewer: Mapped[Reviewer] = relationship(back_populates="maintained_conferences")
    conference: Mapped[Conference] = relationship(
        back_populates="maintaining_reviewers"
    )


class AuthorHasPaper(Base):
    __tablename__ = "author_papers"

    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.author_id", ondelete="CASCADE"), primary_key=True
    )
    paper_id: Mapped[int] = mapped_column(
        ForeignKey("papers.paper_id", ondelete="CASCADE"), primary_key=True
    )
    author_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_corresponding: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    __table_args__ = (
        CheckConstraint("author_order >= 1", name="check_author_order_positive"),
        UniqueConstraint("paper_id", "author_order", name="uq_paper_author_order"),
    )

    # Relationships
    author: Mapped[Author] = relationship(back_populates="authored_papers")
    paper: Mapped[Paper] = relationship(back_populates="authors")
