# Syllabus coverage — Blog Platform

## Week 2 — File Uploads, File Handling & Exporting | API Optimisation, Indexing & Database Performance

_Claude: fill the "Proof" column as tasks finish — a test name (`tests/...::test_x`) or a docs/performance.md section. A topic without proof is not done._

| # | Topic | Where it lives in this app | Task | Proof |
|---|---|---|---|---|
| 1 | Multipart/Form-Data | `POST /imports` accepts `multipart/form-data`, field `files` (1–5) | T-024, T-035 | |
| 2 | Validation | Magic-byte sniffing, zip-bomb guard, encrypted/scanned PDF detection, Pydantic on all JSON | T-024, T-025 | |
| 3 | File Size/Type Limits | 10 MB/file enforced while streaming, 5 files, 50 pages, .docx/.pdf only (BR-17, BR-18) | T-024 | |
| 4 | Local vs Object Storage | `StorageBackend` with local volume and MinIO (S3 API); one contract test suite for both | T-021, T-023 | |
| 5 | File Naming | Server-generated keys `uploads/{user}/{yyyy}/{mm}/{uuid}.{ext}`; sanitised display name; RFC 5987 `filename*` | T-023, T-026 | |
| 6 | Streaming | Chunked upload to storage; `StreamingResponse` for originals and CSV export with server-side cursor | T-024, T-027 | |
| 7 | Buffers | 64 KB chunk buffer, incremental SHA-256, SpooledTemporaryFile behaviour, flat-memory proof for 10 MB upload | T-024 | |
| 8 | Reading/Writing Files | .docx → Markdown (mammoth + markdownify), .pdf → text (pdfplumber); writing CSV/XLSX/PDF | T-025, T-027 | |
| 9 | Temporary Files | Worker temp dir per job; export temp files removed by BackgroundTask; no leftovers after failures | T-025, T-027 | |
| 10 | Secure Downloads | Owner-only, 5-minute HMAC-signed links / S3 presigned URLs; `attachment` + `nosniff` | T-026 | |
| 11 | CSV/PDF/Excel Export | `posts.csv` (streamed), `posts.xlsx` (write-only), `export.pdf` per post | T-027 | |
| 12 | API Bottlenecks | Server-Timing + query-count headers; parsing moved to worker; Locust before/after | T-021, T-022, T-037 | |
| 13 | Payload Reduction | Excerpt not body in lists, `fields=` sparse fieldsets, page_size cap, 304s, gzip | T-030, T-031, T-033 | |
| 14 | Filtering | author, date range, title contains (trigram), source, sort whitelist | T-030 | |
| 15 | Caching Concepts | Redis cache-aside, TTL, version-bump invalidation, ETag/304, Cache-Control, Vary | T-031 | |
| 16 | Batching | Multi-file upload, batch publish/delete, batched `liked_by_me`, bulk-insert perf seed | T-022, T-024, T-028, T-034 | |
| 17 | N+1 Queries | Query-count assertions on every list endpoint; before/after counts | T-028 | |
| 18 | Eager/Lazy Loading | `lazy="raise"` default; `selectinload` vs `joinedload` chosen per relationship | T-028 | |
| 19 | Indexes | FK indexes, trigram GIN on title, partial indexes on imports | T-029 | |
| 20 | Composite Indexes | `(author_id, status, published_at DESC)`; leftmost-prefix demonstration | T-029 | |
| 21 | EXPLAIN / EXPLAIN ANALYZE | `make explain` captures plans before/after into docs/perf/plans/ | T-022, T-029 | |
| 22 | Rate Limiting | Redis fixed windows per BR-25; 429 + Retry-After; fail-open | T-032 | |
| 23 | Compression | GZipMiddleware ≥ 1 KB, excludes already-compressed files; bytes measured | T-033 | |

## Week 3 — Authentication, Authorization & Multi-Tenancy

