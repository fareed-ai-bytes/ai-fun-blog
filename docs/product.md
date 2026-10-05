# Product Requirements — Blog Platform
_Last reviewed: 2026-09-28 (v4: v3 auth/tenancy aligned + RBAC, moderation, DevOps, observability) · Owner: Fareed_

## Problem
Writers need a place to publish where readers are not forced through a login wall, but engagement
(likes, comments) must be tied to a real account so it can't be spammed anonymously and each post has a clear owner.
The underlying goal of this build is to demonstrate authentication AND authorisation (ownership, visibility)
done correctly, in a modular, documented codebase a reviewer can run in minutes.

## Users
| Persona | Goal | Frequency of use |
|---|---|---|
| Reader (anonymous) | Browse the feed, read a post, see like/comment counts and comments | Every visit |
| Author (logged in) | Write drafts, publish, edit, unpublish and delete their own posts | Weekly |
| Engaged reader (logged in) | Like and comment on other people's posts | Every visit |
| Migrating author (logged in) | Bring years of old posts written in Word or saved as PDF onto the platform without retyping | Once, in bulk |
| Publication editor / owner (v3) | Run a team blog: invite writers, edit and publish their posts, see who did what | Weekly |
| Moderator (v4, platform) | Review reports, hide abusive posts/comments across the platform without editing them | Daily |
| Platform admin (v4) | Suspend abusive accounts, assign moderators, read the platform audit log | Weekly |
| Integrating author (v5) | Write in GitHub or VS Code, cross-post to Dev.to, get AI help with titles and excerpts | Weekly |
| Integrator / developer (v5) | Consume the v2 API and publication webhooks from their own tools | Occasionally |
| Operator (v4, you) | Build, ship, observe and restore the system: health, logs, metrics, errors, backups | Daily |
| Reviewer (bootcamp assessor) | Clone, run and verify every feature within minutes | Once — but decides the outcome |

## Scope
### In scope (v1)
- Anyone can browse a paginated feed of published posts and read any published post without logging in.
- A visitor can register with email, username and password, then log in and log out.
- A logged-in user can create posts as drafts, publish, edit, unpublish and delete their own posts only.
- A logged-in user sees a "My posts" dashboard including their drafts.
- A logged-in user can like/unlike and comment on published posts written by others.
- Comment authors and post authors can delete comments.
- Post bodies are written in Markdown and rendered safely.
- One command seeds realistic demo data for the video.
- (v2) A logged-in user can upload up to 5 old posts at once as .docx or .pdf; each becomes a DRAFT post they review before publishing.
- (v2) Import progress and history are visible; the original file can be re-downloaded by its owner through a short-lived link.
- (v2) Authors can export their posts as CSV or Excel; anyone can download a published post as PDF.
- (v2) The feed can be filtered (author, date range, title contains, imported/native) and sorted (newest, most liked).
- (v2) Authors can publish, unpublish or delete many posts in one action.
- (v2) The API stays fast at 100k posts, with measured evidence (query plans, load-test numbers) in the repo.
- (v2) Abuse-prone endpoints are rate-limited; responses are compressed and cached where safe.
- (v3) Sign in with Google, Microsoft, Yahoo or Apple as well as email/password; link and unlink providers; manage sessions.
- (v3) Publications are tenants: every user has a personal publication and can create team publications with owner/editor/writer members and invite links.
- (v4) Authorisation is permission-based: roles are bundles of permissions; the UI shows only what the user is permitted to do.
- (v4) Platform moderators and admins: content reports, moderation queue, hide/unhide, user suspension.
- (v4) Append-only audit log for security, membership, content, moderation and admin actions, viewable per publication and platform-wide.
- (v4) Production-grade containers, prod-like compose stack, CI pipeline and tagged image releases.
- (v4) Health checks, structured logs, metrics dashboards, error tracking, and tested database backups.
- (v5) A documented engineering workflow (SDLC, Git/PR rules, request lifecycle, ports, DNS) enforced by tooling.
- (v5) MVC-style layering with repositories and machine-checked module boundaries; typed frontend client generated from OpenAPI.
- (v5) REST API v2 for posts, comments and likes: cursor pagination, sorting, filtering, problem+json errors, ETags, idempotency keys; v1 formally deprecated for those resources.
- (v5) AI writing assist (title, excerpt, SEO description suggestions) via the Anthropic API.
- (v5) Cross-post published posts to Dev.to with a canonical link back.
- (v5) Posts-as-code: connect a public GitHub repo; pushes to a folder create/update posts.
- (v5) Publication webhooks for integrators, signed and retried.

