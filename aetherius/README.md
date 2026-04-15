# Aetherius Backend (`aetherius/`)

This README is scoped to the operational backend module only.

For full project overview, causal simulation architecture, and replay proof stack, use the root `README.md`.

## Scope

`aetherius/` contains the pilot operations backbone:

- FastAPI API and operator console routes
- PostgreSQL models and migrations
- Celery workers and scheduling
- Signal drafting, review workflow, quality gates, and delivery services
- Jinja templates for console, email, and PDF outputs

## Directory Overview

```text
aetherius/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    templates/
    workers/
  alembic/
  tests/
```

## Local Backend Bring-Up

1. Start infrastructure from repo root:

```bash
docker compose -f docker/docker-compose.yml up -d
```

2. Apply migrations:

```bash
cd aetherius
python -m alembic upgrade head
```

3. Verify health:

- `GET http://localhost:8000/health`

## Auth and Role Model

- Bootstrap: `POST /api/v1/auth/bootstrap-admin`
- Login: `POST /api/v1/auth/login`
- Roles: `admin`, `analyst`, `viewer`

All protected routes require bearer authentication and role checks.

## Delivery Modes

- Local: Mailpit SMTP (`localhost:1025`, UI `http://localhost:8025`)
- Pilot/production: Postmark SMTP

## Ownership Boundary

- Update this subtree for backend workflow changes (auth, review, delivery, audit).
- Update root modules (`core/`, `simulations/`, `orchestrator.py`) for causal simulation/replay behavior.
