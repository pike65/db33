--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: author_papers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.author_papers (
    author_id integer NOT NULL,
    paper_id integer NOT NULL,
    author_order integer NOT NULL,
    is_corresponding boolean NOT NULL,
    CONSTRAINT check_author_order_positive CHECK ((author_order >= 1))
);


--
-- Name: authors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.authors (
    author_id integer NOT NULL,
    orcid character varying(19)
);


--
-- Name: conferences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conferences (
    conference_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500) NOT NULL,
    acronym character varying(20) NOT NULL,
    city character varying(100) NOT NULL,
    country character varying(100) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    paper_submission_deadline timestamp with time zone NOT NULL,
    paper_review_deadline timestamp with time zone NOT NULL,
    CONSTRAINT check_start_not_after_end CHECK ((start_date <= end_date))
);


--
-- Name: papers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.papers (
    paper_id integer NOT NULL,
    track_id integer NOT NULL,
    session_id integer,
    title character varying(500) NOT NULL,
    abstract character varying(500) NOT NULL,
    status character varying(50) NOT NULL,
    submission_date date NOT NULL,
    CONSTRAINT check_paper_status CHECK (((status)::text = ANY ((ARRAY['submitted'::character varying, 'under review'::character varying, 'accepted'::character varying, 'rejected'::character varying, 'withdrawn'::character varying])::text[])))
);


--
-- Name: reviewers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reviewers (
    reviewer_id integer NOT NULL,
    years_of_experience integer NOT NULL,
    CONSTRAINT check_if_xp_years_is_nonnegative CHECK ((years_of_experience >= 0))
);


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sessions (
    session_id integer NOT NULL,
    conference_id integer NOT NULL,
    reviewer_id integer NOT NULL,
    title character varying(100) NOT NULL,
    room character varying(10) NOT NULL,
    session_date date NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone NOT NULL,
    CONSTRAINT check_start_earlier_than_end CHECK ((start_time < end_time))
);


--
-- Name: tracks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tracks (
    track_id integer NOT NULL,
    research_area_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500) NOT NULL,
    conference_id integer NOT NULL,
    reviewer_id integer NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    email character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    country character varying(100) NOT NULL,
    affiliation character varying(100) NOT NULL,
    phone_number character varying(100) NOT NULL
);


--
-- Name: accepted_paper_schedule; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.accepted_paper_schedule AS
 SELECT p.paper_id,
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
    (((cu.first_name)::text || ' '::text) || (cu.last_name)::text) AS chair_name,
    (((au.first_name)::text || ' '::text) || (au.last_name)::text) AS corresponding_author_name,
    au.email AS corresponding_author_email
   FROM ((((((((public.papers p
     JOIN public.tracks t ON ((t.track_id = p.track_id)))
     JOIN public.conferences c ON ((c.conference_id = t.conference_id)))
     JOIN public.sessions s ON ((s.session_id = p.session_id)))
     JOIN public.reviewers r ON ((r.reviewer_id = s.reviewer_id)))
     JOIN public.users cu ON ((cu.user_id = r.reviewer_id)))
     JOIN public.author_papers ahp ON (((ahp.paper_id = p.paper_id) AND (ahp.is_corresponding = true))))
     JOIN public.authors a ON ((a.author_id = ahp.author_id)))
     JOIN public.users au ON ((au.user_id = a.author_id)))
  WHERE (((p.status)::text = 'accepted'::text) AND (p.session_id IS NOT NULL));


--
-- Name: author_research_areas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.author_research_areas (
    author_id integer NOT NULL,
    research_area_id integer NOT NULL
);


--
-- Name: conferences_conference_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.conferences_conference_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: conferences_conference_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.conferences_conference_id_seq OWNED BY public.conferences.conference_id;


--
-- Name: expertise_areas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expertise_areas (
    expertise_area_id integer NOT NULL,
    label character varying(100) NOT NULL
);


--
-- Name: expertise_areas_expertise_area_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.expertise_areas_expertise_area_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: expertise_areas_expertise_area_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.expertise_areas_expertise_area_id_seq OWNED BY public.expertise_areas.expertise_area_id;


