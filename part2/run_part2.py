import sys
from contextlib import redirect_stdout
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.dialects import postgresql

from app.database.seed import seed_database
from app.database.db import SessionLocal
from app.database.models import (
    AuthorHasPaper,
    AuthorResearchArea,
    Conference,
    Host,
    Keyword,
    Paper,
    PaperVersion,
    ReviewerExpertiseArea,
    ReviewerMaintainsConference,
    Track,
    User,
)
from app.database.models import Session as ConfSession
from part2 import queries


class _Tee:
    def __init__(self, *streams):
        self._streams = streams

    def write(self, data: str) -> int:
        for s in self._streams:
            s.write(data)
            s.flush()
        return len(data)

    def flush(self) -> None:
        for s in self._streams:
            s.flush()


def _compile_sql(stmt) -> str:
    if hasattr(stmt, "compile"):
        return str(
            stmt.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": False},
            )
        )
    return str(stmt)


def _reset_to_seed(db) -> None:
    db.execute(delete(PaperVersion))
    db.execute(delete(Keyword))
    db.execute(delete(AuthorHasPaper))
    db.execute(delete(Paper))
    db.execute(delete(ConfSession))
    db.execute(delete(Track))
    db.execute(delete(ReviewerMaintainsConference))
    db.execute(delete(Host))
    db.execute(delete(Conference))
    db.execute(delete(ReviewerExpertiseArea))
    db.execute(delete(AuthorResearchArea))
    db.execute(delete(User))
    db.commit()
    seed_database(db)


def _run_all_tasks():
    with SessionLocal() as db:
        print("=== Task 1: Create tables ===")
        queries.task_1_create_tables(db)
        _reset_to_seed(db)

        print("\n=== Task 2: Row counts ===")
        for table_name, cnt in queries.task_2_table_counts(db):
            print(f"  {table_name}: {cnt}")

        print("\n=== Task 3.1: Update Arman's phone ===")
        before_arman = db.scalar(
            select(User.phone_number).where(User.email == "arman.armanov@example.com")
        )
        print("Before:", before_arman)
        stmt_3_1 = queries.task_3_1_update_arman_phone(db)
        print("SQL:", _compile_sql(stmt_3_1))
        after_arman = db.scalar(
            select(User.phone_number).where(User.email == "arman.armanov@example.com")
        )
        print("After:", after_arman)
        _reset_to_seed(db)

        print("\n=== Task 3.2: Extend conference review deadlines ===")
        before_confs = db.execute(
            select(
                Conference.acronym,
                Conference.city,
                Conference.paper_review_deadline,
            )
        ).all()
        print("Before:", before_confs)
        stmt_3_2 = queries.task_3_2_extend_review_deadlines(db)
        print("SQL:", _compile_sql(stmt_3_2))
        after_confs = db.execute(
            select(
                Conference.acronym,
                Conference.city,
                Conference.paper_review_deadline,
            )
        ).all()
        print("After:", after_confs)
        _reset_to_seed(db)

        print("\n=== Task 4.1: Delete Amina's withdrawn papers ===")
        print("Papers before:", len(db.scalars(select(Paper)).all()))
        stmt_4_1 = queries.task_4_1_delete_amina_withdrawn_papers(db)
        if stmt_4_1 is not None:
            print("SQL:", _compile_sql(stmt_4_1))
        print("Papers after:", len(db.scalars(select(Paper)).all()))
        _reset_to_seed(db)

        print("\n=== Task 4.2: Delete empty Astana sessions ===")
        print("Sessions before:", len(db.scalars(select(ConfSession)).all()))
        stmt_4_2 = queries.task_4_2_delete_empty_astana_sessions(db)
        if stmt_4_2 is not None:
            print("SQL:", _compile_sql(stmt_4_2))
        print("Sessions after:", len(db.scalars(select(ConfSession)).all()))
        _reset_to_seed(db)

        first_paper_id = db.scalar(
            select(Paper.paper_id).order_by(Paper.paper_id).limit(1)
        )
        astana_conf_id = db.scalar(
            select(Conference.conference_id).where(Conference.city == "Astana").limit(1)
        )

        for label, fn in [
            ("Task 5.1", lambda s: queries.task_5_1_accepted_papers(s)),
            ("Task 5.2", lambda s: queries.task_5_2_abstract_machine_learning(s)),
            (
                "Task 5.3",
                lambda s: queries.task_5_3_paper_versions_desc(
                    s, paper_id=first_paper_id
                ),
            ),
            (
                "Task 5.4",
                lambda s: queries.task_5_4_db_reviewers_in_conference(
                    s, conference_id=astana_conf_id
                ),
            ),
            ("Task 6.1", lambda s: queries.task_6_1_track_stats(s)),
            ("Task 6.2", lambda s: queries.task_6_2_reviewer_stats(s)),
            ("Task 6.3", lambda s: queries.task_6_3_conference_stats(s)),
            ("Task 6.4", lambda s: queries.task_6_4_above_average_reviewers(s)),
            ("Task 7", lambda s: queries.task_7_acceptance_rate(s)),
            ("Task 8", lambda s: queries.task_8_create_and_query_schedule_view(s)),
        ]:
            stmt, rows = fn(db)
            print(f"\n=== {label} ===")
            print("SQL:", _compile_sql(stmt))
            for r in rows:
                print(" ", dict(r._mapping))


def main() -> None:
    output_path = Path("part2_output.txt")
    with output_path.open("w", encoding="utf-8") as f:
        tee = _Tee(sys.stdout, f)
        with redirect_stdout(tee):
            _run_all_tasks()


if __name__ == "__main__":
    main()
