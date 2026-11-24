import sys
from datetime import UTC, date, datetime

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database.db import Base, SessionLocal, engine
from app.database.models import (
    Author,
    AuthorHasPaper,
    AuthorResearchArea,
    Conference,
    ExpertiseArea,
    Host,
    Keyword,
    Paper,
    PaperVersion,
    ResearchArea,
    Review,
    Reviewer,
    ReviewerExpertiseArea,
    ReviewerMaintainsConference,
    Track,
    User,
)
from app.database.models import (
    Session as ConfSession,
)
from app.modules.areas.service import (
    EXPERTISE_AREAS,
    RESEARCH_AREAS,
    populate_areas_in_db,
)


def _load_areas(
    db: Session,
) -> tuple[dict[str, ResearchArea], dict[str, ExpertiseArea]]:
    ra_map = {r.label: r for r in db.scalars(select(ResearchArea)).all()}
    ea_map = {e.label: e for e in db.scalars(select(ExpertiseArea)).all()}
    missing = [x for x in RESEARCH_AREAS if x not in ra_map] + [
        x for x in EXPERTISE_AREAS if x not in ea_map
    ]
    if missing:
        raise SystemExit(
            "Research/expertise areas are missing. Populate them first: "
            "open /docs and call POST /populate-areas, then run the seed again."
        )
    return ra_map, ea_map