--
-- Name: hosts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hosts (
    conference_id integer NOT NULL,
    host_name character varying(100) NOT NULL
);


--
-- Name: keywords; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.keywords (
    paper_id integer NOT NULL,
    keyword character varying(100) NOT NULL
);


--
-- Name: maintained_conferences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.maintained_conferences (
    reviewer_id integer NOT NULL,
    conference_id integer NOT NULL
);


--
-- Name: paper_versions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.paper_versions (
    paper_id integer NOT NULL,
    version_number integer NOT NULL,
    file_location character varying(500) NOT NULL,
    upload_datetime timestamp with time zone NOT NULL,
    note character varying(500),
    CONSTRAINT check_version_number_positive CHECK ((version_number >= 1))
);


--
-- Name: papers_paper_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.papers_paper_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: papers_paper_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.papers_paper_id_seq OWNED BY public.papers.paper_id;


--
-- Name: research_areas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.research_areas (
    research_area_id integer NOT NULL,
    label character varying(100) NOT NULL
);


--
-- Name: research_areas_research_area_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.research_areas_research_area_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: research_areas_research_area_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.research_areas_research_area_id_seq OWNED BY public.research_areas.research_area_id;


--
-- Name: reviewer_expertise_areas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reviewer_expertise_areas (
    reviewer_id integer NOT NULL,
    expertise_area_id integer NOT NULL
);


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reviews (
    review_id integer NOT NULL,
    reviewer_id integer NOT NULL,
    paper_id integer NOT NULL,
    overall_score integer NOT NULL,
    recommendation character varying(50) NOT NULL,
    comments_for_authors character varying(500) NOT NULL,
    confidential_comments character varying(500) NOT NULL,
    submission_date date NOT NULL,
    CONSTRAINT check_overall_score CHECK (((overall_score >= 1) AND (overall_score <= 5))),
    CONSTRAINT check_recommendation CHECK (((recommendation)::text = ANY ((ARRAY['accept'::character varying, 'reject'::character varying])::text[])))
);


--
-- Name: reviews_review_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.reviews_review_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: reviews_review_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.reviews_review_id_seq OWNED BY public.reviews.review_id;


--
-- Name: sessions_session_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sessions_session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sessions_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sessions_session_id_seq OWNED BY public.sessions.session_id;


--
-- Name: tracks_track_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tracks_track_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tracks_track_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tracks_track_id_seq OWNED BY public.tracks.track_id;


--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: conferences conference_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conferences ALTER COLUMN conference_id SET DEFAULT nextval('public.conferences_conference_id_seq'::regclass);


--
-- Name: expertise_areas expertise_area_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expertise_areas ALTER COLUMN expertise_area_id SET DEFAULT nextval('public.expertise_areas_expertise_area_id_seq'::regclass);


--
-- Name: papers paper_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.papers ALTER COLUMN paper_id SET DEFAULT nextval('public.papers_paper_id_seq'::regclass);


--
-- Name: research_areas research_area_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.research_areas ALTER COLUMN research_area_id SET DEFAULT nextval('public.research_areas_research_area_id_seq'::regclass);


--
-- Name: reviews review_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews ALTER COLUMN review_id SET DEFAULT nextval('public.reviews_review_id_seq'::regclass);


--
-- Name: sessions session_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions ALTER COLUMN session_id SET DEFAULT nextval('public.sessions_session_id_seq'::regclass);


