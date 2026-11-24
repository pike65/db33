<h1 align="center">DB Assignment 3</h1>

<h3 align="center">By Daryn Imash (pike65)</h3>

# ✳️ Quick Start

Requirements: **Docker Desktop** (must be running). Nothing else is needed.

1. Unzip the archive and open the folder in VS Code.
2. Open a terminal in VS Code (Terminal > New Terminal).
3. Run:

   ```bash
   docker compose up --build -d
   ```

4. Wait about 10 seconds, then open the Swagger UI:

   **http://localhost:8000/docs**

The database starts **empty**: the tables exist, but there is no data. See the next section to add the sample data.

# ❇️ Typical Workflow

Run these in the same terminal after the project is up.

1. **Fill the database with sample data**

   ```bash
   docker compose exec app python -m app.database.seed
   ```

   Refresh `/docs` and try the endpoints (for example `GET /users`).

2. **Run the Part 2 queries**

   ```bash
   docker compose exec app python -m part2.run_part2
   ```

   Prints every task with its SQL and results. Part 2 updates and deletes data, so restore the data afterwards.

3. **Restore the original sample data**

   ```bash
   docker compose exec app python -m app.database.seed --reset
   ```

4. **Experiment** in Swagger or psql. Repeat step 3 at any time to start again from the original data.

# 🍀 Commands

All commands need only Docker. Run them in the project folder.

| What it does | Command |
|---|---|
| Build and start the database and the app in the background | `docker compose up --build -d` |
| Show app logs | `docker compose logs -f app` |
| Fill the empty database with sample data (does nothing if data already exists) | `docker compose exec app python -m app.database.seed` |
| Run all Part 2 tasks and print results | `docker compose exec app python -m part2.run_part2` |
| Delete all data and restore the original sample data | `docker compose exec app python -m app.database.seed --reset` |
| Open psql | `docker exec -it db3_container psql -U neo -d db3_db` |
| Stop everything, keep data | `docker compose down` |
| Stop everything and delete all data | `docker compose down -v` |

# 🛑 Shut Down

Stop the containers and keep the data (it will still be there next time):

```bash
docker compose down
```

Stop the containers and delete all data (the next start gives an empty database):

```bash
docker compose down -v
```

# 🪬 Explore the Database with psql

While the project is running, open a second terminal and run:

```bash
docker exec -it db3_container psql -U neo -d db3_db
```

Useful commands inside psql:

| Command | What it does |
|---|---|
| `\dt` | List all tables |
| `\d table_name` | Show columns, keys and constraints of a table |
| `\dv` | List views |
| `SELECT * FROM table_name LIMIT 5;` | Query a table (end every query with `;`) |
| `\q` | Exit psql |

Database credentials: user `neo`, password `believe123`, database `db3_db`.

# 🧊 Project Details

## Stack

1. `FastAPI` - handling requests, defining endpoints, sending responses
2. `Pydantic` - data validation, serialization
3. `SQLAlchemy` - ORM
4. `PostgreSQL 17` - database
5. `Docker` and `Docker Compose` - running the database and the app
6. `uv` - package manager (Python 3.14)
7. `ruff` - linter and formatting
8. `just` - command runner used during development (optional, not required)

## Structure

1. The web app uses a modular structure: each entity's endpoints, service logic and schemas are isolated in `app/modules/<domain_name>/`.
2. Shared resources (settings, exceptions) are in `app/core/`.
3. Tables (models), the database connection and the seed script are in `app/database/`.
4. Part 2 scripts are in `part2/`, outside the app so there are no conflicts.
5. Tables are created automatically when the app starts. Data is added only by the seed command.