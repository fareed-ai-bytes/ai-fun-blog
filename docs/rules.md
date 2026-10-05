# Rules — Blog Platform
<!-- Every rule must be verifiable. -->

## Coding rules
### Style
- Backend: Python 3.12, `ruff format` + `ruff check` (line length 100), type hints on every function signature.
- Frontend: TypeScript `strict: true`, ESLint + Prettier, 2-space indent, no `any` (use `unknown` + narrowing).
- Naming: Python `snake_case` functions/modules, `PascalCase` classes. React components `PascalCase.tsx`, hooks `useThing.ts`.
- JSON fields are `snake_case` end to end — the frontend types mirror API schemas; no camelCase conversion layer.

### Structure
- Routers (`app/api/v1/`) contain no business logic: validate → call one service function → return a schema. Handlers ≤ 15 lines.
- Every ownership and visibility check lives in `app/services/`. A frontend check is UX only and never the enforcement.
- Routers never return ORM objects — always a Pydantic response model (`response_model=` set on every route).
- Frontend makes HTTP calls only through `src/api/`; no `fetch()` inside components or pages.
- Server data lives in TanStack Query; no global store (Redux/Zustand) for server data.
- Functions over 50 lines must be split.
- (v2) Document parsing libraries (mammoth, markdownify, pdfplumber) are imported only under `app/importers/` and run only in the worker — never in a request handler.
- (v2) Storage is accessed only through `app/storage/`; no `open()` on upload paths or boto3 calls anywhere else.
- (v2) Redis is accessed only through `cache_service` and `ratelimit_service`; cache keys are built only in `cache_service`.

### File handling (v2)
- Never trust the client filename, extension or `Content-Type`; the file type is decided by magic bytes in `importers/sniff.py` (PDF `%PDF-`; DOCX = ZIP `PK\x03\x04` containing `word/document.xml`).
- Never call `await file.read()` without a size; read in `CHUNK_SIZE = 64 * 1024` chunks and abort as soon as the running total exceeds the limit.
- Never build a filesystem path or storage key from user input. Keys come from `storage/naming.py`: `uploads/{user_id}/{yyyy}/{mm}/{uuid4}.{detected_ext}`.
- The original filename is sanitised (basename only, NFC, control characters removed, ≤ 255) and stored for display only. Downloads set `Content-Disposition: attachment; filename="<ascii fallback>"; filename*=UTF-8''<encoded>` and `X-Content-Type-Options: nosniff`.
- Uploaded files are never served from a static or public path — only via `/files/{token}` or an S3 presigned URL.
- Temp files only via `tempfile` inside `TMP_DIR`, inside a `with` block or `try/finally` that deletes them. Export temp files are deleted by a response `BackgroundTask`.
- Before parsing a .docx, check the ZIP: ≤ 1,000 entries and ≤ 50 MB total uncompressed size (zip-bomb guard).

### Performance (v2)
- ORM relationships are declared `lazy="raise"`; every load is explicit (`selectinload` for collections, `joinedload` for many-to-one).
- Every list endpoint has a test asserting a constant query count for page sizes 1 and 50 (`assert_max_queries` fixture).
- `liked_by_me` / `can_delete` for a page are fetched in one `WHERE post_id IN (…)` query, never per item.
- Any new or changed query on posts/likes/comments/imports needs `EXPLAIN (ANALYZE, BUFFERS)` output against the perf dataset in docs/performance.md, before and after.
- Every index is created in an Alembic migration and justified by a plan in docs/performance.md. No speculative indexes.
- `page_size` ≤ 50 everywhere; `fields` and `sort` values come from explicit whitelists.
- Never cache a response containing per-user fields.

### Authorisation (v4)
- All authorisation goes through `app/authz/`. Routes declare `Depends(require_permission(P.POST_UPDATE))`; services call `policy.can(...)` for resource-level checks. No `role ==` / `role in` comparisons anywhere outside `app/authz/roles.py` — enforced by a grep test in `make lint`.
- Permission names exist only as constants in `app/authz/permissions.py`; no string literals of permissions elsewhere (backend) — frontend imports the list generated into `src/authz/permissions.ts`.
- A new permission is mapped to no role until `roles.py` is changed explicitly in the same PR, and `make permissions-doc` is re-run.
- The route-audit test (BR-56) additionally requires every non-public route to declare exactly one `require_permission` guard or be marked `authenticated_only`.
- Frontend: show/hide actions only via `useCan(permission, resource?)` or `<Can>`; never on role names (ESLint `no-restricted-syntax` rule).

### Containers & operations (v4)
- Dockerfiles: multi-stage; base images pinned to a specific version tag (never `latest`); runtime stage runs as a non-root user; no build tools, tests or `.env` in the runtime image; `hadolint` clean.
- Secrets never go through `ARG`/`ENV` in a Dockerfile or `build.args` in compose — only runtime env vars or Docker secrets.
- Every compose service has a `healthcheck`; `depends_on` always uses `condition: service_healthy` or `service_completed_successfully`.
- `compose.prod.yaml` publishes no ports for db, redis, prometheus or internal services.
- Every setting lives in the `Settings` class; a test fails if a field is missing from `.env.example` or vice versa.
- Migrations follow expand/contract: a migration may not break the previous release's code (no drop/rename of a column still read by the previous tag).
- Metric names: `blog_` prefix, snake_case, unit suffix (`_seconds`, `_bytes`, `_total`); labels never contain user ids, emails, slugs or raw paths (use route templates).