--
-- Name: tracks track_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracks ALTER COLUMN track_id SET DEFAULT nextval('public.tracks_track_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: author_papers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.author_papers (author_id, paper_id, author_order, is_corresponding) FROM stdin;
61	51	1	t
65	51	2	f
66	52	1	t
67	52	2	f
65	53	1	t
68	53	2	f
67	54	1	t
68	55	1	t
62	56	1	t
66	56	2	f
67	57	1	f
62	57	2	t
65	58	1	t
66	59	1	t
68	60	1	t
\.


--
-- Data for Name: author_research_areas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.author_research_areas (author_id, research_area_id) FROM stdin;
62	1
61	3
\.


--
-- Data for Name: authors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.authors (author_id, orcid) FROM stdin;
61	0000-0001-0000-0001
62	0000-0001-0000-0002
63	0000-0001-0000-0003
64	\N
65	0000-0001-0000-0005
66	0000-0001-0000-0006
67	\N
68	0000-0001-0000-0008
\.


--
-- Data for Name: conferences; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.conferences (conference_id, name, description, acronym, city, country, start_date, end_date, paper_submission_deadline, paper_review_deadline) FROM stdin;
11	Astana Symposium on Computing	Annual computing conference in Astana.	ASC26	Astana	Kazakhstan	2026-06-10	2026-06-12	2026-04-15 23:59:00+00	2026-05-15 23:59:00+00
12	Berlin Systems Workshop	Workshop on distributed systems in Berlin.	BSW26	Berlin	Germany	2026-09-20	2026-09-22	2026-07-01 23:59:00+00	2026-08-01 23:59:00+00
\.


--
-- Data for Name: expertise_areas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.expertise_areas (expertise_area_id, label) FROM stdin;
1	Peer Review
2	Data Systems
3	Databases
4	Cloud & Infrastructure
5	Algorithms
6	Applied AI
\.


--
-- Data for Name: hosts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.hosts (conference_id, host_name) FROM stdin;
11	Nazarbayev University
11	KBTU
12	TU Berlin
\.


--
-- Data for Name: keywords; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.keywords (paper_id, keyword) FROM stdin;
51	databases
51	cardinality
52	transformers
52	quantization
53	b-tree
53	storage
54	gnn
54	healthcare
55	distributed
55	locks
56	diffusion
56	priors
57	multimodal
57	vision
58	vector-search
58	compression
59	audio
59	contrastive
60	olap
60	columnar
\.


--
-- Data for Name: maintained_conferences; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.maintained_conferences (reviewer_id, conference_id) FROM stdin;
69	11
64	11
71	11
72	12
\.


--
-- Data for Name: paper_versions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.paper_versions (paper_id, version_number, file_location, upload_datetime, note) FROM stdin;
51	1	/files/p1_v1.pdf	2026-03-10 12:00:00+00	Initial
51	2	/files/p1_v2.pdf	2026-04-01 10:00:00+00	Camera ready
52	1	/files/p2_v1.pdf	2026-03-12 15:00:00+00	Initial
53	1	/files/p3_v1.pdf	2026-03-15 09:30:00+00	Draft
53	3	/files/p3_v3.pdf	2026-04-05 18:00:00+00	Revision
54	1	/files/p4_v1.pdf	2026-03-20 11:00:00+00	Submitted
55	1	/files/p5_v1.pdf	2026-03-05 14:00:00+00	Initial
56	1	/files/p6_v1.pdf	2026-03-18 16:00:00+00	Initial
57	1	/files/p7_v1.pdf	2026-03-22 10:15:00+00	v1
57	2	/files/p7_v2.pdf	2026-03-28 12:30:00+00	v2
58	1	/files/p8_v1.pdf	2026-03-11 08:45:00+00	Initial
59	1	/files/p9_v1.pdf	2026-03-25 13:20:00+00	Initial
60	1	/files/p10_v1.pdf	2026-03-29 17:00:00+00	Initial
\.


--
-- Data for Name: papers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.papers (paper_id, track_id, session_id, title, abstract, status, submission_date) FROM stdin;
51	22	11	Neural Query Cardinality Estimation	Machine learning models for join size estimation.	accepted	2026-03-10
52	21	\N	Low-Latency Transformers on Edge Nodes	Quantized inference for constrained devices.	accepted	2026-03-12
53	22	\N	Adaptive B-Tree Compaction Under Skew	Reducing write amplification in skewed workloads.	under review	2026-03-15
54	21	\N	Graph Embeddings for Clinical Triage	Graph neural networks over patient histories.	submitted	2026-03-20
55	22	\N	Naive Heuristics in Distributed Locks	Empirical study of lease timeouts.	rejected	2026-03-05
56	21	\N	Withdrawn Study on Diffusion Priors	Preliminary experiments withdrawn by authors.	withdrawn	2026-03-18
57	21	\N	Second Withdrawn Paper by Amina	Merged into a broader journal manuscript.	withdrawn	2026-03-22
58	22	11	Vector Index Compression with Product Quantization	Memory-efficient nearest neighbor search.	accepted	2026-03-11
59	21	\N	Contrastive Audio Representations	Self-supervised acoustic embeddings.	under review	2026-03-25
60	22	\N	Columnar Scan Pushdown in Analytical Engines	Predicate pushdown for nested formats.	submitted	2026-03-29
\.


--
-- Data for Name: research_areas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.research_areas (research_area_id, label) FROM stdin;
1	Machine Learning
2	Distributed Systems
3	Databases
4	Cybersecurity
5	Software Engineering
\.


--
-- Data for Name: reviewer_expertise_areas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reviewer_expertise_areas (reviewer_id, expertise_area_id) FROM stdin;
69	6
64	2
64	3
70	4
\.


--
-- Data for Name: reviewers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reviewers (reviewer_id, years_of_experience) FROM stdin;
61	5
62	4
63	3
64	6
69	8
70	2
71	7
72	4
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reviews (review_id, reviewer_id, paper_id, overall_score, recommendation, comments_for_authors, confidential_comments, submission_date) FROM stdin;
51	69	51	5	accept	Strong experimental results.	Solid paper for the session.	2026-04-20
52	71	51	4	accept	Clear methodology.	Good fit.	2026-04-21
53	72	51	4	accept	Helpful ablations.	Consistent positive scores.	2026-04-22
54	64	52	4	accept	Practical edge benchmarks.	Accepted.	2026-04-23
55	71	52	5	accept	Crisp writing.	Strong accept.	2026-04-24
56	69	53	3	accept	Clarify skew assumptions.	Borderline positive.	2026-04-25
57	72	54	3	reject	Cohort size is small.	Needs more validation.	2026-04-26
58	64	55	2	reject	Baseline comparison missing.	Reject.	2026-04-27
59	71	58	4	accept	Good recall-memory trade-off.	Accept.	2026-04-28
60	69	59	3	reject	Expand evaluation datasets.	Weak on baselines.	2026-04-29
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sessions (session_id, conference_id, reviewer_id, title, room, session_date, start_time, end_time) FROM stdin;
11	11	69	Keynote & Accepted Papers	A101	2026-06-10	2026-06-10 09:00:00+00	2026-06-10 11:00:00+00
12	11	64	Open Discussion (Empty Session)	B202	2026-06-11	2026-06-11 14:00:00+00	2026-06-11 15:30:00+00
\.


--
-- Data for Name: tracks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tracks (track_id, research_area_id, name, description, conference_id, reviewer_id) FROM stdin;
21	1	Applied AI	Machine learning and intelligent systems.	11	69
22	3	Data Engineering	Relational and distributed storage engines.	11	64
23	4	Empty Track	Track with no submitted papers.	11	71
24	3	Berlin Systems Track	Track in Berlin conference with zero papers.	12	72
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (user_id, email, first_name, last_name, country, affiliation, phone_number) FROM stdin;
61	arman.armanov@example.com	Arman	Armanov	Kazakhstan	Nazarbayev University	+77010000001
62	amina.aminova@example.com	Amina	Aminova	Kazakhstan	KBTU	+77010000002
63	dias.serikov@example.com	Dias	Serikov	Kazakhstan	AITU	+77010000003
64	dana.nurlanova@example.com	Dana	Nurlanova	Kazakhstan	Satbayev University	+77010000004
65	alikhan.tolegen@example.com	Alikhan	Tolegen	Kazakhstan	SDU University	+77010000005
66	madina.kassenova@example.com	Madina	Kassenova	Kazakhstan	MNU	+77010000006
67	timur.akhmetov@example.com	Timur	Akhmetov	Kazakhstan	IITU	+77010000007
68	aisulu.omarova@example.com	Aisulu	Omarova	Kazakhstan	KIMEP	+77010000008
69	rustem.bekov@example.com	Rustem	Bekov	Kazakhstan	NU	+77010000009
70	saule.karimova@example.com	Saule	Karimova	Kazakhstan	KBTU	+77010000010
71	nurlan.smagulov@example.com	Nurlan	Smagulov	Germany	TU Munich	+491510000011
72	kamila.zhaksylyk@example.com	Kamila	Zhaksylyk	Germany	TU Berlin	+491510000012
\.


--
-- Name: conferences_conference_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.conferences_conference_id_seq', 12, true);


--
-- Name: expertise_areas_expertise_area_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.expertise_areas_expertise_area_id_seq', 36, true);


--
-- Name: papers_paper_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.papers_paper_id_seq', 60, true);


--
-- Name: research_areas_research_area_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.research_areas_research_area_id_seq', 30, true);


--
-- Name: reviews_review_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reviews_review_id_seq', 60, true);


--
-- Name: sessions_session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sessions_session_id_seq', 12, true);


--
-- Name: tracks_track_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tracks_track_id_seq', 24, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_id_seq', 72, true);


