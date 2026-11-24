from sqlalchemy import (
    Float,
    Numeric,
    case,
    cast,
    distinct,
    func,
    literal,
    select,
    text,
    update,
)
from sqlalchemy.orm import Session, aliased

from app.database.db import Base, engine
from app.database.models import (
    Author,
    AuthorHasPaper,
    Conference,
    ExpertiseArea,
    Paper,
    PaperVersion,
    Review,
    Reviewer,
    ReviewerExpertiseArea,
    ReviewerMaintainsConference,
    Track,
    User,
)
from app.database.models import Session as ConfSession


def task_1_create_tables(db: Session) -> None:
    Base.metadata.create_all(bind=engine)
    db.commit()


def task_2_table_counts(db: Session) -> list[tuple[str, int]]:
    counts: list[tuple[str, int]] = []
    for table in Base.metadata.sorted_tables:
        cnt = db.scalar(select(func.count()).select_from(table)) or 0
        counts.append((table.name, int(cnt)))
    return counts


def task_3_1_update_arman_phone(
    db: Session,
    email: str = "arman.armanov@example.com",
    phone: str = "+77773414141",
):
    stmt = update(User).where(User.email == email).values(phone_number=phone)
    db.execute(stmt)
    db.commit()
    return stmt


def task_3_2_extend_review_deadlines(db: Session):
    stmt = update(Conference).values(
        paper_review_deadline=case(
            (
                Conference.city == "Astana",
                Conference.paper_review_deadline + text("interval '7 days'"),
            ),
            else_=Conference.paper_review_deadline + text("interval '3 days'"),
        )
    )
    db.execute(stmt)
    db.commit()
    return stmt


def task_4_1_delete_amina_withdrawn_papers(
    db: Session, email: str = "amina.aminova@example.com"
):
    amina_author_id = (
        select(Author.author_id).join(User).where(User.email == email).scalar_subquery()
    )
    withdrawn_with_amina_corr = (
        select(Paper.paper_id)
        .join(AuthorHasPaper, AuthorHasPaper.paper_id == Paper.paper_id)
        .where(
            Paper.status == "withdrawn",
            AuthorHasPaper.author_id == amina_author_id,
            AuthorHasPaper.is_corresponding.is_(True),
        )
    )
    paper_ids = list(db.scalars(withdrawn_with_amina_corr).all())
    stmt = None
    if paper_ids:
        stmt = select(Paper).where(Paper.paper_id.in_(paper_ids))
        papers_to_delete = list(db.scalars(stmt).all())
        for p in papers_to_delete:
            db.delete(p)
    db.commit()
    return stmt


def task_4_2_delete_empty_astana_sessions(db: Session, city: str = "Astana"):
    assigned_session_ids = select(Paper.session_id).where(Paper.session_id.is_not(None))
    astana_conf_ids = select(Conference.conference_id).where(Conference.city == city)
    stmt = select(ConfSession).where(
        ConfSession.conference_id.in_(astana_conf_ids),
        ConfSession.session_id.notin_(assigned_session_ids),
    )
    empty_sessions = list(db.scalars(stmt).all())
    for s in empty_sessions:
        db.delete(s)
    db.commit()
    return stmt


def task_5_1_accepted_papers(db: Session):
    stmt = (
        select(
            Paper.paper_id,
            Paper.title,
            (User.first_name + literal(" ") + User.last_name).label(
                "corresponding_author"
            ),
            User.email.label("corresponding_email"),
            Track.name.label("track_name"),
            Conference.conference_id,
            Conference.acronym,
        )
        .join(Track, Track.track_id == Paper.track_id)
        .join(Conference, Conference.conference_id == Track.conference_id)
        .join(
            AuthorHasPaper,
            (AuthorHasPaper.paper_id == Paper.paper_id)
            & (AuthorHasPaper.is_corresponding.is_(True)),
        )
        .join(Author, Author.author_id == AuthorHasPaper.author_id)
        .join(User, User.user_id == Author.author_id)
        .where(Paper.status == "accepted")
        .order_by(Paper.paper_id)
    )
    return stmt, db.execute(stmt).all()


