<h1 align="center">DB Assignment 3</h1>

<h3 align="center">By Daryn Imash (pike65)</h3>

# Setup and Run
-- here add details how it must be run (docker things)


# Run Separetely
-- here add details how to use everything when runned locally (separately: db is run by docker compose, others are controlled by just)

# ❇️ Project Details
## Stack
1. `FastAPI` - handling requests, definng endpoints, sending responses
2. `Pydantic` - data validation, serialization
3. `SQLAlchemy` - ORM
4. `Docker` and `Docker Compose` - using PostgreSQL, deployment
5. `uv` - package manager
6. `ruff` - linter and formatting
7. `just` - command runner and control tool

## Structure
1. Web app uses modular structure where each entity's endoints, service/business logic, schemas are isolated (no circular imports). They are placed in `/modules/<domain_name>/*` folders.
2. Shared and common resources are placed in `/core/*` folder.
3. All tables (models) and everything related to DB placed in `/database/*` folder.
4. Additional folders and files are placed in root outside of app so no conflicts would appear.

# using psql
```bash
docker exec -it db3_container psql -U neo -d db3_db
```