### Explicitly out of scope
- Image uploads, cover images, and images embedded inside imported documents (stripped with a warning)
- Legacy .doc, .odt, .rtf, .pages imports; OCR of scanned PDFs; virus/malware scanning
- Resumable/chunked uploads, direct browser-to-S3 uploads, import from URLs or other platforms
- Rich-text / WYSIWYG editor (Markdown textarea + preview only)
- Tags, categories, full-text search, trending/ranking (a title-contains filter IS in scope)
- Following users, notifications, email of any kind
- Email verification, password reset, "remember me", MFA/passkeys
- Custom roles or editing the role→permission mapping at runtime (mapping lives in code; changes go through review)
- (v5) Medium, Hashnode, WordPress, LinkedIn or other cross-post targets; pulling edits back from Dev.to
- (v5) Private GitHub repositories, GitLab/Bitbucket, two-way GitHub sync (platform edits written back to the repo)
- (v5) AI-generated or AI-rewritten post bodies, AI tags, AI moderation, chat features
- (v5) Migrating non-post resources to API v2; GraphQL; SDKs for our own API
- Moderator appeals workflow, automated content classification
- Threaded replies, comment editing, reactions other than a single like
- Autosave, version history, scheduled publishing
- Dark mode, i18n
- Cloud hosting, Kubernetes, Terraform (CI + image release are in scope; "deploy" targets the local prod-like compose stack)
- Log aggregation beyond Docker logs (Loki is a Could), paging/on-call, distributed tracing
- Point-in-time recovery / WAL archiving (daily logical backups only)