def seed_database(db: Session) -> None:
    existing = db.scalar(select(User).where(User.email == "arman.armanov@example.com"))
    if existing is not None:
        return

    # 1. Research areas & expertise areas (created via POST /populate-areas)
    ra_map, ea_map = _load_areas(db)
    ra_ai = ra_map["Machine Learning"]
    ra_db = ra_map["Databases"]
    ra_sec = ra_map["Cybersecurity"]

    ea_ml = ea_map["Applied AI"]
    ea_data = ea_map["Data Systems"]
    ea_db = ea_map["Databases"]
    ea_crypto = ea_map["Cloud & Infrastructure"]

    # 2. Users (12 total: 4 both roles, 4 author-only, 4 reviewer-only)
    u_arman = User(
        email="arman.armanov@example.com",
        first_name="Arman",
        last_name="Armanov",
        country="Kazakhstan",
        affiliation="Nazarbayev University",
        phone_number="+77010000001",
    )
    u_amina = User(
        email="amina.aminova@example.com",
        first_name="Amina",
        last_name="Aminova",
        country="Kazakhstan",
        affiliation="KBTU",
        phone_number="+77010000002",
    )
    u_dias = User(
        email="dias.serikov@example.com",
        first_name="Dias",
        last_name="Serikov",
        country="Kazakhstan",
        affiliation="AITU",
        phone_number="+77010000003",
    )
    u_dana = User(
        email="dana.nurlanova@example.com",
        first_name="Dana",
        last_name="Nurlanova",
        country="Kazakhstan",
        affiliation="Satbayev University",
        phone_number="+77010000004",
    )

    u_alikhan = User(
        email="alikhan.tolegen@example.com",
        first_name="Alikhan",
        last_name="Tolegen",
        country="Kazakhstan",
        affiliation="SDU University",
        phone_number="+77010000005",
    )
    u_madina = User(
        email="madina.kassenova@example.com",
        first_name="Madina",
        last_name="Kassenova",
        country="Kazakhstan",
        affiliation="MNU",
        phone_number="+77010000006",
    )
    u_timur = User(
        email="timur.akhmetov@example.com",
        first_name="Timur",
        last_name="Akhmetov",
        country="Kazakhstan",
        affiliation="IITU",
        phone_number="+77010000007",
    )
    u_aisulu = User(
        email="aisulu.omarova@example.com",
        first_name="Aisulu",
        last_name="Omarova",
        country="Kazakhstan",
        affiliation="KIMEP",
        phone_number="+77010000008",
    )

    u_rustem = User(
        email="rustem.bekov@example.com",
        first_name="Rustem",
        last_name="Bekov",
        country="Kazakhstan",
        affiliation="NU",
        phone_number="+77010000009",
    )
    u_saule = User(
        email="saule.karimova@example.com",
        first_name="Saule",
        last_name="Karimova",
        country="Kazakhstan",
        affiliation="KBTU",
        phone_number="+77010000010",
    )
    u_nurlan = User(
        email="nurlan.smagulov@example.com",
        first_name="Nurlan",
        last_name="Smagulov",
        country="Germany",
        affiliation="TU Munich",
        phone_number="+491510000011",
    )
    u_kamila = User(
        email="kamila.zhaksylyk@example.com",
        first_name="Kamila",
        last_name="Zhaksylyk",
        country="Germany",
        affiliation="TU Berlin",
        phone_number="+491510000012",
    )

    users = [
        u_arman,
        u_amina,
        u_dias,
        u_dana,
        u_alikhan,
        u_madina,
        u_timur,
        u_aisulu,
        u_rustem,
        u_saule,
        u_nurlan,
        u_kamila,
    ]
    db.add_all(users)
    db.flush()

    # 3. Authors & Reviewers
    a_arman = Author(author_id=u_arman.user_id, orcid="0000-0001-0000-0001")
    a_amina = Author(author_id=u_amina.user_id, orcid="0000-0001-0000-0002")
    a_dias = Author(author_id=u_dias.user_id, orcid="0000-0001-0000-0003")
    a_dana = Author(author_id=u_dana.user_id, orcid=None)
    a_alikhan = Author(author_id=u_alikhan.user_id, orcid="0000-0001-0000-0005")
    a_madina = Author(author_id=u_madina.user_id, orcid="0000-0001-0000-0006")
    a_timur = Author(author_id=u_timur.user_id, orcid=None)
    a_aisulu = Author(author_id=u_aisulu.user_id, orcid="0000-0001-0000-0008")
    db.add_all(
        [a_arman, a_amina, a_dias, a_dana, a_alikhan, a_madina, a_timur, a_aisulu]
    )

    r_arman = Reviewer(reviewer_id=u_arman.user_id, years_of_experience=5)
    r_amina = Reviewer(reviewer_id=u_amina.user_id, years_of_experience=4)
    r_dias = Reviewer(reviewer_id=u_dias.user_id, years_of_experience=3)
    r_dana = Reviewer(reviewer_id=u_dana.user_id, years_of_experience=6)
    r_rustem = Reviewer(reviewer_id=u_rustem.user_id, years_of_experience=8)
    r_saule = Reviewer(reviewer_id=u_saule.user_id, years_of_experience=2)
    r_nurlan = Reviewer(reviewer_id=u_nurlan.user_id, years_of_experience=7)
    r_kamila = Reviewer(reviewer_id=u_kamila.user_id, years_of_experience=4)
    db.add_all(
        [r_arman, r_amina, r_dias, r_dana, r_rustem, r_saule, r_nurlan, r_kamila]
    )
    db.flush()

    db.add_all(
        [
            AuthorResearchArea(
                author_id=a_amina.author_id, research_area_id=ra_ai.research_area_id
            ),
            AuthorResearchArea(
                author_id=a_arman.author_id, research_area_id=ra_db.research_area_id
            ),
            ReviewerExpertiseArea(
                reviewer_id=r_rustem.reviewer_id,
                expertise_area_id=ea_ml.expertise_area_id,
            ),
            ReviewerExpertiseArea(
                reviewer_id=r_dana.reviewer_id,
                expertise_area_id=ea_data.expertise_area_id,
            ),
            ReviewerExpertiseArea(
                reviewer_id=r_dana.reviewer_id,
                expertise_area_id=ea_db.expertise_area_id,
            ),
            ReviewerExpertiseArea(
                reviewer_id=r_saule.reviewer_id,
                expertise_area_id=ea_crypto.expertise_area_id,
            ),
        ]
    )

    # 4. Conferences (Astana + Berlin; Berlin has 0 papers)
    conf_astana = Conference(
        name="Astana Symposium on Computing",
        description="Annual computing conference in Astana.",
        acronym="ASC26",
        city="Astana",
        country="Kazakhstan",
        start_date=date(2026, 6, 10),
        end_date=date(2026, 6, 12),
        paper_submission_deadline=datetime(2026, 4, 15, 23, 59, tzinfo=UTC),
        paper_review_deadline=datetime(2026, 5, 15, 23, 59, tzinfo=UTC),
    )
    conf_berlin = Conference(
        name="Berlin Systems Workshop",
        description="Workshop on distributed systems in Berlin.",
        acronym="BSW26",
        city="Berlin",
        country="Germany",
        start_date=date(2026, 9, 20),
        end_date=date(2026, 9, 22),
        paper_submission_deadline=datetime(2026, 7, 1, 23, 59, tzinfo=UTC),
        paper_review_deadline=datetime(2026, 8, 1, 23, 59, tzinfo=UTC),
    )
    db.add_all([conf_astana, conf_berlin])
    db.flush()

    db.add_all(
        [
            Host(
                conference_id=conf_astana.conference_id,
                host_name="Nazarbayev University",
            ),
            Host(conference_id=conf_astana.conference_id, host_name="KBTU"),
            Host(conference_id=conf_berlin.conference_id, host_name="TU Berlin"),
            ReviewerMaintainsConference(
                conference_id=conf_astana.conference_id,
                reviewer_id=r_rustem.reviewer_id,
            ),
            ReviewerMaintainsConference(
                conference_id=conf_astana.conference_id,
                reviewer_id=r_dana.reviewer_id,
            ),
            ReviewerMaintainsConference(
                conference_id=conf_astana.conference_id,
                reviewer_id=r_nurlan.reviewer_id,
            ),
            ReviewerMaintainsConference(
                conference_id=conf_berlin.conference_id,
                reviewer_id=r_kamila.reviewer_id,
            ),
        ]
    )

    # 5. Tracks (including an empty track with 0 papers)
    track_ai = Track(
        name="Applied AI",
        description="Machine learning and intelligent systems.",
        research_area_id=ra_ai.research_area_id,
        conference_id=conf_astana.conference_id,
        reviewer_id=r_rustem.reviewer_id,
    )
    track_db = Track(
        name="Data Engineering",
        description="Relational and distributed storage engines.",
        research_area_id=ra_db.research_area_id,
        conference_id=conf_astana.conference_id,
        reviewer_id=r_dana.reviewer_id,
    )
    track_empty = Track(
        name="Empty Track",
        description="Track with no submitted papers.",
        research_area_id=ra_sec.research_area_id,
        conference_id=conf_astana.conference_id,
        reviewer_id=r_nurlan.reviewer_id,
    )
    track_berlin = Track(
        name="Berlin Systems Track",
        description="Track in Berlin conference with zero papers.",
        research_area_id=ra_db.research_area_id,
        conference_id=conf_berlin.conference_id,
        reviewer_id=r_kamila.reviewer_id,
    )
    db.add_all([track_ai, track_db, track_empty, track_berlin])
    db.flush()

    # 6. Sessions in Astana (including an empty session with 0 papers)
    sess_accepted = ConfSession(
        conference_id=conf_astana.conference_id,
        reviewer_id=r_rustem.reviewer_id,
        title="Keynote & Accepted Papers",
        room="A101",
        session_date=date(2026, 6, 10),
        start_time=datetime(2026, 6, 10, 9, 0, tzinfo=UTC),
        end_time=datetime(2026, 6, 10, 11, 0, tzinfo=UTC),
    )
    sess_empty_astana = ConfSession(
        conference_id=conf_astana.conference_id,
        reviewer_id=r_dana.reviewer_id,
        title="Open Discussion (Empty Session)",
        room="B202",
        session_date=date(2026, 6, 11),
        start_time=datetime(2026, 6, 11, 14, 0, tzinfo=UTC),
        end_time=datetime(2026, 6, 11, 15, 30, tzinfo=UTC),
    )
    db.add_all([sess_accepted, sess_empty_astana])
    db.flush()

    # 7. Papers (10 papers across all 5 statuses; accepted with & without session;
    #    withdrawn papers with Amina as corresponding author)
    papers_spec = [
        {
            "title": "Neural Query Cardinality Estimation",
            "abstract": "Machine learning models for join size estimation.",
            "status": "accepted",
            "submission_date": date(2026, 3, 10),
            "track_id": track_db.track_id,
            "session_id": sess_accepted.session_id,
            "keywords": ["databases", "cardinality"],
            "authors": [
                (a_arman.author_id, 1, True),
                (a_alikhan.author_id, 2, False),
            ],
            "versions": [
                (
                    1,
                    "/files/p1_v1.pdf",
                    datetime(2026, 3, 10, 12, 0, tzinfo=UTC),
                    "Initial",
                ),
                (
                    2,
                    "/files/p1_v2.pdf",
                    datetime(2026, 4, 1, 10, 0, tzinfo=UTC),
                    "Camera ready",
                ),
            ],
        },
        {
            "title": "Low-Latency Transformers on Edge Nodes",
            "abstract": "Quantized inference for constrained devices.",
            "status": "accepted",
            "submission_date": date(2026, 3, 12),
            "track_id": track_ai.track_id,
            "session_id": None,
            "keywords": ["transformers", "quantization"],
            "authors": [
                (a_madina.author_id, 1, True),
                (a_timur.author_id, 2, False),
            ],
            "versions": [
                (
                    1,
                    "/files/p2_v1.pdf",
                    datetime(2026, 3, 12, 15, 0, tzinfo=UTC),
                    "Initial",
                ),
            ],
        },
        {
            "title": "Adaptive B-Tree Compaction Under Skew",
            "abstract": "Reducing write amplification in skewed workloads.",
            "status": "under review",
            "submission_date": date(2026, 3, 15),
            "track_id": track_db.track_id,
            "session_id": None,
            "keywords": ["b-tree", "storage"],
            "authors": [
                (a_alikhan.author_id, 1, True),
                (a_aisulu.author_id, 2, False),
            ],
            "versions": [
                (
                    1,
                    "/files/p3_v1.pdf",
                    datetime(2026, 3, 15, 9, 30, tzinfo=UTC),
                    "Draft",
                ),
                (
                    3,
                    "/files/p3_v3.pdf",
                    datetime(2026, 4, 5, 18, 0, tzinfo=UTC),
                    "Revision",
                ),
            ],
        },
        {
            "title": "Graph Embeddings for Clinical Triage",
            "abstract": "Graph neural networks over patient histories.",
            "status": "submitted",
            "submission_date": date(2026, 3, 20),
            "track_id": track_ai.track_id,
            "session_id": None,
            "keywords": ["gnn", "healthcare"],
            "authors": [
                (a_timur.author_id, 1, True),
            ],
            "versions": [
                (
                    1,
                    "/files/p4_v1.pdf",
                    datetime(2026, 3, 20, 11, 0, tzinfo=UTC),
                    "Submitted",
                ),
            ],
        },
        {
            "title": "Naive Heuristics in Distributed Locks",
            "abstract": "Empirical study of lease timeouts.",
            "status": "rejected",
            "submission_date": date(2026, 3, 5),
            "track_id": track_db.track_id,
            "session_id": None,
            "keywords": ["distributed", "locks"],
            "authors": [
                (a_aisulu.author_id, 1, True),
            ],
            "versions": [
                (
                    1,
                    "/files/p5_v1.pdf",
                    datetime(2026, 3, 5, 14, 0, tzinfo=UTC),
                    "Initial",
                ),
            ],
        },
        {
            "title": "Withdrawn Study on Diffusion Priors",
            "abstract": "Preliminary experiments withdrawn by authors.",
            "status": "withdrawn",
            "submission_date": date(2026, 3, 18),
            "track_id": track_ai.track_id,
            "session_id": None,
            "keywords": ["diffusion", "priors"],
            "authors": [
                (a_amina.author_id, 1, True),
                (a_madina.author_id, 2, False),
            ],
            "versions": [
                (
                    1,
                    "/files/p6_v1.pdf",
                    datetime(2026, 3, 18, 16, 0, tzinfo=UTC),
                    "Initial",
                ),
            ],
        },
        {
            "title": "Second Withdrawn Paper by Amina",
            "abstract": "Merged into a broader journal manuscript.",
            "status": "withdrawn",
            "submission_date": date(2026, 3, 22),
            "track_id": track_ai.track_id,
            "session_id": None,
            "keywords": ["multimodal", "vision"],
            "authors": [
                (a_timur.author_id, 1, False),
                (a_amina.author_id, 2, True),
            ],
            "versions": [
                (
                    1,
                    "/files/p7_v1.pdf",
                    datetime(2026, 3, 22, 10, 15, tzinfo=UTC),
                    "v1",
                ),
                (
                    2,
                    "/files/p7_v2.pdf",
                    datetime(2026, 3, 28, 12, 30, tzinfo=UTC),
                    "v2",
                ),
            ],
        },
        {
            "title": "Vector Index Compression with Product Quantization",
            "abstract": "Memory-efficient nearest neighbor search.",
            "status": "accepted",
            "submission_date": date(2026, 3, 11),
            "track_id": track_db.track_id,
            "session_id": sess_accepted.session_id,
            "keywords": ["vector-search", "compression"],
            "authors": [
                (a_alikhan.author_id, 1, True),
            ],
            "versions": [
                (
                    1,
                    "/files/p8_v1.pdf",
                    datetime(2026, 3, 11, 8, 45, tzinfo=UTC),
                    "Initial",
                ),
            ],
        },
        {
            "title": "Contrastive Audio Representations",
            "abstract": "Self-supervised acoustic embeddings.",
            "status": "under review",
            "submission_date": date(2026, 3, 25),
            "track_id": track_ai.track_id,
            "session_id": None,
            "keywords": ["audio", "contrastive"],
            "authors": [
                (a_madina.author_id, 1, True),
            ],
            "versions": [
                (
                    1,
                    "/files/p9_v1.pdf",
                    datetime(2026, 3, 25, 13, 20, tzinfo=UTC),
                    "Initial",
                ),
            ],
        },
        {
            "title": "Columnar Scan Pushdown in Analytical Engines",
            "abstract": "Predicate pushdown for nested formats.",
            "status": "submitted",
            "submission_date": date(2026, 3, 29),
            "track_id": track_db.track_id,
            "session_id": None,
            "keywords": ["olap", "columnar"],
            "authors": [
                (a_aisulu.author_id, 1, True),
            ],
            "versions": [
                (
                    1,
                    "/files/p10_v1.pdf",
                    datetime(2026, 3, 29, 17, 0, tzinfo=UTC),
                    "Initial",
                ),
            ],
        },
    ]

    created_papers: list[Paper] = []
    for spec in papers_spec:
        paper = Paper(
            title=spec["title"],
            abstract=spec["abstract"],
            status=spec["status"],
            submission_date=spec["submission_date"],
            track_id=spec["track_id"],
            session_id=spec["session_id"],
        )
        db.add(paper)
        db.flush()
        created_papers.append(paper)

        for kw in spec["keywords"]:
            db.add(Keyword(paper_id=paper.paper_id, keyword=kw))

        for author_id, order, is_corr in spec["authors"]:
            db.add(
                AuthorHasPaper(
                    paper_id=paper.paper_id,
                    author_id=author_id,
                    author_order=order,
                    is_corresponding=is_corr,
                )
            )

        for ver_no, file_loc, up_dt, note in spec["versions"]:
            db.add(
                PaperVersion(
                    paper_id=paper.paper_id,
                    version_number=ver_no,
                    file_location=file_loc,
                    upload_datetime=up_dt,
                    note=note,
                )
            )

    p1, p2, p3, p4, p5, _p6, _p7, p8, p9, _p10 = created_papers

    # 8. Reviews (10 reviews; no self-reviews; r_saule has 0 reviews; varied counts)
    reviews = [
        Review(
            reviewer_id=r_rustem.reviewer_id,
            paper_id=p1.paper_id,
            overall_score=5,
            recommendation="accept",
            comments_for_authors="Strong experimental results.",
            confidential_comments="Solid paper for the session.",
            submission_date=date(2026, 4, 20),
        ),
        Review(
            reviewer_id=r_nurlan.reviewer_id,
            paper_id=p1.paper_id,
            overall_score=4,
            recommendation="accept",
            comments_for_authors="Clear methodology.",
            confidential_comments="Good fit.",
            submission_date=date(2026, 4, 21),
        ),
        Review(
            reviewer_id=r_kamila.reviewer_id,
            paper_id=p1.paper_id,
            overall_score=4,
            recommendation="accept",
            comments_for_authors="Helpful ablations.",
            confidential_comments="Consistent positive scores.",
            submission_date=date(2026, 4, 22),
        ),
        Review(
            reviewer_id=r_dana.reviewer_id,
            paper_id=p2.paper_id,
            overall_score=4,
            recommendation="accept",
            comments_for_authors="Practical edge benchmarks.",
            confidential_comments="Accepted.",
            submission_date=date(2026, 4, 23),
        ),
        Review(
            reviewer_id=r_nurlan.reviewer_id,
            paper_id=p2.paper_id,
            overall_score=5,
            recommendation="accept",
            comments_for_authors="Crisp writing.",
            confidential_comments="Strong accept.",
            submission_date=date(2026, 4, 24),
        ),
        Review(
            reviewer_id=r_rustem.reviewer_id,
            paper_id=p3.paper_id,
            overall_score=3,
            recommendation="accept",
            comments_for_authors="Clarify skew assumptions.",
            confidential_comments="Borderline positive.",
            submission_date=date(2026, 4, 25),
        ),
        Review(
            reviewer_id=r_kamila.reviewer_id,
            paper_id=p4.paper_id,
            overall_score=3,
            recommendation="reject",
            comments_for_authors="Cohort size is small.",
            confidential_comments="Needs more validation.",
            submission_date=date(2026, 4, 26),
        ),
        Review(
            reviewer_id=r_dana.reviewer_id,
            paper_id=p5.paper_id,
            overall_score=2,
            recommendation="reject",
            comments_for_authors="Baseline comparison missing.",
            confidential_comments="Reject.",
            submission_date=date(2026, 4, 27),
        ),
        Review(
            reviewer_id=r_nurlan.reviewer_id,
            paper_id=p8.paper_id,
            overall_score=4,
            recommendation="accept",
            comments_for_authors="Good recall-memory trade-off.",
            confidential_comments="Accept.",
            submission_date=date(2026, 4, 28),
        ),
        Review(
            reviewer_id=r_rustem.reviewer_id,
            paper_id=p9.paper_id,
            overall_score=3,
            recommendation="reject",
            comments_for_authors="Expand evaluation datasets.",
            confidential_comments="Weak on baselines.",
            submission_date=date(2026, 4, 29),
        ),
    ]
    db.add_all(reviews)
    db.commit()


def main() -> None:
    reset = "--reset" in sys.argv

    if reset:
        with engine.begin() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
        print("Database wiped.")

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        if reset:
            populate_areas_in_db(db)
        seed_database(db)
    print("Database seeded.")


if __name__ == "__main__":
    main()