| # | Topic | Where it lives in this app | Task | Proof |
|---|---|---|---|---|
| 1 | Password Hashing | argon2id, parameter upgrade on login, dummy verify for unknown emails (BR-38) | T-041 | |
| 2 | Sessions/JWT | 15-min access JWT + rotating refresh, family revocation, `kid` key rotation, sessions list (BR-39, BR-40, BR-53) | T-042, T-048 | |
| 3 | Authentication vs Authorization | 401 vs 403 vs 404 contract; OIDC for identity, permissions for access (BR-41) | T-044, T-045, T-051 | |
| 4 | Tenant Context | Publication resolved from `/pubs/{slug}` path by dependency (BR-45) | T-049, T-050 | |
| 5 | Resource Ownership | Posts owned by publication, likes/comments by user; IDOR suite → 404 (BR-46, BR-48) | T-050–T-052 | |
| 6 | Middleware/Dependencies | Request-ID, security headers, Origin check middleware; auth/tenant/permission dependency chain; route audit (BR-56) | T-044 | |
| 7 | Secure Secrets | `SecretStr`, startup validation, Docker secrets, gitleaks, no `VITE_` secrets (BR-51, BR-52) | T-043 | |
| 8 | CORS | Credentialed allowlist, second-origin demo, preflight tests (BR-54, BR-55) | T-053 | |

## Week 4 — Role-Based Access Control Implementation | DevOps, Containers & Observability

| # | Topic | Where it lives in this app | Task | Proof |
|---|---|---|---|---|
| 1 | Roles | Publication roles writer/editor/owner + platform moderator/admin + implicit member (BR-61) | T-061, T-065 | |
| 2 | Permissions | `resource:action[:scope]` catalogue in `app/authz/permissions.py` (BR-59, BR-60) | T-061 | |
| 3 | Role-Permission Mapping | `roles.py` = BR-61 table; generated `docs/permissions.md`; parity test | T-061 | |
| 4 | Guards | `require_permission()` dependencies; frontend `<RequirePermission>` route guards (BR-63) | T-062, T-068 | |
| 5 | Middleware/Dependencies | Fixed guard chain authn → suspended → tenant → resource → permission; route audit | T-062 | |
| 6 | Ownership Rules | `own` vs `any` scopes; hide-not-delete moderation keeps ownership (BR-60, BR-68) | T-062, T-066 | |
| 7 | Tenant-Aware Authorization | Effective permissions per publication; platform perms never grant tenant content (BR-62, BR-66) | T-063 | |
| 8 | Least Privilege | Minimal role bundles, admin via CLI only, separate Postgres roles, non-root read-only containers (BR-64, BR-65, BR-76) | T-064, T-065, T-069 | |
| 9 | Permission-Based UI | `/me/permissions` + `useCan`/`<Can>`; role × screen test (BR-73) | T-068 | |
| 10 | Audit Logs | Append-only `audit_log` via DB grants, in-transaction writes, viewers + CSV (BR-70–BR-72) | T-067 | |
| 11 | Docker | Multi-stage, non-root images; shared api/worker image; size budgets | T-069 | |
| 12 | Docker Compose | Base + dev + prod files, profiles, healthcheck-gated startup, migrate one-shot, networks | T-070 | |
| 13 | Build vs Runtime | Build args only for SHA/time; `config.js` runtime config; same image everywhere (BR-75) | T-069, T-071 | |
| 14 | Environment Configuration | `ENV=local|ci|prod`, validated `Settings`, `.env.example` parity test (BR-74) | T-071 | |
| 15 | CI/CD Concepts | CI gate (BR-82); tag-based release to GHCR; scripted deploy with ready-gated rollback (BR-83) | T-077, T-078 | |
| 16 | Health Checks | `/health/live`, `/health/ready`, worker heartbeat, Docker HEALTHCHECK (BR-77) | T-072 | |
| 17 | Logs | JSON logs, request-ID correlation api ↔ worker, redaction (BR-78) | T-073 | |
| 18 | Metrics | Prometheus RED + business metrics, Grafana dashboards as code (BR-79) | T-074, T-079 | |
| 19 | Error Tracking | Sentry SDK → GlitchTip, release tagging, PII scrubbing (BR-80) | T-075 | |
| 20 | Database Backups | Daily `pg_dump` + uploads, retention, scripted restore drill (BR-81) | T-076 | |