## Functional requirements
| ID | Requirement | Priority | Acceptance criteria |
|---|---|---|---|
| FR-01 | Register with email, username, password | Must | `POST /api/v1/auth/register` valid → 201 + session cookie set; duplicate email or username → 409; password < 8 chars or invalid username → 422 |
| FR-02 | Log in / log out / current user | Must | Correct creds → 200 + cookie; wrong email OR password → 401 with the same generic message; logout → 204 and cookie cleared; `GET /auth/me` → 401 afterwards |
| FR-03 | Public feed of published posts | Must | Anonymous `GET /posts` returns only published posts, `published_at` desc, 10 per page, each with title, excerpt, author, published_at, like_count, comment_count |
| FR-04 | Read a published post without login | Must | Anonymous `GET /posts/{slug}` on published → 200 with body; on a draft → 404 (not 403) |
| FR-05 | Create a post | Must | Logged-in `POST /posts` → 201, author = current user, default status draft; anonymous → 401 |
| FR-06 | Edit own post | Must | Author `PATCH /posts/{id}` → 200; another user → 403; anonymous → 401; slug does not change when title changes |
| FR-07 | Publish / unpublish own post | Must | draft→published sets `published_at` only the first time; published→draft removes it from feed and public read (404) |
| FR-08 | Delete own post | Must | Author `DELETE /posts/{id}` → 204 and its likes/comments are gone; another user → 403 |
| FR-09 | "My posts" dashboard | Must | `GET /me/posts` returns all the current user's posts, drafts included, `updated_at` desc |
| FR-10 | Like / unlike | Must | `PUT /posts/{id}/like` → 200 `{like_count, liked_by_me: true}`; repeat PUT leaves count unchanged; `DELETE` reverses; own post → 403; draft → 404; anonymous → 401 |
| FR-11 | Comment on a published post | Must | `POST /posts/{id}/comments` → 201; empty or > 2,000 chars → 422; draft → 404; anonymous → 401 |
| FR-12 | Read comments publicly | Must | Anonymous `GET /posts/{id}/comments` → 200, oldest first, paginated 20 per page |
| FR-13 | Delete a comment | Should | Comment author or post author → 204; anyone else → 403 |
| FR-14 | Author page | Could | `GET /posts?author={username}` returns that user's published posts only |
| FR-15 | Demo seed data | Must | `make seed` creates 3 users with documented passwords, ≥ 8 posts incl. 1 draft per user, likes and comments; running twice creates no duplicates |
| FR-16 | Upload old posts (.docx/.pdf) | Must | Logged-in `POST /imports` (multipart, field `files`, 1–5 files) → 202 with per-file `accepted`/`rejected`; anonymous → 401; all files invalid → 422 |
| FR-17 | Upload validation & limits | Must | Type decided by file content, not name or Content-Type: renamed .exe → rejected `UNSUPPORTED_TYPE`; 10 MB + 1 byte → `FILE_TOO_LARGE` without the API reading the whole file; 6 files → 422 `TOO_MANY_FILES` |
| FR-18 | Convert to draft post | Must | Worker turns a valid file into a draft within 30 s: title from first heading/PDF title, body as Markdown, `source=imported`; never auto-published |
| FR-19 | Import status & history | Must | `GET /imports/{id}` shows `queued → processing → succeeded/failed` with `error_code` and `warnings`; `GET /imports` lists own imports only |
| FR-20 | Duplicate detection | Should | Same user re-uploads an identical file whose earlier import succeeded → rejected `DUPLICATE_IMPORT` with the existing post id |
| FR-21 | Secure original download | Must | Owner requests a link → gets a URL valid 5 minutes; after expiry → 403; another user can't obtain a link (404); file served as attachment |
| FR-22 | Export own posts CSV | Must | `GET /me/exports/posts.csv` streams all own posts with stats; first byte < 500 ms for 10k posts; API memory stays flat |
| FR-23 | Export own posts Excel | Should | `GET /me/exports/posts.xlsx` → workbook with sheets `Posts` and `Comments`; opens in Excel/LibreOffice without repair prompt |
| FR-24 | Download post as PDF | Should | `GET /posts/{id}/export.pdf` → PDF for published posts (anyone) or own drafts; others' drafts → 404 |
| FR-25 | Feed filtering & sorting | Must | `GET /posts` supports `author`, `from`, `to`, `q` (title contains, case-insensitive), `source`, `sort=newest|most_liked`; unknown sort → 422 |
| FR-26 | Payload control | Should | `?fields=id,title,slug` returns only those fields; `page_size` max 50 (51 → 422); feed items never include `body_md` |
| FR-27 | Batch actions | Should | `POST /me/posts/batch` with ≤ 50 ids and action publish/unpublish/delete → 200 with per-id result; others' ids report `FORBIDDEN` without failing the rest |
| FR-28 | Rate limiting | Must | Limits in rules.md BR-25; exceeding → 429 `RATE_LIMITED` with `Retry-After` header |
| FR-29 | Performance evidence | Must | `docs/performance.md` has before/after EXPLAIN ANALYZE and load-test numbers for feed, post detail, author page, title filter, my-posts |
| FR-30 | "Originally published" date | Could | Author can set `original_published_at` on imported posts; shown on post page; feed order unaffected |
| FR-31 | Reading time | Could | Post shows "N min read" from stored `word_count` (200 wpm) |
| FR-32 | Sign in with Google and Microsoft (v3) | Must | OIDC code + PKCE flow completes on localhost; new user created with generated username; BR-29–BR-37 tests pass |
| FR-33 | Sign in with Yahoo (v3) | Should | Real sign-in works, or the blocker is recorded in memory.md |
| FR-34 | Sign in with Apple (v3) | Could | Works via HTTPS tunnel with a paid developer account, or skip decision recorded |
| FR-35 | Account linking & password settings (v3) | Must | Link/unlink providers, set/change password; BR-31, BR-33–BR-35 tests pass |
| FR-36 | Sessions (v3) | Must | Rotating refresh tokens, sessions list with revoke, log out everywhere; BR-39, BR-40 tests pass |
| FR-37 | Publications (v3) | Must | Personal publication on signup; team publications; `/pub/{slug}` public page; existing posts migrated (BR-42, BR-43) |
| FR-38 | Members, roles & invites (v3) | Must | Invite links, role change, remove, leave, transfer ownership; BR-48–BR-50 tests pass |
| FR-39 | Tenant isolation (v3) | Must | Tenant routes under `/pubs/{slug}`; cross-tenant IDOR suite returns 404 everywhere (BR-45, BR-46) |
| FR-40 | Permission catalogue & mapping (v4) | Must | Every protected route declares one permission; `docs/permissions.md` generated from code matches the BR-61 table (test) |
| FR-41 | Effective permissions endpoint (v4) | Must | `GET /me/permissions?pub={slug}` returns platform, publication and self permissions for the caller; anonymous → 401 |
| FR-42 | Permission-based UI (v4) | Must | For each role, every hidden action is also rejected by the API (403/404) and every shown action succeeds — verified by a role × screen test |
| FR-43 | Platform roles (v4) | Must | Admin granted only by `make grant-admin`; admins assign/revoke moderators via API; self role change → 403 (BR-65) |
| FR-44 | Report content (v4) | Should | Logged-in user reports a published post/comment once; duplicate → 409; own content → 403 (BR-67) |
| FR-45 | Moderation queue (v4) | Should | Moderator lists open reports, hides/unhides posts and comments with reason; hidden content disappears publicly (BR-68) |
| FR-46 | User suspension (v4) | Should | Admin suspends → sessions revoked at once, login → 403 `ACCOUNT_SUSPENDED` (BR-69) |
| FR-47 | Audit log (v4) | Must | Events in BR-70 recorded in the same transaction; UPDATE/DELETE by app DB role fails; owner, admin and self views with filters and CSV export (BR-70–BR-72) |
| FR-48 | Production images (v4) | Must | Multi-stage, non-root images for api (worker reuses it) and web (nginx); hadolint clean; api < 300 MB, web < 60 MB |
| FR-49 | Compose environments (v4) | Must | `make up` (dev, hot reload), `make up-prod` (built images) and `make up-obs`; all services healthy < 60 s |
| FR-50 | Runtime config & version (v4) | Must | Same web image points at a different API/DSN by changing env only (no rebuild); `GET /version` returns git SHA and build time |
| FR-51 | CI pipeline (v4) | Must | Every PR runs lint, tests, migration up/down, secret scan, image build + vulnerability scan; failing any blocks merge (BR-82) |
| FR-52 | Release & deploy (v4) | Should | Tag `vX.Y.Z` publishes images to GHCR; `make deploy VERSION=vX.Y.Z` does backup → migrate → restart → ready check, and rolls back on failure (BR-83) |
| FR-53 | Health checks (v4) | Must | `/health/live` and `/health/ready` per BR-77; stopping Redis turns ready 503 naming `redis`; worker heartbeat visible |
| FR-54 | Structured logs (v4) | Must | Every log line is JSON with request_id; one request traceable across api and worker logs; redaction test passes (BR-78) |
| FR-55 | Metrics & dashboard (v4) | Must | `/metrics` internal only; Grafana dashboard (provisioned from repo) shows request rate, error rate, p95 latency, import queue depth, cache hit ratio, 403/429 counts |
| FR-56 | Error tracking (v4) | Should | A forced backend and frontend error each appear in GlitchTip/Sentry with release SHA, request_id and no PII (BR-80) |
| FR-57 | Backups & restore drill (v4) | Must | `make backup` produces a compressed dump + uploads archive; `make restore-test` restores into a scratch DB and row counts match (BR-81) |
| FR-58 | Alerts (v4) | Could | Prometheus rules for 5xx rate, readiness, queue depth, backup age visible in Grafana |
| FR-59 | "View as role" preview (v4) | Could | Owner previews a publication page as writer/editor/reader; UI only — API calls still use the real user |
| FR-60 | Engineering workflow tooling (v5) | Must | Commitlint, PR template, CODEOWNERS, pre-commit, protected `main`, `make help`, CHANGELOG on release (rules.md Git workflow) |
| FR-61 | Engineering foundations doc (v5) | Must | `docs/engineering.md` verified against the repo: SDLC, workflow, client-server, HTTP, request lifecycle, ports, DNS |
| FR-62 | Layered modules with repositories (v5) | Must | All SQL in repositories; import-linter contracts pass in CI; no behaviour change (OpenAPI identical after restructure) |
| FR-63 | Generated typed API client (v5) | Must | Frontend uses types generated from OpenAPI; CI fails on drift |
| FR-64 | REST API v2 for posts, comments, likes (v5) | Must | BR-84–BR-93 contract tests pass; frontend uses v2 for these resources |
| FR-65 | v1 deprecation (v5) | Should | Deprecation/Sunset/Link headers on v1 posts/comments/likes; usage metric; migration guide |
| FR-66 | AI writing assist (v5) | Should | Suggestions within 30 s or a clear timeout; never auto-applied; limits and budget enforced (BR-105) |
| FR-67 | Dev.to cross-post (v5) | Should | Connect with API key; cross-post creates a Dev.to draft with canonical URL; edits update it; failures visible (BR-104) |
| FR-68 | GitHub connection via OAuth2 (v5) | Should | Connect/disconnect with minimal scope; repo/branch/folder chosen; webhook created and removed automatically (BR-101) |
| FR-69 | GitHub posts-as-code sync (v5) | Should | Push of a `.md` file creates/updates a post within 30 s; delete unpublishes; signatures verified; duplicates ignored (BR-102, BR-103) |
| FR-70 | Outbound publication webhooks (v5) | Should | Owners register endpoints; deliveries signed, retried, logged; test event button; SSRF-safe (BR-106–BR-108) |
| FR-71 | Integration status (v5) | Should | Connections page shows health; repeated auth failures mark `needs_reauth` and pause jobs (BR-110) |
| FR-72 | Personal access tokens (v5) | Could | Scoped, expiring, hashed tokens for `/api/v2` (BR-109) |

