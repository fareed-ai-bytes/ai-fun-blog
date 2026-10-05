# Project Memory — Blog Platform
<!-- Append-only log of things a new engineer (or a fresh Claude session) would get wrong.
     NOT a task list (tasks.md) and NOT a restatement of architecture (architecture.md).
     Prune when it passes ~150 lines. Items marked (anticipated) were written before any code existed —
     confirm or delete them once hit. -->

## Decisions log
| Date | Decision | Why | Alternatives rejected |
|---|---|---|---|
| 2026-09-26 | FastAPI + React/Vite SPA + PostgreSQL, in Docker Compose | Auto-generated OpenAPI covers the API-contract deliverable; clear module boundaries for the "modular" requirement | Next.js full-stack — faster start but API contract is hand-written and boundaries blur; Express — no free OpenAPI |
| 2026-09-26 | JWT in HttpOnly SameSite=Lax cookie, no refresh token | Token unreadable by JS; simplest secure option for a 1-week build | localStorage bearer token — XSS-exposed; refresh-token rotation — too much for v1 |
| 2026-09-26 | Vite dev proxy `/api` → `api:8000` | Same origin in the browser, so the cookie is first-party and CORS stays trivial | Direct cross-origin calls — needs `allow_credentials` + exact origins and breaks easily |
| 2026-09-26 | Routers → services, no repository layer | Enough separation for this size; fewer files for Claude to keep consistent | Full repository pattern — ceremony without benefit at 4 tables |
| 2026-09-26 | Markdown bodies rendered with react-markdown, raw HTML disabled | Safe by default; no sanitiser to configure | WYSIWYG + HTML storage — XSS surface and out of scope |
| 2026-09-26 | Non-owner requesting a draft gets 404, not 403 | Don't leak that the draft exists | 403 — reveals existence |
| 2026-09-26 | Self-likes blocked (BR-03) | Brief says "other logged-in users can like" | Allowing — pending confirmation |
| 2026-09-26 | snake_case JSON end to end | One convention; no conversion bugs | camelCase transform layer |
| 2026-09-26 | Tests on PostgreSQL, not SQLite | Enum, cascade and uniqueness behaviour must match runtime | SQLite in-memory — faster but diverges |
| 2026-09-28 | v2: DB-backed import queue (`FOR UPDATE SKIP LOCKED`) + separate worker container | Durable across restarts, no extra broker, parsing off the API process | FastAPI BackgroundTasks — lost on restart, competes with requests; Celery/arq — extra moving parts for one job type |
| 2026-09-28 | v2: Redis for cache and rate limits only | One small service covers two syllabus topics | In-process cache/limits — wrong as soon as there are 2 API workers |
| 2026-09-28 | v2: Storage interface with local (default) and MinIO (profile) backends | Local keeps the demo fast; MinIO proves object-storage semantics (keys, presigned URLs) | S3 only — needs cloud creds; local only — misses the topic |
| 2026-09-28 | v2: .docx via mammoth → HTML → markdownify; .pdf via pdfplumber | Permissive licences; mammoth maps Word styles to semantic headings | PyMuPDF — AGPL licence; python-docx alone — manual style mapping |
| 2026-09-28 | v2: PDF export via reportlab | Pure Python, no system packages in the image | WeasyPrint — needs Pango/Cairo system libs |
| 2026-09-28 | v2: openpyxl in write-only mode for XLSX | Constant memory for large sheets | Normal mode — holds the whole workbook in memory |
| 2026-09-28 | v2: Version-bump cache invalidation | Can't forget a key; stale keys just expire | Deleting keys per change — easy to miss filtered-feed keys |
| 2026-09-28 | v2: Rate limiter fails open if Redis is down (logged at WARNING) | Availability of reads beats strict limiting for a blog | Fail closed — Redis blip takes the site down |
| 2026-09-28 | v2: Imported posts always land as drafts | PDF conversion is lossy; the author must review | Auto-publish — publishes broken formatting under their name |
| 2026-09-28 | v2: Offset pagination kept for the UI; keyset measured only in performance.md | Numbered pages are in design.md; keyset shown as the fix for deep pages | Switching UI to cursor pagination — design change mid-week |
| 2026-09-28 | v3: Tenant = publication (personal + team) | A blog needs a real "unit with members" for multi-tenancy; mirrors Medium/Substack publications | Tenant = user (no members, trivial); subdomain tenants (DNS/cookie complexity locally) |
| 2026-09-28 | v3: Tenant context from URL path only | Explicit, testable, visible in logs; no spoofable header | `X-Tenant` header; tenant claim in JWT (stale after role change) |
| 2026-09-28 | v3: Never auto-link accounts by email | Some providers return unverified or mutable email claims → account-takeover risk | Auto-link on `email_verified` — trusts the provider's claim too much |
| 2026-09-28 | v3: 15-min access JWT + rotating refresh with family revocation | Revocable sessions, theft detection, still stateless on most requests | Server-side sessions only (fine, but misses the JWT topic); long-lived JWT (no revocation) |
| 2026-09-28 | v3: Authlib as OIDC client; local fake OIDC provider for tests | Handles JWKS, PKCE, nonce; tests never hit real providers | Hand-rolled OIDC — easy to miss a validation step |
| 2026-09-28 | v3: Apple sign-in is Could | Paid developer account + HTTPS redirect required | Must — could burn a day on setup |
| 2026-09-28 | v4: Permission checks with role→permission mapping in code (`roles.py`) | Reviewable in PRs, unit-testable, generated docs | DB-driven custom roles — privilege-escalation surface and admin UI we don't need |
| 2026-09-28 | v4: Platform roles (moderator, admin) separate from publication roles and never grant tenant content permissions | Least privilege; admins moderate the platform, not publications' private work | Superuser admin — simplest but violates least privilege |
| 2026-09-28 | v4: Admin granted only via CLI | Removes the "compromised admin creates more admins" path | API endpoint for admin grants |
| 2026-09-28 | v4: One `audit_log` table replaces planned `auth_events` | One viewer, one retention job, one query model | Separate tables per category |
| 2026-09-28 | v4: Append-only enforced by Postgres grants + separate DB roles | Enforced even if app code is buggy | App-level discipline only |
| 2026-09-28 | v4: One backend image for api and worker; nginx-unprivileged for web | Fewer images to build/scan; non-root by default | Separate worker image; Vite preview server in prod |
| 2026-09-28 | v4: Frontend runtime config via `config.js` written at container start | Build once, run anywhere — `VITE_*` values are baked at build time | Rebuild per environment |
| 2026-09-28 | v4: GlitchTip (self-hosted, Sentry SDK) under `obs` profile | No external account; switch to Sentry SaaS by changing DSN | Sentry SaaS only — needs signup |
| 2026-09-28 | v4: Prometheus + Grafana under `obs` profile, dashboards as code | Metrics topic proven locally; reproducible dashboards | Hosted APM |
| 2026-09-28 | v4: Daily `pg_dump -Fc` + uploads archive + scripted restore drill | Proves recovery, not just backup | WAL archiving/PITR — out of scope for a week |
| 2026-09-28 | v5: Introduce a repository layer and feature modules (REVERSES the v1 "no repository layer" decision) | Syllabus requires MVC repositories/boundaries; the codebase is now large enough that services mixing SQL and rules are hard to test | Keep layered folders without repositories — fails B7/B8; big-bang rewrite — too risky, so move-only commits with tests green |
| 2026-09-28 | v5: Boundaries enforced by import-linter | Rules that aren't checked decay | Code review only |
| 2026-09-28 | v5: API v2 only for posts/comments/likes | Demonstrates versioning without migrating 80+ routes | Full v2 — a week on its own |
| 2026-09-28 | v5: RFC 9457 problem+json in v2, v1 envelope untouched | Standard format; changing v1's error shape would be a breaking change | Changing v1 in place |
| 2026-09-28 | v5: Cursor pagination in v2, offset stays in v1 | Stable under inserts, uses the composite index (v2 perf evidence) | Offset everywhere |
| 2026-09-28 | v5: `If-Match` required on v2 PATCH/DELETE | Prevents lost updates between editors in team publications | Last-write-wins |
| 2026-09-28 | v5: Anthropic via official SDK; Dev.to and GitHub via raw httpx through one resilient client | Contrast SDK vs raw HTTP; SDK handles auth/streaming/types, raw HTTP gives full control over retries and mapping | SDKs everywhere (PyGithub etc.) — hides the HTTP topics |
| 2026-09-28 | v5: AI suggests only title/excerpt/SEO description, never body | Keeps authorship human; small, cheap, reviewable outputs | AI drafting posts — out of scope |
| 2026-09-28 | v5: Dev.to as cross-post target | Public API with per-user API keys; developer audience fits | Medium — API closed to new integrations (as far as known); Hashnode — GraphQL adds a second API style |
| 2026-09-28 | v5: GitHub OAuth App, public repos only, minimal scope | Avoids the broad `repo` scope; reading public content needs no scope | GitHub App — better least privilege but more setup (installation tokens, JWT); consider if time allows |
| 2026-09-28 | v5: Outbound webhook signing `t=…,v1=…` HMAC with timestamp | Replay protection, familiar pattern for integrators | Unsigned or body-only HMAC |
| 2026-09-28 | v5: User integration credentials encrypted with AES-GCM + key ids | Rotation without downtime; DB dump alone leaks nothing usable | Plaintext or hashing (can't hash — we need the value) |
| 2026-09-28 | v4: "CD" = GHCR release + scripted deploy to prod-like compose | No hosting target in scope; still demonstrates promote-by-tag, migrate, health-gated rollback | Real cloud deploy — out of scope (open question in product.md) |

## Gotchas & non-obvious behaviour
- (anticipated) `fetch` does not send cookies cross-origin without `credentials: 'include'`; set it once in `src/api/client.ts`.
- (anticipated) If CORS is ever used with credentials, `allow_origins=["*"]` is rejected by browsers — list exact origins.
- (anticipated) Inside Docker the Vite proxy target is `http://api:8000`, not `localhost:8000`.
- (anticipated) `Secure` cookies are dropped on plain http://localhost in some browsers — keep `COOKIE_SECURE=false` locally.
- (anticipated) Alembic autogenerate misses Postgres enum changes and some server defaults — review every generated migration.
- (anticipated) Use timezone-aware UTC datetimes (`datetime.now(UTC)`); naive datetimes break comparisons with `timestamptz`.
- (anticipated) Counting likes/comments per post in a loop causes N+1 — use one grouped subquery in the feed query.

- (anticipated, v2) FastAPI needs `python-multipart` installed for `UploadFile`/form fields; without it the app fails at startup.
- (anticipated, v2) Uvicorn has no request-body size limit — enforce it in our streaming loop; check `Content-Length` first as a cheap early reject, but never rely on it.
- (anticipated, v2) Starlette spools `UploadFile` to disk above ~1 MB; the size check must still happen while reading.
- (anticipated, v2) `fetch()` has no upload progress events — uploads use XMLHttpRequest in `src/api/uploads.ts`.
- (anticipated, v2) MinIO presigned URLs are signed for the host you configured; a URL signed for `minio:9000` is unreachable from the browser. Sign with `S3_ENDPOINT_PUBLIC`.
- (anticipated, v2) A .docx is a ZIP — check entry count and uncompressed size before extracting (zip bomb).
- (anticipated, v2) GZip on PDF/XLSX/ZIP wastes CPU for no gain — exclude them.
- (anticipated, v2) `StreamingResponse` generators may run after the request-scoped DB session is closed, depending on FastAPI version — open a dedicated session inside the export generator and verify with a 10k-row export.
- (anticipated, v2) `pg_trgm` must be enabled in a migration (`CREATE EXTENSION IF NOT EXISTS pg_trgm`) before the GIN index.
- (anticipated, v2) Postgres does not index foreign-key columns automatically.
- (anticipated, v2) `EXPLAIN ANALYZE` actually executes the statement — never run it on DELETE/UPDATE without wrapping in a rolled-back transaction.
- (anticipated, v2) Run `ANALYZE` after `make seed-perf`, or the planner uses stale statistics and plans lie.
- (anticipated, v2) Behind Docker, `request.client.host` is the proxy/container IP unless proxy headers are configured — rate limits keyed on IP will lump everyone together. Configure `--proxy-headers --forwarded-allow-ips` deliberately.
- (anticipated, v2) ETags must be computed from the cached (non-personalised) body, otherwise every logged-in user gets a different ETag and 304s never happen.

- (anticipated, v3) Apple returns to the callback via cross-site POST (`form_post`); a `SameSite=Lax` state cookie is not sent → use `SameSite=None; Secure` for that cookie (HTTPS only).
- (anticipated, v3) Apple sends the user's name only on the very first authorisation — store it then.
- (anticipated, v3) Microsoft `common` endpoint: the `iss` claim contains the user's tenant id; validate against the per-tenant issuer template, not a fixed string.
- (anticipated, v3) Parallel requests hitting 401 at once must share one refresh call, or rotation will look like token reuse and revoke the family.
- (anticipated, v3) Scope the refresh cookie `Path=/api/v1/auth/refresh` so it is not sent with every request.
- (anticipated, v4) Any `VITE_*` value is baked into the JS bundle at build time — anything environment-specific must come from `config.js` at runtime.
- (anticipated, v4) `depends_on: condition: service_healthy` does nothing useful unless the dependency defines a `healthcheck`.
- (anticipated, v4) Tables created by `blog_migrator` are not visible to `blog_app` unless `ALTER DEFAULT PRIVILEGES` was set first — and `audit_log` must then have UPDATE/DELETE explicitly revoked from `blog_app`.
- (anticipated, v4) prometheus-client with multiple uvicorn workers needs multiprocess mode (`PROMETHEUS_MULTIPROC_DIR` on a writable tmpfs), otherwise each scrape sees one worker.
- (anticipated, v4) Read-only root filesystem breaks anything writing to `/tmp` or `~/.cache` — mount tmpfs and set `HOME`/cache dirs explicitly.
- (anticipated, v4) nginx-unprivileged listens on 8080, not 80.
- (anticipated, v4) `pg_dump` must be the same or newer major version than the server — run it from the `postgres:16` image.
- (anticipated, v4) Docker HEALTHCHECK and Prometheus hit health/metrics constantly — exclude them from access logs or they drown everything else.
- (anticipated, v4) Source maps uploaded to GlitchTip/Sentry must not also be served by nginx.

- (anticipated, v5) Webhook HMAC must be computed over the raw request bytes — read `await request.body()` before any JSON parsing; re-serialised JSON will not match.
- (anticipated, v5) GitHub cannot reach localhost: use a smee.io channel (`make smee`) forwarding to the api container; the channel URL is public — treat it as non-secret, the HMAC is the protection.
- (anticipated, v5) Retry multiplication: an SDK with its own retries inside our retry loop can turn 3 attempts into 9 — configure the SDK's retries explicitly in the adapter.
- (anticipated, v5) httpx's default timeout is short and it never retries by itself — always go through `integrations/http.py`.
- (anticipated, v5) SSRF guards that check the hostname but let the HTTP client re-resolve DNS are bypassable (DNS rebinding) — connect to the vetted IP.
- (anticipated, v5) openapi-typescript output churns if `operation_id`s are auto-generated from function names — set them explicitly.
- (anticipated, v5) Idempotency keys need a lock while the first request is in flight, otherwise two concurrent retries both execute.
- (anticipated, v5) Moving files between modules breaks Alembic's model imports and pytest fixtures' import paths — update `alembic/env.py` model imports in the same commit.
- (anticipated, v5) Weak ETags (`W/`) are not valid for `If-Match` comparisons — v2 uses strong ETags.

## Things that were tried and failed
- (none yet)

## Environment / access notes
- Everything runs locally via Docker Compose; no cloud accounts or credentials involved.
- `.env` is git-ignored; `.env.example` must stay in sync whenever a new setting is added.

## Stakeholder context
- Assessed by bootcamp reviewers through three things: the repo README, the docs, and a 2-minute video. A reviewer who can't run it in 5 minutes will judge the whole project on that.
- Seed data is part of the product — the demo depends on it looking realistic.
- (v5) The v5 syllabus lists foundation topics (16) plus MVC/REST/integration topics (34). Many foundations are already true of the repo; the assessment value is making them visible (engineering.md) and enforced (tooling), not rebuilding them.
- (v4) Weeks 3–4 add 8 + 20 syllabus topics. RBAC topics overlap week 3 by design — week 4 refactors role checks into permissions rather than rebuilding them.
- (v2) Week-2 assessment is against a syllabus of 23 topics. Reviewers will look for each one; docs/TOPICS.md is the map that lets them find it in seconds.