### Architecture & layering (v5)
- Backend code is organised by feature module: `app/modules/<feature>/` containing `router.py` (controller), `schemas.py` (view / API representation), `service.py` (business rules), `repository.py` (data access), `models.py` (ORM), optional `mappers.py`, `ports.py`.
- Allowed dependencies (enforced by import-linter in `make lint`): router → own service + schemas + `core`/`authz`/`tenancy`; service → own repository, own `ports.py`, other modules' **service** only (never another module's repository or models); repository → own models + `db`; `app/integrations/*` → `core` + HTTP client/SDK and the port they implement — never `modules/*` internals.
- Routers contain no SQLAlchemy and no business logic; services import nothing from `fastapi` (no `Request`, `HTTPException`, `Depends`); repositories contain no permission checks and return ORM/domain objects, never Pydantic API schemas.
- Every SQL query lives in a repository. Services are unit-tested with fake repositories; repositories are tested against Postgres.
- Cross-module calls go through the other module's service functions listed in its `__init__.py` (`__all__`) — that is the module's public interface.
- Frontend calls the API only through the client generated from OpenAPI (`make gen-client`); hand-written request/response types for API data are not allowed.

### REST API design (v5 — applies to `/api/v2`; v1 is frozen except for security fixes)
- URIs: plural lowercase nouns, kebab-case, identifiers in the path, at most one level of nesting (`/posts/{id}/comments`), no verbs. State changes are field updates via PATCH (e.g. `status: "published"`), not action URLs. The few documented action endpoints (auth flows, batch, download links) are listed in `docs/api.md` under "Non-resource endpoints".
- Methods: GET safe; PUT and DELETE idempotent; PATCH = JSON Merge Patch semantics; POST creates → `201` + `Location`; accepted async work → `202` + `Location` of the job.
- Every route declares `response_model`, explicit `status_code`, `operation_id` (`<resource>_<action>`), summary, and all error responses it can return — the generated client depends on it.
- Request models use `extra="forbid"`; response models never expose internal fields (hashes, storage keys, encrypted tokens, `token_version`).
- Query parameters are validated against per-resource whitelists; unknown parameters → 400.

### Third-party integrations (v5)
- All outbound HTTP goes through `app/integrations/http.py` (shared httpx client with timeouts, retries, backoff, `Retry-After`, per-provider token bucket, logging, metrics). No `httpx.get(...)`/`requests` calls elsewhere (grep test). SDK clients (Anthropic) are constructed only in their adapter, with SDK-level retries disabled or set so total attempts never exceed BR-97.
- Each provider adapter lives in `app/integrations/<provider>/` with `client.py`, `mapper.py` (pure functions, fixture tests), `errors.py` (provider errors → our `UpstreamError` subclasses).
- Tests never call real providers: httpx is mocked with `respx`; recorded provider payloads live in `tests/fixtures/providers/<provider>/`.
- Integration secrets are read only through `Settings` (platform secrets) or `crypto_service.decrypt()` at the moment of use (user credentials); decrypted values never leave the adapter call scope.

### Error handling & logging
- Services raise domain exceptions from `app/core/errors.py` (`NotFound`, `Forbidden`, `Conflict`, `Unauthorized`). Services never raise `HTTPException`.
- One exception handler maps domain exceptions to the error envelope in architecture.md.
- Never swallow exceptions; log with context and re-raise or map.
- Use `logging.getLogger(__name__)`; no `print()`.
- (v4) Log fields go in `extra={...}`, never interpolated into the message; the JSON formatter's redaction filter must stay in the handler chain (test).
- (v4) Unhandled exceptions are reported to error tracking once, at the boundary (exception handler / worker loop) — never `capture_exception` scattered in services.
- Never log passwords, password hashes, JWTs, cookies or full request bodies of auth endpoints.

### Testing
- Every endpoint has tests for: happy path, 401 (if auth required), 403 (if ownership applies), 404 visibility (if drafts are involved), 422 on one invalid input.
- Every business rule BR-xx below has at least one test whose name contains its ID (e.g. `test_br03_cannot_like_own_post`).
- Tests run against PostgreSQL (`TEST_DATABASE_URL`); each test runs in a transaction that is rolled back.
- Run `make test-api` and `make lint` before declaring any task done; report the result.
- Never skip, xfail or delete a failing test to get green — fix the code or ask.

