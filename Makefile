COMPOSE = docker compose

.PHONY: dev migrate seed test logs

dev:
	$(COMPOSE) up --build

migrate:
	$(COMPOSE) run --rm api alembic upgrade head

seed:
	$(COMPOSE) run --rm -v ./scripts:/scripts api python /scripts/seed.py

test:
	$(COMPOSE) run --rm api pytest

logs:
	$(COMPOSE) logs -f api worker flower postgres redis