## v5a — Engineering Foundations & Project Setup (IDs F1–F16)

| # | Topic | Where it lives in this app | Task | Proof |
|---|---|---|---|---|
| F1 | SDLC | docs/engineering.md maps each phase to an artifact: product.md → architecture.md/design.md → tasks.md → tests/CI → release tags → dashboards/runbooks → memory.md | T-081 | |
| F2 | Git/GitHub Workflow | Trunk-based flow, protected `main`, required checks, CODEOWNERS, squash merges (rules.md Git workflow) | T-082 | |
| F3 | Branching | `feat/T-XXX-…` short-lived branches, hotfix-from-tag flow | T-082 | |
| F4 | Commits | Conventional Commits + task ID, enforced by commitlint (pre-commit + CI); CHANGELOG generated from them | T-082 | |
| F5 | Pull Requests | PR template (task, what/why, test evidence, migration/rollback), ≤ 400-line guideline, green CI gate | T-082 | |
| F6 | Terminal | Makefile as the single command interface, `make help`, strict-mode shell scripts, shellcheck | T-082 | |
| F7 | Package Managers | uv + `uv.lock`, npm + `package-lock.json`, frozen installs, drift check, Dependabot | T-083 | |
| F8 | Environment Variables | Typed `Settings`, `.env.example` parity test, secrets vs config (BR-51, BR-74, BR-75) | T-071 (v4) | |
| F9 | Project Structure | Monorepo layout + feature modules (`app/modules/<feature>/`) | T-084 | |
| F10 | Client-Server Architecture | SPA client ↔ FastAPI server ↔ Postgres/Redis/storage; diagram in engineering.md | T-081 | |
| F11 | Frontend vs Backend | Responsibility table in engineering.md (UI state vs enforcement); generated typed client | T-081, T-087 | |
| F12 | HTTP Basics | Methods, status codes, headers, caching, cookies explained with this app's real requests | T-081 | |
| F13 | Request/Response Lifecycle | Traced path: browser → nginx → middleware order → controller → guards → service → repository → DB → view → headers | T-081 | |
| F14 | DNS | Docker embedded DNS (service names), `localhost` vs container names, SSRF guard resolving DNS (BR-108) | T-081, T-092 | |
| F15 | Ports | Port map (host vs container, dev vs prod, privileged vs unprivileged) in engineering.md | T-081 | |
| F16 | Frontend-Backend Communication | Vite proxy (dev) / nginx (prod), cookies + CSRF/CORS rules, generated client, error handling on the client | T-081, T-087 | |

## v5b — Backend Architecture & MVC | REST API Design | Third-Party API Integration (IDs B1–B34)