## Non-functional requirements
- Performance: feed and post-detail endpoints p95 < 300 ms locally with 1,000 seeded posts. Counts come from one aggregate query per page — no N+1.
- Security: passwords hashed with argon2; session = JWT in an `HttpOnly`, `SameSite=Lax` cookie (`Secure` when `COOKIE_SECURE=true`); no tokens in localStorage; Markdown rendered with raw HTML disabled; CORS restricted to the frontend origin; secrets only in `.env`.
- PII: email is the only PII. It is never returned by a public endpoint — only by `/auth/me`.
- Availability / cost: local Docker only; zero cloud cost.
- (v2) Uploads: 10 MB/file, 5 files/request. Uploading a 10 MB file raises API process memory by < 5 MB (proves streaming, not buffering).
- (v2) Performance at 100k posts / 500k likes / 200k comments (`make seed-perf`): feed p95 < 250 ms cold, < 50 ms cache-hit; post detail p95 < 150 ms; no Seq Scan on posts/likes/comments in any listed query plan.
- (v2) Throughput: feed sustains 200 req/s locally with p95 inside target (Locust, 50 users).
- (v2) JSON responses > 1 KB are gzip-compressed; feed page payload ≤ 8 KB compressed.
- (v2) Import failures never leave orphaned temp files; stuck jobs are retried (max 3) then failed.
- (v4) Security: every container runs as non-root; API and worker root filesystems are read-only; the app connects to Postgres with a role that has no DDL rights and cannot alter the audit log.
- (v4) Operability: `make up-prod` healthy in < 60 s; CI completes in < 10 min; metrics scrape < 50 ms.
- (v4) Recovery: RPO 24 h, RTO 30 min for the demo dataset, proved by the restore drill.
- (v5) Resilience: with any single provider (Anthropic, Dev.to, GitHub) returning errors or timing out, all core Must FRs still pass (chaos test with respx).
- (v5) Webhook ingress: GitHub webhook answered in < 2 s p95; outbound delivery first attempt < 60 s after the event.

