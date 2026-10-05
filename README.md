# Blog Platform

A multi-user blog: anyone can read published posts without logging in; registered users write and
manage their own posts; other logged-in users like and comment. Built with FastAPI, PostgreSQL and a
React + Vite SPA, running locally on Docker Compose.

> Status: **v1 in progress** — repo scaffold (T-001) done. Progress is tracked in [docs/tasks.md](docs/tasks.md).

## Prerequisites
- Docker Desktop (with WSL2 on Windows)
- GNU Make
- For running tools outside Docker (`LOCAL=1`): [uv](https://docs.astral.sh/uv/) and Node.js ≥ 22.12

## Quickstart
```bash
cp .env.example .env
make up
```
- Web app: http://localhost:5173
- API health: http://localhost:8000/api/v1/health
- API docs (OpenAPI): http://localhost:8000/docs

## Commands
Run `make help` for every target. The most used:

| Command | What it does |
|---|---|
| `make up` / `make down` | Start / stop db, api and web |
| `make test-api` | Backend tests |
| `make lint` / `make fmt` | Lint / format backend and frontend |
| `make ci` | All CI checks locally |

Add `LOCAL=1` to run backend/frontend tools on the host instead of in containers, e.g. `make lint LOCAL=1`.

## Project structure
```
backend/    FastAPI app (app/modules/<feature>/ — router, service, repository, schemas, models)
frontend/   React + Vite + TypeScript SPA
docs/       Product, architecture, rules, design, tasks and project memory
```

## Documentation
- [Product requirements](docs/product.md) · [Architecture & API contract](docs/architecture.md) · [Rules](docs/rules.md)
- [Design](docs/design.md) · [Tasks & progress](docs/tasks.md) · [Engineering workflow](docs/engineering.md)

## License
GPL-3.0 — see [LICENSE](LICENSE).
