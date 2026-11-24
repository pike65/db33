# ==========================================
# Default
# ==========================================

# List all available commands
default:
    @just --list

# ==========================================
# Database & Docker
# ==========================================

# Run DB in foreground
up:
    docker compose up

# Run DB in background
upd:
    docker compose up -d

# Stop db
stop:
    docker compose down

# Stop and wipe DB volumes (use when models/tables change)
down:
    docker compose down -v

# Fill tables of DB
seed:
    uv run python -m app.database.seed

# Restore original seed data (wipe + recreate + seed)
seed-reset:
    uv run python -m app.database.seed --reset

# Run script for Part 2
part2:
    uv run python -m part2.run_part2

# ==========================================
# Code Quality
# ==========================================

# Format code with Ruff
fmt:
    uv run ruff format .

# Lint and auto-fix issues with Ruff
lint:
    uv run ruff check . --fix

# Format and lint in one step
check: fmt lint


# ==========================================
# Backend & Demo
# ==========================================

# Run FastAPI dev server
fast:
    uv run fastapi dev

# Full stack start: boot DB in background, then start FastAPI
dev: upd fast

# Run everything in Docker (for proferssors)
docker:
    docker compose up --build