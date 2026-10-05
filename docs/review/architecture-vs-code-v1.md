# architecture.md vs. the v1 code — differences (T-018)
_Written 2026-10-06. Per CLAUDE.md the docs were **not** changed to match the code; each row needs a
decision: fix the doc, fix the code, or accept._

| # | Area | architecture.md says | Code does | Suggested resolution |
|---|---|---|---|---|
| 1 | Backend layout | v1 "Directory map": `app/api/v1/*.py` routers, `app/services/`, `app/models/`, `app/schemas/`; v5 map supersedes it "once T-084 lands" | v5 layout from day one: `app/modules/<feature>/{router,schemas,service,repository,models}.py` (memory.md 2026-10-05) | Doc: mark the v1 map as historical now; mark T-084 done-by-design |
| 2 | Repository layer | Decisions list: "Routers → services, no repository layer" | Repositories exist (v5 decision applied early) | Doc: strike the v1 decision line (memory.md already records the reversal) |
| 3 | `core/deps.py` | Holds `get_db`, `get_current_user`, `get_optional_user` | `get_db` in `app/db/session.py`; auth dependencies in `app/modules/auth/dependencies.py` | Doc: update the Key components row |
| 4 | Service names | `auth_service`, `post_service`, `like_service`, `comment_service` | `modules/{auth,posts,likes,comments}/service.py`, plus `modules/users/service.py` (public interface used by auth) | Doc: rename in Key components |
| 5 | Module boundaries | Repository → own models only (rules.md v5) | `posts/repository.py` reads `likes` and `comments` for counts and `liked_by_me` (one query per page) | Accept as a documented exception; encode it in the T-086 import-linter contract |
| 6 | System overview diagram | Middleware box "gzip, rate limit, timing" | No custom middleware in v1 (only CORS) — those arrive in v2 (T-021, T-032, T-033) | Doc: label the box "(v2)" |
| 7 | Editor route | design.md: `/edit/:id` | `/edit/:slug` — the v1 API reads posts by slug only, so an id-based route would need a second lookup | Doc (design.md): change to `/edit/:slug`, or add `GET /posts/by-id/{id}` in a later task |
| 8 | Error codes | Envelope defined; codes not listed | Codes in use: `VALIDATION_ERROR`, `NOT_AUTHENTICATED`, `INVALID_CREDENTIALS`, `EMAIL_TAKEN`, `USERNAME_TAKEN`, `POST_NOT_FOUND`, `NOT_POST_OWNER`, `CANNOT_LIKE_OWN_POST`, `COMMENT_NOT_FOUND`, `NOT_ALLOWED_TO_DELETE_COMMENT`, `NOT_FOUND`, `METHOD_NOT_ALLOWED` | Doc: add the list (also generated into docs/api.md) |
| 9 | PATCH/DELETE on someone else's post | API table: owner routes → 403 | 403 for a published post, **404 for a draft** (BR-01/BR-41 — never confirm a draft exists) | Doc: add the 404 note to the API table |
| 10 | Timestamps | Not specified | `created_at`/`updated_at` set Python-side (`utcnow`), `now()` server default as fallback | Accept (memory.md) |
| 11 | Frontend dependencies | Pre-approved list | Adds `jsdom` (Vitest DOM) and `@testing-library/dom` (peer of `@testing-library/react`) — dev only | Confirm, then add both to the rules.md pre-approved list |
| 12 | Commands | CLAUDE.md command list | Extra targets: `make setup`, `make test-e2e`, `make api-docs`, `LOCAL=1` mode | Doc: add to CLAUDE.md Commands |
| 13 | Compose | v1: `docker-compose.yml` (db, api, web) | Matches; api/web healthchecks added early (v4 rule) | None |