def task_5_2_abstract_machine_learning(db: Session, phrase: str = "machine learning"):
    stmt = (
        select(Paper.paper_id, Paper.title)
        .where(Paper.abstract.ilike(f"%{phrase}%"))
        .order_by(Paper.paper_id)
    )
    return stmt, db.execute(stmt).all()


def task_5_3_paper_versions_desc(db: Session, paper_id: int):
    stmt = (
        select(
            PaperVersion.version_number,
            PaperVersion.file_location,
            PaperVersion.upload_datetime,
        )
        .where(PaperVersion.paper_id == paper_id)
        .order_by(PaperVersion.version_number.desc())
    )
    return stmt, db.execute(stmt).all()


def task_5_4_db_reviewers_in_conference(
    db: Session,
    conference_id: int,
    expertise_label: str = "Databases",
    min_years: int = 3,
):
    stmt = (
        select(
            Reviewer.reviewer_id,
            (User.first_name + literal(" ") + User.last_name).label("full_name"),
            User.email,
        )
        .distinct()
        .join(
            ReviewerMaintainsConference,
            ReviewerMaintainsConference.reviewer_id == Reviewer.reviewer_id,
        )
        .join(
            ReviewerExpertiseArea,
            ReviewerExpertiseArea.reviewer_id == Reviewer.reviewer_id,
        )
        .join(
            ExpertiseArea,
            ExpertiseArea.expertise_area_id == ReviewerExpertiseArea.expertise_area_id,
        )
        .join(User, User.user_id == Reviewer.reviewer_id)
        .where(
            ReviewerMaintainsConference.conference_id == conference_id,
            ExpertiseArea.label == expertise_label,
            Reviewer.years_of_experience >= min_years,
        )
        .order_by(Reviewer.reviewer_id)
    )
    return stmt, db.execute(stmt).all()


def task_6_1_track_stats(db: Session):
    stmt = (
        select(
            Track.track_id,
            Track.name,
            Track.conference_id,
            func.count(distinct(Paper.paper_id)).label("distinct_papers"),
            func.count(distinct(AuthorHasPaper.author_id)).label("distinct_authors"),
        )
        .outerjoin(Paper, Paper.track_id == Track.track_id)
        .outerjoin(AuthorHasPaper, AuthorHasPaper.paper_id == Paper.paper_id)
        .group_by(Track.track_id, Track.name, Track.conference_id)
        .order_by(Track.track_id)
    )
    return stmt, db.execute(stmt).all()


def task_6_2_reviewer_stats(db: Session):
    stmt = (
        select(
            Reviewer.reviewer_id,
            (User.first_name + literal(" ") + User.last_name).label("full_name"),
            func.count(Review.review_id).label("review_count"),
            func.avg(Review.overall_score).label("avg_score"),
        )
        .join(User, User.user_id == Reviewer.reviewer_id)
        .outerjoin(Review, Review.reviewer_id == Reviewer.reviewer_id)
        .group_by(Reviewer.reviewer_id, User.first_name, User.last_name)
        .order_by(Reviewer.reviewer_id)
    )
    return stmt, db.execute(stmt).all()


def task_6_3_conference_stats(db: Session):
    stmt = (
        select(
            Conference.conference_id,
            Conference.acronym,
            func.count(distinct(Paper.paper_id)).label("total_papers"),
            func.count(
                distinct(case((Paper.status == "accepted", Paper.paper_id)))
            ).label("accepted_papers"),
            func.avg(Review.overall_score).label("avg_review_score"),
        )
        .outerjoin(Track, Track.conference_id == Conference.conference_id)
        .outerjoin(Paper, Paper.track_id == Track.track_id)
        .outerjoin(Review, Review.paper_id == Paper.paper_id)
        .group_by(Conference.conference_id, Conference.acronym)
        .order_by(Conference.conference_id)
    )
    return stmt, db.execute(stmt).all()