| # | Topic | Where it lives in this app | Task | Proof |
|---|---|---|---|---|
| B1 | MVC Architecture | MVC mapping for an API backend (BR-94, architecture.md) | T-084 | |
| B2 | Models in MVC | `modules/*/models.py` (ORM) + repositories | T-084, T-085 | |
| B3 | Views in MVC | `modules/*/schemas.py` response models (API representation) + React UI | T-084, T-087 | |
| B4 | Controllers in MVC | `modules/*/router.py` — thin FastAPI routers | T-084 | |
| B5 | Routes in REST APIs | v2 resource routes, operation ids, versioned routers | T-089, T-090 | |
| B6 | Services in MVC | `modules/*/service.py` — business rules, fastapi-free, unit-tested with fakes | T-085, T-086 | |
| B7 | Repositories in MVC | `modules/*/repository.py` — all SQL | T-085 | |
| B8 | Dependency Boundaries in MVC | import-linter contracts in CI; `ports.py` for integrations | T-086 | |
| B9 | Separation of Concerns in MVC | Layer rules (rules.md Architecture & layering) | T-084–T-086 | |
| B10 | Modular Project Structure | Feature modules with public `__init__` interfaces | T-084 | |
| B11 | FastAPI/Django REST Project Architecture | App factory, versioned routers, dependency injection, settings, modules (architecture.md) | T-084 | |
| B12 | REST Principles | Resource orientation, statelessness, uniform interface, cacheability (ETag), v2 rules | T-088, T-089 | |
| B13 | Resources in REST APIs | posts, comments, likes as v2 resources; non-resource endpoints listed explicitly | T-089, T-090 | |
| B14 | HTTP Methods in REST APIs | GET/POST/PUT/PATCH/DELETE semantics, safety and idempotency (rules.md REST) | T-089, T-090 | |
| B15 | Status Codes in REST APIs | BR-86 table, contract tests per route | T-088, T-089 | |
| B16 | URI Design in REST APIs | Plural nouns, ≤ 1 nesting level, no verbs, state via PATCH | T-089, T-090 | |
| B17 | Path/Query Parameters in REST APIs | ids in path; filters/sort/pagination in query; unknown params → 400 | T-088, T-089 | |
| B18 | Request/Response Bodies in REST APIs | JSON only, `extra="forbid"`, unwrapped single resources, list envelope (BR-91) | T-088, T-087 | |
| B19 | Pagination in REST APIs | Cursor pagination + `Link` header (BR-88); offset kept in v1 | T-088 | |
| B20 | Filtering in REST APIs | Field-named params, `_after/_before` ranges (BR-90) | T-088, T-089 | |
| B21 | Sorting in REST APIs | `sort=-published_at,title` whitelist + id tie-break (BR-89) | T-088 | |
| B22 | Versioning in REST APIs | `/api/v1` → `/api/v2`, Deprecation/Sunset headers, usage-gated removal (BR-84, BR-85) | T-091 | |
| B23 | Error Formats in REST APIs | RFC 9457 problem+json in v2 vs v1 envelope (BR-87) | T-088 | |
| B24 | External APIs | Anthropic, Dev.to, GitHub adapters under `app/integrations/` | T-092–T-097 | |
| B25 | API Keys | Consuming: Anthropic (platform key), Dev.to (user key, encrypted); issuing: personal access tokens (Could) | T-093–T-095, T-099 | |
| B26 | OAuth2 | GitHub delegated access: authorization code + state, minimal scope, token storage, revocation (BR-101) | T-096 | |
| B27 | SDKs vs Raw HTTP | Anthropic via official SDK vs Dev.to/GitHub via raw httpx — trade-offs recorded in memory.md | T-094, T-095 | |
| B28 | Request/Response Mapping | Our post ↔ provider request/response payloads in `mapper.py` | T-094, T-095 | |
| B29 | Timeouts in API Integrations | Connect/read timeouts, AI 30 s budget, 504 mapping (BR-96) | T-092, T-094 | |
| B30 | Retries in API Integrations | Idempotency-aware retries, full-jitter backoff, no retry multiplication with SDK retries (BR-96) | T-092 | |
| B31 | Rate Limits in API Integrations | Per-provider token buckets, `Retry-After`, deferral (BR-97) | T-092, T-095 | |
| B32 | Webhooks in API Integrations | Inbound GitHub (verify, dedupe, 202) and outbound publication webhooks (sign, retry, log) (BR-103, BR-106, BR-107) | T-097, T-098 | |
| B33 | Data Mapping in API Integrations | Front matter → post, post → Dev.to article, canonical URL rules (BR-99, BR-102, BR-104) | T-095, T-097 | |
| B34 | Secrets in API Integrations | Platform secrets in env/Docker secrets; user credentials AES-GCM encrypted with key rotation; webhook secrets shown once (BR-100, BR-106) | T-093, T-096, T-098 | |
