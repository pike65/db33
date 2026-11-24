default:
    @just --list

# ---------- Docker (main workflow) ----------

# Build and start database + app in the foreground
up:
    docker compose up --build

# Build and start database + app in the background
upd:
    docker compose up --build -d

# Show app logs
logs:
    docker compose logs -f app

# Stop containers, keep data
stop:
    docker compose down

# Stop containers and delete all data
down:
    docker compose down -v

# Fill the empty database with sample data
seed:
    docker compose exec app python -m app.database.seed

# Wipe the database and restore the original sample data
seed-reset:
    docker compose exec app python -m app.database.seed --reset

# Run all Part 2 tasks and print results
part2:
    docker compose exec app python -m part2.run_part2

# Open psql inside the database container
psql:
    docker exec -it db3_container psql -U neo -d db3_db

# ---------- Local development (no app container) ----------

# Start only the database
db:
    docker compose up -d db

# Run the API locally with auto-reload
fast:
    uv run fastapi dev

# Seed / reset / Part 2 from your local Python environment
seed-local:
    uv run python -m app.database.seed

seed-reset-local:
    uv run python -m app.database.seed --reset

part2-local:
    uv run python -m part2.run_part2

# ---------- Code quality ----------

fmt:
    uv run ruff format .

lint:
    uv run ruff check . --fix

check: fmt lint