--
-- Name: author_papers author_papers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.author_papers
    ADD CONSTRAINT author_papers_pkey PRIMARY KEY (author_id, paper_id);


--
-- Name: author_research_areas author_research_areas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.author_research_areas
    ADD CONSTRAINT author_research_areas_pkey PRIMARY KEY (author_id, research_area_id);


--
-- Name: authors authors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authors
    ADD CONSTRAINT authors_pkey PRIMARY KEY (author_id);


--
-- Name: conferences conferences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conferences
    ADD CONSTRAINT conferences_pkey PRIMARY KEY (conference_id);


--
-- Name: expertise_areas expertise_areas_label_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expertise_areas
    ADD CONSTRAINT expertise_areas_label_key UNIQUE (label);


--
-- Name: expertise_areas expertise_areas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expertise_areas
    ADD CONSTRAINT expertise_areas_pkey PRIMARY KEY (expertise_area_id);


--
-- Name: hosts hosts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hosts
    ADD CONSTRAINT hosts_pkey PRIMARY KEY (conference_id, host_name);


--
-- Name: keywords keywords_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keywords
    ADD CONSTRAINT keywords_pkey PRIMARY KEY (paper_id, keyword);


--
-- Name: maintained_conferences maintained_conferences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.maintained_conferences
    ADD CONSTRAINT maintained_conferences_pkey PRIMARY KEY (reviewer_id, conference_id);


