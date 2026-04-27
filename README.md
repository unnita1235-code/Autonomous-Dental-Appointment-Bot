# Autonomous Dental Appointment Bot

Production-focused monorepo for a dental clinic appointment automation platform.

## Monorepo Layout

- `apps/api`: FastAPI backend, SQLAlchemy async, Alembic, Celery workers
- `apps/web`: Next.js 14 frontend with App Router and TypeScript
- `apps/worker`: Additional worker task stubs
- `scripts`: Seed and evaluation scripts

## Quick Start

1. Copy environment values:
   - `cp .env.example .env`
2. Start services:
   - `docker compose up --build`
3. API health check:
   - `http://localhost:8000/health`
4. Web app (once started separately):
   - `http://localhost:3000`

## Backend Commands

- Run API (local): `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Run Celery worker: `celery -A app.workers.celery_app worker --loglevel=info`
- Run migrations: `alembic upgrade head`

## Frontend Commands

- Install: `npm install`
- Dev server: `npm run dev`
- Build: `npm run build`