### Dependencies
- (v5) Pre-approved additions: httpx (already transitively present), respx, anthropic, cryptography, import-linter, openapi-typescript (dev), @commitlint/cli + config-conventional (dev), pre-commit.
- (v4) Pre-approved additions: authlib, prometheus-client, python-json-logger, sentry-sdk, @sentry/react.
- Do not add a package without asking first. Pre-approved: fastapi, uvicorn, sqlalchemy, alembic, psycopg, pydantic-settings, pyjwt, pwdlib[argon2], pytest, httpx, ruff; react, react-router, @tanstack/react-query, tailwindcss, shadcn/ui deps, react-markdown, @fontsource/*, vitest, @testing-library/react, playwright.

### Never do
- Never commit secrets, keys or `.env`.
- Never store tokens in localStorage/sessionStorage.
- Never use `dangerouslySetInnerHTML` or `rehype-raw`.
- Never change the DB schema without an Alembic migration; never edit a migration that has been applied.
- Never return `email` or `password_hash` from any endpoint other than `/auth/me` (email only).
- Never build anything listed under "Explicitly out of scope" in product.md.
- Never log file contents, signed URLs or signed tokens.
- Never auto-publish an imported post.

## Business rules
| ID | Rule | Example |
|---|---|---|
| BR-01 | Anonymous users and non-owners can only see `published` posts. A draft requested by anyone but its author returns 404, never 403. | User B GETs A's draft slug → 404 |
| BR-02 | Only the author can edit, publish/unpublish or delete a post. **(v3: superseded by BR-44 — publication editors/owners may also act; keep until T-053 ships)** | User B PATCHes A's post → 403 |
| BR-03 | A user cannot like their own post. (needs confirmation) | Author PUTs like on own post → 403 `CANNOT_LIKE_OWN_POST` |
| BR-04 | One like per user per post; like and unlike are idempotent. | PUT twice → like_count +1 total |
| BR-05 | Likes and new comments are only allowed on published posts. | Like on draft → 404 |
| BR-06 | Authors may comment on their own posts. | Author replies to readers → 201 |
| BR-07 | A comment can be deleted by its author or by the post's author; no one else. | User C deletes B's comment on A's post → 403 |
| BR-08 | `published_at` is set on the first publish only; unpublish + republish keeps the original date. | Published 1 Oct, unpublished, republished 3 Oct → still 1 Oct |
| BR-09 | Unpublishing hides the post and its likes/comments from everyone except the author; nothing is deleted. | Republish → counts reappear |
| BR-10 | Slug = kebab-case of title at creation, suffixed `-2`, `-3`… on collision; it never changes afterwards. | "Hello World" twice → `hello-world`, `hello-world-2` |
| BR-11 | Email is case-insensitive and stored lowercased; username is lowercase `[a-z0-9_]`, 3–30 chars. | `Fareed@X.com` and `fareed@x.com` → 409 on second |
| BR-12 | Login failure returns the same 401 message whether email or password is wrong. | "Invalid email or password" |
| BR-13 | Feed order is `published_at` DESC, then `id`; page size 10 (posts), 20 (comments). | |
| BR-14 | Excerpt = first 280 chars of body with Markdown syntax stripped, cut at a word boundary. | |
| BR-15 | Deleting a post deletes its likes and comments (DB cascade). | |
| BR-16 | Imported posts are always created as `draft`, `source=imported`. The author must publish them. | |
| BR-17 | Accepted import types: .docx and .pdf only, by content. Legacy .doc → `UNSUPPORTED_TYPE` with message "Save as .docx and retry". | |
| BR-18 | Limits: 10 MB per file, 5 files per request, 50 PDF pages, 50,000 chars of converted Markdown, 50 MB uncompressed .docx. | 60-page PDF → `TOO_MANY_PAGES` |
| BR-19 | Same user + same SHA-256 + an earlier `succeeded` import → rejected `DUPLICATE_IMPORT` with that post id. Failed imports can be retried. | |
| BR-20 | Only the uploader can get a download link for an original; links expire after 5 minutes. | |
| BR-21 | Embedded images are removed (warning `IMAGES_REMOVED`). A PDF with < 50 extractable characters fails `NO_TEXT_LAYER` (OCR out of scope). Encrypted PDFs fail `ENCRYPTED_PDF`. | |
| BR-22 | Title = first Heading 1 (.docx) or PDF metadata Title, else first non-empty line ≤ 200 chars (warning `TITLE_GUESSED`). | |
| BR-23 | Deleting a post keeps its import record (`post_id` → null). Deleting an import deletes the stored original, not the post. | |
| BR-24 | CSV/XLSX exports contain only the requester's own posts. PDF export follows BR-01 visibility. | |
| BR-25 | Rate limits: login 5/min per IP and 20/hour per email · register 3/hour per IP · imports 10 files/hour per user · comments 10/min per user · exports 5/min per user · download links 20/hour per user · all anonymous requests 120/min per IP. | 6th login in a minute → 429 + `Retry-After` |
| BR-26 | Batch actions: ≤ 50 ids; each id is checked for ownership and processed independently; one failure never rolls back the others. | |
| BR-27 | Cached anonymous content may be up to 60 s stale; the author always sees their own change immediately (logged-in responses bypass cache). | |
| BR-28 | `original_published_at` is display-only; feed order and filters use platform `published_at`. | |

### v3 — Authentication, authorisation & multi-tenancy
| ID | Rule | Example |
|---|---|---|
| BR-29 | Login methods: email + password (kept), Google, Microsoft (personal and work/school), Yahoo, Apple. Priority: Google & Microsoft Must, Yahoo Should, Apple Could. All use OpenID Connect Authorization Code flow with PKCE, exchanged server-side. | |
| BR-30 | A social identity is keyed by `(provider, sub)` only — never by email. Email from a provider is contact/display data, not an identifier. | User changes their Google email → still the same account |
| BR-31 | Accounts are never linked automatically. If a first-time social login carries an email that already belongs to a local account → `409 ACCOUNT_EXISTS_LINK_REQUIRED`: the user must sign in with their existing method and link from Settings. | Password user signs in with Microsoft using same email → told to log in and link |
| BR-32 | A new social user gets `username` generated from the provider name or email local part (BR-11 format, suffixed `_2`, `_3` on collision) and `display_name` from the provider; both editable in Settings. Apple sends the name only on the first authorisation — store it then or never. | |
| BR-33 | Social-only accounts have no password (`password_hash` null). Password login for them returns the BR-12 generic 401. They may set a password from Settings. | |
| BR-34 | An account must always keep at least one login method. Unlinking the last provider of a password-less account → `409 LAST_LOGIN_METHOD`. | |
| BR-35 | Sensitive actions require re-authentication within the last 10 minutes (`auth_time`): link/unlink provider, set/change password, log out everywhere, delete publication, transfer ownership. Otherwise → `401 REAUTH_REQUIRED`. | |
| BR-36 | OAuth callback must validate: `state` (single use, ≤ 10 min, bound to browser cookie), PKCE verifier, ID-token signature via provider JWKS, `iss`, `aud`, `exp`, `nonce`. Any failure → redirect to `/login?error=OAUTH_FAILED` (generic); the specific reason is logged, not shown. | Replayed `state` → OAUTH_FAILED |
| BR-37 | Post-login redirect target must be a relative path starting with `/` and not `//` or containing `\`; anything else → `/`. | `?next=https://evil.com` → `/` |
| BR-38 | Passwords: argon2id; length 8–128; hashing parameters come from settings; on successful login a hash made with old parameters is re-hashed. Login with an unknown email still performs a dummy verify so response time doesn't reveal whether the email exists. | |
| BR-39 | Sessions: access JWT lives 15 min (HttpOnly cookie); refresh token 7 days sliding, 30 days absolute, stored only as a hash in `sessions`, rotated on every use. Re-use of an already-rotated refresh token revokes that whole session family. Logout revokes the current session; "Log out everywhere" revokes all and bumps `users.token_version`. | Stolen old refresh token used → both attacker and user sessions die |
| BR-40 | JWTs: algorithm pinned per key (`alg` from token header is never trusted), claims `iss`, `aud`, `sub`, `sid`, `iat`, `exp`, `kid` required, 30 s clock leeway. Tokens carry no email, roles or tenant — those are looked up per request. | Token with `alg: none` → 401 |
| BR-41 | Authentication = who you are → `401` when unknown/invalid. Authorisation = what you may do → `403` when known but not allowed. Use `404` instead of `403` whenever the resource's existence must stay hidden (drafts, other tenants' members/invites/drafts). | |
| BR-42 | Tenant = **Publication**. Every user gets a personal publication on signup (slug = username, user is owner; cannot have other members; cannot be deleted while the account exists). Any user can create team publications. | |
| BR-43 | Every post belongs to exactly one publication and has one author who was a member when creating it. v1/v2 posts are migrated into their author's personal publication. | |
| BR-44 | **(v4: now expressed as permissions — see BR-59–BR-62; effective rights unchanged)** Roles per publication: **owner** (everything incl. members, settings, delete), **editor** (edit/publish/unpublish/delete any post, delete any comment on its posts, export publication posts), **writer** (create posts; edit/publish/unpublish/delete own posts only). Non-members have reader rights only. | Writer PATCHes another writer's post → 403 |
| BR-45 | Tenant context comes only from the URL path (`/api/v1/pubs/{pub_slug}/…`) and is resolved by a dependency that verifies membership. Never from request body, query string or a client-set header. | Body contains `publication_id` of another pub → ignored |
| BR-46 | Every tenant-scoped query filters by the resolved `publication_id`. Fetching a resource by id that exists in another publication → `404`. | `PATCH /pubs/a/posts/{id-from-pub-b}` → 404 |
| BR-47 | Public reading is cross-tenant: published posts from all publications appear in the global feed; `/pub/{slug}` lists one publication's published posts. Anonymous rules (BR-01) unchanged. | |
| BR-48 | Ownership: posts are owned by the publication (they stay when their author leaves; author name stays on them); likes and comments are owned by the user globally. A removed member immediately loses write rights. | |
| BR-49 | A publication always has ≥ 1 owner. The last owner cannot leave or be demoted → `409 LAST_OWNER`. Deleting a team publication (owner + BR-35 re-auth) deletes its posts. | |
| BR-50 | Invites: owners create an invite link with role editor or writer; valid 7 days, single use, revocable; token stored hashed. Accepting requires login. | Second use of an invite → 404 |
| BR-51 | Secrets (JWT keys, OAuth client secrets, Apple `.p8` key, signed-URL secret, DB/Redis/S3 credentials) come only from env vars or Docker secrets, are typed `SecretStr`, and never appear in the repo, image layers, logs, API responses or the frontend bundle. Nothing secret may use a `VITE_` prefix (Vite ships those to the browser). | |
| BR-52 | Outside `ENV=local`, the API refuses to start if any secret equals its `.env.example` placeholder or the JWT key is < 32 bytes. | |
| BR-53 | JWT signing keys rotate by `kid`: the new key signs; the previous key only verifies, and is removed after the longest token lifetime (30 days) has passed. | |
| BR-54 | CORS: credentialed requests allowed only from exact origins in `CORS_ORIGINS`; never `*` with credentials; methods GET/POST/PUT/PATCH/DELETE; headers `Content-Type`, `X-Request-ID`; preflight `max-age` 600 s. A disallowed origin receives no `Access-Control-Allow-Origin`. A public embed endpoint (if built) may use `*` only with no credentials and GET only. | Request from `http://evil.test` → no ACAO header |
| BR-55 | CSRF: every state-changing request must carry an `Origin` (or `Referer`) in the allowlist, else `403 CSRF_ORIGIN_MISMATCH`. OAuth callbacks are exempt but protected by `state` (BR-36). | |
| BR-56 | Every route is either in the explicit public-route allowlist or declares an auth dependency; a test walks all routes and fails otherwise. Authorisation is done in dependencies/services, not in a global middleware. | New route without auth → CI fails |
| BR-57 | **(v4: stored in the unified `audit_log`, category `auth` — see BR-70)** Auth events are audit-logged (login success/failure with method, link/unlink, password set/change, logout-everywhere, refresh-token reuse, role change, invite accept) with user id, IP, user agent, time; kept 90 days; never containing tokens, codes or passwords. | |
| BR-58 | Rate limits (extends BR-25): OAuth start 20/min per IP · token refresh 30/min per session · invite accept 10/hour per user · re-auth attempts 5/10 min per user. | |

### v4 — Role-based access control & operations
| ID | Rule | Example |
|---|---|---|
| BR-59 | Authorisation is permission-based. Code asks "does the actor hold `post:update:any` (or `post:update:own` and own it)?", never "is the actor an editor?". Roles are only named bundles of permissions. | |
| BR-60 | Permission format `resource:action[:scope]`; scope `own` or `any`. `any` implies `own`. Ownership: post → `author_id`; comment → `author_id`; like → `user_id`. | Writer holds `post:update:own` → may edit own post only |
| BR-61 | The role→permission mapping is the table below, implemented only in `app/authz/roles.py`. `docs/permissions.md` is generated from code; a test fails if code and this table differ. | |
| BR-62 | Effective permissions inside a publication = that publication's role permissions ∪ `member` permissions. Platform-role permissions apply only to platform resources (users, reports, moderation state, platform audit) and never grant tenant content permissions (read drafts, edit, publish, delete, export). | Admin opens a team's draft → 404 |
| BR-63 | Guard order for every protected route: authenticate (401) → not suspended (403 `ACCOUNT_SUSPENDED`) → resolve tenant (404 if not visible) → load resource scoped to tenant (404) → permission + ownership (403, or 404 per BR-41) → handler. | |
| BR-64 | Least privilege: every role gets the minimum it needs. Moderators hide/unhide but never edit or delete content; admins suspend and assign moderators but cannot read drafts, edit posts or change publication membership; editors cannot manage members; a new permission belongs to no role until mapped explicitly. | |
| BR-65 | The platform `admin` role is granted/revoked only via CLI (`make grant-admin`, requires direct DB access) — never via API. Admins assign/revoke `moderator` via API. Nobody can change their own platform or publication role → `403 SELF_ROLE_CHANGE` (ownership transfer BR-49 excepted). | |
| BR-66 | Permissions are resolved per request from the DB (cached only for the request's lifetime); role changes, removals and suspensions take effect on the caller's next request. | Editor demoted to writer → next PATCH on another's post → 403 |
| BR-67 | Reports: an authenticated user may report a published, visible post or comment once, with reason `spam`, `abuse` or `other` (+ note ≤ 500 chars). Duplicate → 409; own content → 403. | |
| BR-68 | Moderation hides, never deletes. A hidden post/comment disappears from all public lists and direct reads (404 for others); the author sees it with "Hidden by moderation: <reason>" and cannot republish it while hidden. Unhide restores it. Resolving a report with `hide` hides the content and marks all its open reports `actioned`. | |
| BR-69 | Suspension (admin, reason required): all sessions revoked immediately, `token_version` bumped, login → `403 ACCOUNT_SUSPENDED`; published content stays unless moderated. Admins cannot suspend themselves or another admin. | |
| BR-70 | One append-only `audit_log` records: all BR-57 auth events; role, membership and invite changes; post publish/unpublish/delete; moderation actions; reports resolved; suspensions; platform-role changes (incl. CLI); exports; permission denials (at most one row per actor + permission per minute). Each row: time, actor, action, outcome, resource, publication, request_id, IP, user agent, before/after for changes. Never tokens, passwords or post bodies. | |
| BR-71 | Audit writes happen in the same DB transaction as the action — if the audit row can't be written, the action fails. The `blog_app` DB role has INSERT/SELECT only on `audit_log`; only the retention job (`blog_maintenance`) deletes rows older than 365 days. | `UPDATE audit_log` as app role → permission denied |
| BR-72 | Audit visibility: publication owners see their publication's rows; platform admins see all; every user sees their own `auth` rows ("Security activity"). Viewing and exporting audit logs is itself audited. | |
| BR-73 | Permission-based UI: the frontend decides what to show from `GET /me/permissions` + ownership, never from role names. The server remains the only enforcement; every action hidden in the UI for a role has a server test proving it is rejected for that role. | |
| BR-74 | Environments are `local`, `ci`, `prod` (prod-like compose). The same image (same git SHA) runs in all of them; only env vars and secrets differ. No `if ENV == ...` outside `Settings`. | |
| BR-75 | Build-time: code, dependencies, `GIT_SHA`, `BUILD_TIME`. Runtime: everything else — API URL, DSNs, feature flags, limits, secrets. The web image reads runtime config from `config.js` written at container start, so changing API URL or DSN never needs a rebuild. | |
| BR-76 | Images are tagged with the git SHA (plus `vX.Y.Z` on release); `latest` is never deployed. Containers run as non-root; api/worker root filesystems are read-only (writable: tmpfs `/tmp`, uploads volume). | |
| BR-77 | Health: `/health/live` → 200 whenever the process can serve (no dependency checks). `/health/ready` → 200 only if DB, Redis, storage are reachable, the DB is at Alembic head and the worker heartbeat is < 30 s old; else 503 listing failing components (no stack traces, hostnames or secrets). Both are public, rate-limit exempt and logged only at DEBUG. | Redis stopped → ready 503 `{"failing":["redis"]}` |
| BR-78 | Logs: JSON to stdout, one event per line, with `request_id`; user identified by `user_id` only. Passwords, tokens, cookies, auth headers, emails, signed URLs, file contents and post bodies are redacted. Default level INFO; DEBUG is never enabled when `ENV=prod`. | |
| BR-79 | `/metrics` is reachable only on the internal network (nginx returns 404 for it). Metric labels are bounded — no user ids, emails, slugs or raw URLs. | |
| BR-80 | Error tracking receives unhandled exceptions from api, worker and web, tagged with release (`GIT_SHA`), environment and `request_id`. PII is scrubbed before sending (emails, cookies, auth headers, request bodies). Expected 4xx responses are not reported. Empty DSN = disabled. | |
| BR-81 | Backups: full logical backup daily and immediately before every deploy migration; uploads storage captured in the same run; keep 7 daily + 4 weekly; RPO 24 h, RTO 30 min. A backup counts only after `make restore-test` has restored it successfully; the restore drill runs before every release. | Backup older than 26 h → alert (FR-58) |
| BR-82 | Nothing merges to `main` unless CI passes: lint (ruff, ESLint, hadolint, role-name grep), backend + frontend tests (incl. permission matrix, route audit, IDOR suite), migration upgrade/downgrade/upgrade, gitleaks, image build and Trivy scan with no CRITICAL findings. | |
| BR-83 | Release: tag `vX.Y.Z` → images published to GHCR. Deploy = backup → run migrations as `blog_migrator` → restart app containers on the new tag → `/health/ready` green within 60 s, else automatic rollback to the previous tag. Migrations must be backward compatible with the previous release. | |

#### BR-61 role → permission mapping
| Permission | member (any logged-in user) | writer | editor | owner | moderator (platform) | admin (platform) |
|---|---|---|---|---|---|---|
| `like:create`, `like:delete:own` | ✓ | | | | | |
| `comment:create`, `comment:delete:own`, `report:create`, `pub:create`, `profile:update:own` | ✓ | | | | | |
| `post:create`, `import:create`, `pub:members:read` | | ✓ | ✓ | ✓ | | |
| `post:read_draft:own`, `post:update:own`, `post:publish:own`, `post:delete:own` | | ✓ | ✓ | ✓ | | |
| `post:read_draft:any`, `post:update:any`, `post:publish:any`, `post:delete:any` | | | ✓ | ✓ | | |
| `comment:delete:any` (within the publication), `pub:export` | | | ✓ | ✓ | | |
| `pub:members:manage`, `pub:invites:manage`, `pub:settings:update`, `pub:delete`, `pub:transfer`, `pub:audit:read` | | | | ✓ | | |
| `report:review`, `content:hide`, `content:unhide` | | | | | ✓ | ✓ |
| `user:read_admin`, `user:suspend`, `role:assign_moderator`, `audit:read_all` | | | | | | ✓ |
| `role:assign_admin` | CLI only — held by no role | | | | | |
| (v5) `integration:connect:own`, `token:manage:own` | ✓ | | | | | |
| (v5) `ai:assist` (on posts the actor may update), `post:crosspost:own` | | ✓ | ✓ | ✓ | | |
| (v5) `post:crosspost:any` | | | ✓ | ✓ | | |
| (v5) `pub:webhooks:manage`, `pub:github_sync:manage` | | | | ✓ | | |
Publication roles apply only inside their publication; a user's personal publication makes them its owner. Platform roles are additive to `member` and never include tenant content permissions (BR-62).

### v5 — REST API design, backend architecture & third-party integrations
| ID | Rule | Example |
|---|---|---|
| BR-84 | API versioning: major version in the URL (`/api/v1`, `/api/v2`). Breaking changes only in a new major; additive changes (new endpoints, new optional fields, new enum values documented as extensible) are allowed within a version. v2 covers posts, comments and likes; all other resources stay on v1 until migrated. | |
| BR-85 | v1 posts/comments/likes routes return a `Deprecation` header, a `Sunset` header (≥ 90 days after v2 ships) and `Link: </docs/api/v2-migration>; rel="deprecation"`. They are removed only after the sunset date **and** 14 consecutive days with zero calls (metric `blog_api_deprecated_calls_total`). | |
| BR-86 | Status codes (v2): 200 read/update · 201 create (+ `Location`) · 202 async accepted · 204 delete/no body · 304 not modified · 400 malformed JSON or unknown query parameter · 401 · 403 · 404 · 405 · 409 conflict · 412 `If-Match` mismatch · 415 non-JSON body · 422 validation · 428 missing `If-Match` · 429 · 500 · 502 upstream provider error · 503 upstream rate-limited or dependency down (+ `Retry-After`) · 504 upstream timeout. | Dev.to times out while validating an API key → 504 `UPSTREAM_TIMEOUT` |
| BR-87 | v2 errors use RFC 9457 `application/problem+json`: `type` (`https://blog.local/problems/<code-kebab>`), `title`, `status`, `detail`, `instance` (request path), plus `code` (stable UPPER_SNAKE), `request_id`, and `errors: [{field, message}]` for 422. v1 keeps its envelope; the two formats never mix within a version. | |
| BR-88 | v2 pagination is cursor-based: `?limit` (default 20, max 100) and `?cursor` (opaque, encodes sort values + id). Response `{data, page: {limit, next_cursor}, links: {self, next}}` and a `Link: <…>; rel="next"` header; `next_cursor` is null on the last page. No total counts. | |
| BR-89 | v2 sorting: `?sort=-published_at,title` (comma list, `-` = descending) from a per-resource whitelist (posts: `published_at`, `like_count`, `title`, `created_at`); default `-published_at`; `id` always appended as tie-breaker. Unknown field → 400 `INVALID_SORT`. | |
| BR-90 | v2 filtering: query params named after fields (`author`, `publication`, `status`, `source`, `slug`, `q`); ranges via `_after` / `_before` suffixes (`published_after=2024-01-01`); repeated param = OR within a field; different params AND together. | `?author=fareed&published_after=2024-01-01` |
| BR-91 | v2 bodies: JSON only (`Content-Type: application/json`, else 415); snake_case; RFC 3339 UTC timestamps with `Z`; UUIDs as strings; single resources are returned unwrapped; lists use the BR-88 envelope; request models reject unknown fields (422). | |
| BR-92 | Optimistic concurrency (v2): single-resource GET returns a strong `ETag`; PATCH and DELETE require `If-Match` (missing → 428, stale → 412 with the current ETag in the problem body). | Two editors save the same post → second gets 412 |
| BR-93 | Idempotency (v2): POST endpoints accept `Idempotency-Key` (≤ 255 chars). Same user + key + identical body within 24 h → the stored response is replayed with `Idempotent-Replayed: true`; same key with a different body → 409 `IDEMPOTENCY_KEY_REUSED`; a request still in progress with that key → 409 `IDEMPOTENCY_IN_PROGRESS`. | |
| BR-94 | MVC mapping (documented in architecture.md): Model = ORM models + repositories; View = Pydantic response schemas (API representation) and the React UI consuming them; Controller = FastAPI routers; Service = business rules. Business rules exist only in services; persistence only in repositories. | |
| BR-95 | Integrations are optional: the failure, slowness or absence of any external API never blocks reading, writing, publishing, commenting or password login. Each integration feature shows a clear degraded state instead. | Anthropic down → "AI suggestions unavailable", editor works |
| BR-96 | Outbound calls: timeouts connect 3 s / read 10 s (AI assist: 30 s total). Retries only on network errors, 408, 429, 5xx, and only for idempotent requests or requests carrying a provider idempotency key. Max 3 attempts; exponential backoff with full jitter (base 0.5 s, cap 8 s); `Retry-After` honoured up to 60 s — longer defers the job instead of sleeping. | Dev.to 503 twice then 200 → one article, 3 attempts logged |
| BR-97 | Outbound rate limits: a Redis token bucket per provider (and per user credential where the provider limits per token) keeps us under each provider's documented limit; a 429 pauses that bucket for `Retry-After`. Limits are settings, documented with a source link in docs/engineering.md. | |
| BR-98 | Work that is slow, retry-prone or triggered by webhooks runs in the worker as jobs (cross-post, GitHub sync, outbound webhook delivery). Only AI assist is synchronous (≤ 30 s, then 504 "Try again"). | |
| BR-99 | Data mapping: each provider has pure mapper functions between provider payloads and our domain objects, tested with recorded fixtures. Extra provider fields are ignored; missing required fields fail the job with `MAPPING_FAILED` (payload id logged, payload body not). Our canonical post fields are never overwritten by fields the provider doesn't own. | |
| BR-100 | Integration secrets: platform secrets (`ANTHROPIC_API_KEY`, GitHub OAuth client secret, GitHub webhook secret) only via env/Docker secrets. User-supplied credentials (Dev.to API key, GitHub access tokens) are encrypted at rest with AES-GCM using `INTEGRATION_ENCRYPTION_KEYS` (key id stored per row for rotation), never returned by the API (only last 4 chars), never logged, deleted on disconnect; GitHub grants are also revoked at the provider on disconnect. | |
| BR-101 | OAuth2 delegated access (GitHub): authorization code with `state` (and PKCE where supported); request the minimum scopes — public repositories only, scope limited to managing the repo webhook; private repos are out of scope. The connection belongs to the user; a publication's sync uses the connecting owner's grant and stops if that owner leaves the publication. | |
| BR-102 | GitHub sync: only `*.md` files in the configured folder of the configured branch. YAML front matter: `title` (required), `published` (bool, default false), `original_published_at` (optional). Key = (sync config, file path). Added/modified file → create/update post (published only if `published: true` — an explicit exception to BR-16 because Markdown is lossless and the author controls the flag); deleted file → post unpublished, never deleted; rename = unpublish old + create new. Synced posts are read-only in the editor ("Managed in GitHub"). | |
| BR-103 | Inbound webhooks: read the raw body (≤ 1 MB, else 413), verify the HMAC signature with a constant-time comparison **before** parsing JSON (invalid → 401, audited), dedupe by delivery id for 7 days (duplicate → 200 no-op), ignore unknown events (204), respond ≤ 2 s with 202 and do the work in a job. | Replayed GitHub delivery → 200, nothing re-run |
| BR-104 | Dev.to cross-post: allowed for published posts by actors with `post:crosspost:own/any`. Created on Dev.to as an unpublished draft unless the user ticks "Publish on Dev.to"; `canonical_url` always points to our post; one Dev.to article per post (external id stored) — later edits here update it; unpublishing or deleting here does not delete it on Dev.to (the UI says so). | |
| BR-105 | AI assist (Anthropic): only on explicit user action, only for posts the actor may update. Sends title + body (truncated to 20,000 chars). Returns suggestions (title ≤ 200, excerpt ≤ 280, SEO description ≤ 160) that the user accepts or edits — never applied automatically, never generates or rewrites the body. Limits: 20 requests/day per user; platform monthly budget `AI_MONTHLY_BUDGET_USD`, after which the feature disables with a message. Prompts and outputs are not stored; usage (tokens, latency, outcome) is. The UI states that the draft is sent to a third-party AI provider. | |
| BR-106 | Outbound webhooks: owners register endpoints (https only; http allowed when `ENV=local`) for `post.published`, `post.unpublished`, `post.deleted`, `comment.created`. Payload `{id, type, created_at, api_version: "2", data}` using v2 representations. Headers `X-Blog-Event`, `X-Blog-Delivery`, `X-Blog-Signature: t=<unix>,v1=<hex hmac_sha256(secret, t + "." + body)>`. Secret shown once, rotatable (old secret also signs for 24 h). | |
| BR-107 | Webhook delivery: 5 s timeout, success = any 2xx, no redirects followed; retries after 1 m, 5 m, 30 m, 2 h, 6 h, 12 h (7 attempts); an endpoint with 20 consecutive failed deliveries is disabled and flagged to the owner; delivery log kept 30 days with request/response status and duration (bodies truncated to 2 KB). | |
| BR-108 | SSRF guard for every user-supplied URL (webhook endpoints, any future fetch): resolve DNS, reject private, loopback, link-local, multicast and cloud-metadata addresses (e.g. 169.254.169.254) unless `ENV=local`, and connect to the vetted IP (prevents DNS rebinding). | `http://10.0.0.5/hook` in prod → 422 `URL_NOT_ALLOWED` |
| BR-109 | Personal access tokens (Could): `bp_` + 32 random bytes, stored hashed, shown once; scoped to one publication and a subset of the creator's current permissions; expiry ≤ 90 days; accepted only as `Authorization: Bearer` on `/api/v2`, never as cookies; creation, first use per day and revocation are audited. Token permissions shrink automatically if the creator's role shrinks. | |
| BR-110 | Integration status: every connection shows last success, last failure (code + time) and whether it is active; three consecutive auth failures (401/403 from the provider) mark the connection `needs_reauth` and pause its jobs. | |

## Git workflow
- `main` is always runnable. Short-lived branches: `feat/T-005-post-crud`, `fix/T-012-feed-order`.
- Conventional Commits with task ID: `feat(posts): add publish toggle (T-007)`.
- One task per merge. Commit migrations in the same commit as the model change.
- (v5) Trunk-based: branches live ≤ 2 days; no long-lived `develop`/release branches; hotfixes branch from the release tag, merge to `main`, and are tagged `vX.Y.Z+1`.
- (v5) Commit messages are validated by commitlint (pre-commit hook and CI): `type(scope): subject (T-XXX)`, types `feat|fix|refactor|test|docs|chore|ci|build|perf`; breaking changes marked `!` or `BREAKING CHANGE:` footer.
- (v5) Pull requests: use `.github/pull_request_template.md` (task ID, what/why, test evidence, screenshots for UI, migration + rollback notes, checklist); keep diffs ≤ 400 changed lines excluding generated files — split otherwise; self-review the diff before requesting review; CI must be green (BR-82); squash-merge only, PR title becomes the commit message.
- (v5) `main` is protected: no direct pushes, linear history, required checks, CODEOWNERS review for `app/authz/`, `app/integrations/`, `deploy/`, `.github/`.
- (v5) Versioning: SemVer tags `vX.Y.Z`; `CHANGELOG.md` generated from Conventional Commits at release.
- (v5) Terminal: every repeated command is a `make` target listed by `make help`; shell scripts start with `set -euo pipefail` and are shellcheck-clean.
- (v5) Package managers: backend `uv` with committed `uv.lock` (`uv sync --frozen` in CI and Docker); frontend `npm` with committed `package-lock.json` (`npm ci` in CI and Docker); no global installs in docs or scripts; Dependabot weekly, grouped by ecosystem.