--
-- Name: paper_versions paper_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.paper_versions
    ADD CONSTRAINT paper_versions_pkey PRIMARY KEY (paper_id, version_number);


--
-- Name: papers papers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.papers
    ADD CONSTRAINT papers_pkey PRIMARY KEY (paper_id);


--
-- Name: research_areas research_areas_label_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.research_areas
    ADD CONSTRAINT research_areas_label_key UNIQUE (label);


--
-- Name: research_areas research_areas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.research_areas
    ADD CONSTRAINT research_areas_pkey PRIMARY KEY (research_area_id);


--
-- Name: reviewer_expertise_areas reviewer_expertise_areas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviewer_expertise_areas
    ADD CONSTRAINT reviewer_expertise_areas_pkey PRIMARY KEY (reviewer_id, expertise_area_id);


--
-- Name: reviewers reviewers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviewers
    ADD CONSTRAINT reviewers_pkey PRIMARY KEY (reviewer_id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (review_id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (session_id);


--
-- Name: tracks tracks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_pkey PRIMARY KEY (track_id);


--
-- Name: author_papers uq_paper_author_order; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.author_papers
    ADD CONSTRAINT uq_paper_author_order UNIQUE (paper_id, author_order);


--
-- Name: reviews uq_review_reviewer_paper; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT uq_review_reviewer_paper UNIQUE (reviewer_id, paper_id);


--
-- Name: users users_phone_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_phone_number_key UNIQUE (phone_number);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: author_papers author_papers_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.author_papers
    ADD CONSTRAINT author_papers_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.authors(author_id) ON DELETE CASCADE;


--
-- Name: author_papers author_papers_paper_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.author_papers
    ADD CONSTRAINT author_papers_paper_id_fkey FOREIGN KEY (paper_id) REFERENCES public.papers(paper_id) ON DELETE CASCADE;


--
-- Name: author_research_areas author_research_areas_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.author_research_areas
    ADD CONSTRAINT author_research_areas_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.authors(author_id) ON DELETE CASCADE;


--
-- Name: author_research_areas author_research_areas_research_area_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.author_research_areas
    ADD CONSTRAINT author_research_areas_research_area_id_fkey FOREIGN KEY (research_area_id) REFERENCES public.research_areas(research_area_id) ON DELETE CASCADE;


--
-- Name: authors authors_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authors
    ADD CONSTRAINT authors_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: hosts hosts_conference_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hosts
    ADD CONSTRAINT hosts_conference_id_fkey FOREIGN KEY (conference_id) REFERENCES public.conferences(conference_id) ON DELETE CASCADE;


--
-- Name: keywords keywords_paper_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.keywords
    ADD CONSTRAINT keywords_paper_id_fkey FOREIGN KEY (paper_id) REFERENCES public.papers(paper_id) ON DELETE CASCADE;


--
-- Name: maintained_conferences maintained_conferences_conference_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.maintained_conferences
    ADD CONSTRAINT maintained_conferences_conference_id_fkey FOREIGN KEY (conference_id) REFERENCES public.conferences(conference_id) ON DELETE CASCADE;


--
-- Name: maintained_conferences maintained_conferences_reviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.maintained_conferences
    ADD CONSTRAINT maintained_conferences_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.reviewers(reviewer_id) ON DELETE CASCADE;


--
-- Name: paper_versions paper_versions_paper_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.paper_versions
    ADD CONSTRAINT paper_versions_paper_id_fkey FOREIGN KEY (paper_id) REFERENCES public.papers(paper_id) ON DELETE CASCADE;


--
-- Name: papers papers_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.papers
    ADD CONSTRAINT papers_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(session_id) ON DELETE SET NULL;


--
-- Name: papers papers_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.papers
    ADD CONSTRAINT papers_track_id_fkey FOREIGN KEY (track_id) REFERENCES public.tracks(track_id) ON DELETE CASCADE;


--
-- Name: reviewer_expertise_areas reviewer_expertise_areas_expertise_area_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviewer_expertise_areas
    ADD CONSTRAINT reviewer_expertise_areas_expertise_area_id_fkey FOREIGN KEY (expertise_area_id) REFERENCES public.expertise_areas(expertise_area_id) ON DELETE CASCADE;


--
-- Name: reviewer_expertise_areas reviewer_expertise_areas_reviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviewer_expertise_areas
    ADD CONSTRAINT reviewer_expertise_areas_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.reviewers(reviewer_id) ON DELETE CASCADE;


--
-- Name: reviewers reviewers_reviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviewers
    ADD CONSTRAINT reviewers_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: reviews reviews_paper_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_paper_id_fkey FOREIGN KEY (paper_id) REFERENCES public.papers(paper_id) ON DELETE CASCADE;


--
-- Name: reviews reviews_reviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.reviewers(reviewer_id) ON DELETE CASCADE;


--
-- Name: sessions sessions_conference_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_conference_id_fkey FOREIGN KEY (conference_id) REFERENCES public.conferences(conference_id) ON DELETE CASCADE;


--
-- Name: sessions sessions_reviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.reviewers(reviewer_id) ON DELETE CASCADE;


--
-- Name: tracks tracks_conference_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_conference_id_fkey FOREIGN KEY (conference_id) REFERENCES public.conferences(conference_id) ON DELETE CASCADE;


--
-- Name: tracks tracks_research_area_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_research_area_id_fkey FOREIGN KEY (research_area_id) REFERENCES public.research_areas(research_area_id) ON DELETE CASCADE;


--
-- Name: tracks tracks_reviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.reviewers(reviewer_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