## Success metrics
- Fresh clone → running app with seed data in ≤ 3 commands and < 5 minutes on a machine with Docker.
- Every Must FR has at least one passing automated API test that asserts its acceptance criterion.
- Backend coverage ≥ 80% for `app/services` and `app/api`.
- Demo video shows every Must FR in ≤ 2:00.
- (v2) Every topic in docs/TOPICS.md points to a passing test or a measured result in docs/performance.md.
- (v2) ≥ 90% of the seed .docx fixtures convert with headings, lists and paragraphs intact.
- (v4) Permission matrix test covers every (role × permission) pair; zero routes without a declared permission or public allowlisting.
- (v4) A fresh clone reaches a green CI run and a healthy `make up-prod` without manual steps beyond `.env`.

## Open questions
- Self-likes: assumed BLOCKED, reading "other logged-in users can like" literally. Confirm.
- Can a post author delete other people's comments on their post? Assumed YES (FR-13). Confirm.
- Is a public deployment expected, or is local-only acceptable? Assumed local-only from the deliverable wording.
- Exact deadline date for the week.
- (v2) Does "docs" mean .docx only, or also legacy .doc? Assumed .docx only; .doc is rejected with "save as .docx".
- (v2) Should the video demo S3 (MinIO) or is local storage enough? Assumed local in the demo, MinIO shown for 5 seconds.
- (v2) Is the PDF export for anyone (published posts) acceptable, or authors only? Assumed anyone, rate-limited.
- (v3) Does the bootcamp's "tenant" mean something other than a publication? Assumed publication.
- (v4) Is a real hosted deployment expected for "CI/CD"? Assumed no — CD = tagged images + scripted deploy to the prod-like compose stack.
- (v4) Error tracking: self-hosted GlitchTip (assumed) or a Sentry SaaS free account? Same SDK either way — only the DSN changes.
- (v5) Who pays for the Anthropic API key used in the demo, and what monthly budget cap? Assumed a small cap set in `.env`.
- (v5) Is Dev.to an acceptable cross-post target? (Medium's API no longer accepts new integrations, as far as known — verify.)
- (v5) Webhooks from GitHub need a public URL locally — smee.io assumed acceptable for the demo.
