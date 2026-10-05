# Blog Platform

A multi-user blog where **anyone can read** published posts without logging in, **registered users
write** and manage their own posts, and **other logged-in users like and comment**. It's built to
show authentication and authorisation done properly (ownership, visibility, safe defaults) in a
modular, tested and documented codebase you can run locally in a few minutes.

**Stack:** FastAPI · PostgreSQL 16 · SQLAlchemy 2 + Alembic · React + Vite + TypeScript ·
TanStack Query · Tailwind CSS · Docker Compose

> **Status:** v1 (core blog + auth) feature-complete. Progress and next steps live in
> [docs/tasks.md](docs/tasks.md).

<!-- Screenshot: add docs/screenshot.png (feed page after `make setup`) and uncomment:
![Feed page](docs/screenshot.png)
-->

## Features (v1)
- Public feed (newest first, 10 per page) and post pages — no login needed.
- Sign up, log in, log out. Session is a JWT in an `HttpOnly`, `SameSite=Lax` cookie; passwords
  hashed with argon2id.
- Write posts in Markdown with a live preview; save drafts; publish and unpublish; edit; delete.
- "My posts" dashboard with drafts and status badges.
- Like/unlike (not your own posts) and comment on published posts; delete your comments, or any
  comment on your own post.
- Drafts are invisible to everyone but their author — requesting one returns **Not found**, not
  "Forbidden".
- Author pages (`/u/<username>`), loading/empty/error states everywhere, raw HTML in posts shown
  as text.

## Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (on Windows: with WSL2)
- GNU Make
- Only for running tools outside Docker (`LOCAL=1`) or the browser smoke test:
  [uv](https://docs.astral.sh/uv/) and Node.js ≥ 22.12

## Quickstart
```bash
cp .env.example .env
make setup        # = make up + make migrate + make seed
```
Then open:
| What | URL |
|---|---|
| Web app | http://localhost:5173 |
| Interactive API docs (OpenAPI) | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/v1/health |

### Demo logins (created by `make seed`)
| Email | Password |
|---|---|
| alice@example.com | `demo-password-1` |
| bob@example.com | `demo-password-1` |
| carol@example.com | `demo-password-1` |

Each has published posts, one draft, and likes and comments on the others' posts.
`make seed` is safe to run again — it never creates duplicates.

## Commands
Run `make help` for every target. The ones you'll use:

| Command | What it does |
|---|---|
| `make setup` | First run: start the stack, migrate, seed |
| `make up` / `make down` | Start / stop db (:5432), api (:8000) and web (:5173) |
| `make logs` | Follow all container logs |
| `make migrate` | Apply database migrations |
| `make migration m="add x"` | Create a new migration (review it before committing) |
| `make seed` | Load demo data (idempotent) |
| `make test-api` | Backend tests (pytest, against a separate `blog_test` database) |
| `make test-web` | Frontend unit tests (Vitest) |
| `make test-e2e` | Browser smoke test (Playwright) against the running stack |
| `make lint` / `make fmt` | Lint / format backend (ruff) and frontend (ESLint, Prettier, tsc) |
| `make ci` | Everything CI runs: lint + backend + frontend tests |
| `make api-docs` | Re-export `docs/openapi.json` and regenerate `docs/api.md` |

Add `LOCAL=1` to run backend/frontend tools on your machine instead of in containers, e.g.
`make lint LOCAL=1` (the database still runs in Docker).

## Project structure
```
backend/
  app/
    main.py              app factory: CORS, error handlers, /api/v1 routers
    core/                settings, security (argon2id, JWT), errors (envelope), pagination
    db/                  engine/session, declarative base
    modules/<feature>/   auth, users, posts, likes, comments, health
                         router.py (HTTP) → service.py (rules) → repository.py (SQL) → models.py
  alembic/               migrations
  scripts/               seed.py, export_openapi.py, gen_api_docs.py
  tests/                 pytest suite (one test per acceptance criterion and business rule)
frontend/
  src/api/               the only place that calls fetch(); typed endpoint functions
  src/features/          auth, posts, likes, comments — hooks and feature components
  src/components/        shared UI (layout, header, buttons, states, markdown)
  src/pages/             route-level screens
  e2e/                   Playwright smoke test
docs/                    product, architecture, rules, design, API reference, usage guide
```

## How it works
The browser talks only to the Vite dev server (:5173), which proxies `/api` to FastAPI (:8000), so
the auth cookie is first-party and CORS stays strict. Routers validate input with Pydantic and call
a service; services hold every ownership and visibility rule and raise domain errors; repositories
hold all SQL. Every error response uses one envelope:
`{"error": {"code", "message", "details"}}`. Feed counts come from a single query per page — no
N+1 — and tests assert the query count stays constant.

## Documentation
- [API reference](docs/api.md) (generated from [openapi.json](docs/openapi.json)) ·
  [Usage walkthroughs](docs/usage.md)
- [Product requirements](docs/product.md) · [Architecture](docs/architecture.md) ·
  [Rules](docs/rules.md) · [Design](docs/design.md)
- [Tasks & progress](docs/tasks.md) · [Decisions & gotchas](docs/memory.md) ·
  [Engineering workflow](docs/engineering.md)

## License
GPL-3.0 — see [LICENSE](LICENSE).