def task_6_4_above_average_reviewers(db: Session):
    per_reviewer_counts = (
        select(
            Reviewer.reviewer_id.label("reviewer_id"),
            (User.first_name + literal(" ") + User.last_name).label("full_name"),
            func.count(Review.review_id).label("review_count"),
        )
        .join(User, User.user_id == Reviewer.reviewer_id)
        .outerjoin(Review, Review.reviewer_id == Reviewer.reviewer_id)
        .group_by(Reviewer.reviewer_id, User.first_name, User.last_name)
        .cte("per_reviewer_counts")
    )
    overall_avg = select(
        func.avg(cast(per_reviewer_counts.c.review_count, Float))
    ).scalar_subquery()
    stmt = (
        select(
            per_reviewer_counts.c.reviewer_id,
            per_reviewer_counts.c.full_name,
            per_reviewer_counts.c.review_count,
            overall_avg.label("overall_avg_reviews"),
        )
        .where(cast(per_reviewer_counts.c.review_count, Float) > overall_avg)
        .order_by(per_reviewer_counts.c.reviewer_id)
    )
    return stmt, db.execute(stmt).all()


def task_7_acceptance_rate(db: Session):
    accepted_cnt = func.count(case((Paper.status == "accepted", 1)))
    rejected_cnt = func.count(case((Paper.status == "rejected", 1)))
    denom = accepted_cnt + rejected_cnt
    rate = case(
        (
            denom > 0,
            func.round(
                cast(
                    100.0 * cast(accepted_cnt, Numeric) / cast(denom, Numeric),
                    Numeric,
                ),
                2,
            ),
        ),
        else_=None,
    )
    stmt = (
        select(
            Conference.conference_id,
            Conference.acronym,
            accepted_cnt.label("accepted_count"),
            rejected_cnt.label("rejected_count"),
            rate.label("acceptance_rate_pct"),
        )
        .outerjoin(Track, Track.conference_id == Conference.conference_id)
        .outerjoin(Paper, Paper.track_id == Track.track_id)
        .group_by(Conference.conference_id, Conference.acronym)
        .order_by(Conference.conference_id)
    )
    return stmt, db.execute(stmt).all()


def task_8_create_and_query_schedule_view(db: Session):
    _chair_user = aliased(User)
    _author_user = aliased(User)

    view_sql = text(
        """
        CREATE OR REPLACE VIEW accepted_paper_schedule AS
        SELECT
            p.paper_id,
            p.title AS paper_title,
            c.conference_id,
            c.acronym AS conference_acronym,
            t.name AS track_name,
            s.session_id,
            s.title AS session_title,
            s.session_date,
            s.start_time,
            s.end_time,
            s.room AS room_label,
            (cu.first_name || ' ' || cu.last_name) AS chair_name,
            (au.first_name || ' ' || au.last_name) AS corresponding_author_name,
            au.email AS corresponding_author_email
        FROM papers p
        JOIN tracks t ON t.track_id = p.track_id
        JOIN conferences c ON c.conference_id = t.conference_id
        JOIN sessions s ON s.session_id = p.session_id
        JOIN reviewers r ON r.reviewer_id = s.reviewer_id
        JOIN users cu ON cu.user_id = r.reviewer_id
        JOIN author_papers ahp ON ahp.paper_id = p.paper_id AND ahp.is_corresponding = TRUE
        JOIN authors a ON a.author_id = ahp.author_id
        JOIN users au ON au.user_id = a.author_id
        WHERE p.status = 'accepted'
          AND p.session_id IS NOT NULL;
        """
    )
    db.execute(view_sql)
    db.commit()

    query_sql = text(
        """
        SELECT *
        FROM accepted_paper_schedule
        ORDER BY conference_id, session_date, start_time, session_id, paper_id;
        """
    )
    return query_sql, db.execute(query_sql).all()
