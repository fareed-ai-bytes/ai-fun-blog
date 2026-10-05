# Blog Platform — every repeated command lives here. Run `make help` for the list.
# Commands run inside Docker by default; pass LOCAL=1 to run backend/frontend tools directly
# on the host (uv / npm), e.g. `make test-api LOCAL=1`.

SHELL := sh
.DEFAULT_GOAL := help
COMPOSE := docker compose

ifeq ($(LOCAL),1)
API_RUN := cd backend && uv run
API_DB_RUN := $(API_RUN)
WEB_RUN := cd frontend && npx
else
API_RUN := $(COMPOSE) run --rm --no-deps api
API_DB_RUN := $(COMPOSE) run --rm api
WEB_RUN := $(COMPOSE) run --rm --no-deps web npx
endif

define todo
	@echo "make $@: not implemented yet ($(1))"; exit 1
endef

.PHONY: help
help: ## List every target with a description
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup: up migrate seed ## First run: start the stack, migrate, seed demo data

##@ Stack
.PHONY: up down logs logs-worker up-s3 up-prod up-obs
up: ## Start db, api and web (dev, hot reload)
	$(COMPOSE) up -d --build --wait

down: ## Stop the stack
	$(COMPOSE) down

logs: ## Follow logs of all services
	$(COMPOSE) logs -f

logs-worker: ## Follow import worker logs
	$(call todo,T-021)

up-s3: ## Start the stack with MinIO object storage
	$(call todo,T-021)

up-prod: ## Prod-like stack: built images, nginx on :8080
	$(call todo,T-070)

up-obs: ## Observability: Prometheus, Grafana, GlitchTip
	$(call todo,T-074)

##@ Database
.PHONY: migrate migration seed seed-perf
migrate: ## Apply Alembic migrations
	$(API_DB_RUN) alembic upgrade head

migration: ## Create a migration: make migration m="message"
	$(API_DB_RUN) alembic revision --autogenerate -m "$(m)"

seed: ## Seed demo data (idempotent)
	$(API_DB_RUN) python -m scripts.seed

seed-perf: ## Seed 100k-post performance dataset (slow)
	$(call todo,T-022)

##@ Quality
.PHONY: test-api test-web test-e2e lint lint-api lint-web lint-arch fmt ci
test-api: ## Run backend tests (against the blog_test database)
	$(API_DB_RUN) pytest

test-web: ## Run frontend unit tests (Vitest)
	$(WEB_RUN) vitest run

test-e2e: ## Playwright smoke test against the running stack (host; needs `make up`)
	cd frontend && npx playwright install chromium && npx playwright test

lint: lint-api lint-web ## Lint backend and frontend

lint-api: ## Lint backend (ruff)
	$(API_RUN) ruff check .
	$(API_RUN) ruff format --check .

lint-web: ## Lint frontend (ESLint + Prettier + tsc)
	$(WEB_RUN) eslint .
	$(WEB_RUN) prettier --check .
	$(WEB_RUN) tsc -b

lint-arch: ## Check module boundaries (import-linter)
	$(call todo,T-086)

fmt: ## Format backend and frontend
	$(API_RUN) ruff format .
	$(API_RUN) ruff check --fix .
	$(WEB_RUN) prettier --write .

ci: lint test-api test-web ## Run all CI checks locally

##@ Performance
.PHONY: explain loadtest
explain: ## EXPLAIN (ANALYZE, BUFFERS) key queries -> docs/perf/plans/
	$(call todo,T-022)

loadtest: ## Locust load test, headless, 60 s
	$(call todo,T-022)

##@ Operations
.PHONY: backup restore-test grant-admin deploy
backup: ## Back up database and uploads
	$(call todo,T-076)

restore-test: ## Restore latest backup into a scratch DB and compare
	$(call todo,T-076)

grant-admin: ## Grant platform admin: make grant-admin email=...
	$(call todo,T-065)

deploy: ## Deploy a release: make deploy VERSION=vX.Y.Z
	$(call todo,T-078)

##@ Codegen & tooling
.PHONY: permissions-doc gen-client smee
permissions-doc: ## Regenerate docs/permissions.md from app/authz
	$(call todo,T-061)

gen-client: ## Regenerate typed API client from OpenAPI
	$(call todo,T-087)

smee: ## Webhook tunnel for GitHub (smee.io)
	$(call todo,T-097)
