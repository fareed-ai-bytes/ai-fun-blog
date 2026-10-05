# Build plan — how to drive Claude Code through this project

The kit's PROMPTS.md steps 1–6 assume an existing codebase ("analyse this code and fill…").
This project is greenfield, so the docs are already filled and the order is inverted:
docs first → verify Claude understood them → build task by task. Keep PROMPTS.md only for its
"Ongoing — end of session" prompt.

## 0. Setup (once)
1. `mkdir blog-platform && cd blog-platform && git init`
2. Copy `CLAUDE.md` to the repo root and `docs/*.md` into `./docs/`. Commit: `docs: project context (T-000)`.
3. Start Claude Code in the repo. Run `/memory` and confirm CLAUDE.md is loaded.

## 1. Comprehension check (before any code)
```
Without writing any code: in 5 bullets tell me what this app is, how it's built, and the auth flow.
Then list every contradiction, ambiguity or missing decision you find across CLAUDE.md and docs/.
Then name the 3 rules in docs/rules.md you are most likely to break.
```
Fix the docs for anything real it finds. Do not skip this — a wrong doc poisons every later session.

## 2. Per-task loop (repeat for T-001 … T-019)
Use plan mode for T-001, T-002, T-004, T-006 and T-013 — they set patterns everything else copies.
```
Read docs/tasks.md. Do T-0XX only.
1. Plan: list files you'll create/change and the tests that prove the acceptance criterion. Wait for my OK.
2. For backend tasks, write the failing tests first, then the code.
3. Run `make test-api` and `make lint` (and `make test-web` for frontend tasks); show the output summary.
4. Update docs/tasks.md and append decisions/gotchas to docs/memory.md. Show the diff.
```
Start a fresh session (`/clear`) between tasks. If a session goes sideways, revert and redo the task rather than patching.

## 3. Checkpoints
- End of D2: `make test-api` green, every BR-xx has a named test. Ask:
  `List each FR and BR and the test that covers it. Flag any without one.`
- End of D4: click through every Must FR in the browser yourself. Don't trust "done" without looking.

## 4. Docs deliverable (T-018)
```
Export the OpenAPI schema to docs/openapi.json. Generate docs/api.md from it: one section per endpoint with
auth level, request, response, error codes, and one curl example. Then write docs/usage.md with walkthroughs
for reader, author and commenter using the seed logins. Finally compare docs/architecture.md with the real
code and list every difference — do not fix the doc silently, show me.
```

## 5. Demo script (T-020) — target 1:55
| Time | Show |
|---|---|
| 0:00–0:15 | Repo + README quickstart; run `make up` (pre-built so it's fast), `make seed` |
| 0:15–0:35 | Logged out: feed, open a post, comments visible, "Log in to like" shown, `/docs` API page for 3 seconds |
| 0:35–1:05 | Log in as user A: Write → Save draft → shows in My posts as Draft → Publish → appears in feed; Edit title |
| 1:05–1:35 | Log in as user B (second browser/incognito): like A's post, comment; show A's draft URL returns Not found |
| 1:35–1:50 | Back as A: no like button on own post; delete B's comment; delete a post |
| 1:50–1:55 | Terminal: `make test-api` green, one line on architecture |
Rehearse once. Two browser profiles pre-logged-in save ~20 seconds.

---

# v2 — Import, export & performance week

## Start of week
```
Read docs/product.md FR-16 to FR-31, the v2 sections of docs/architecture.md and docs/rules.md, and docs/TOPICS.md.
Without writing code: list contradictions or gaps between them, and tell me which of the 23 topics
you think is weakest in this design and why.
```
Then work T-021 → T-039 with the same per-task loop as week 1. Plan mode for T-024, T-025, T-028, T-031.

## Performance tasks — extra rule for every prompt
```
Before changing anything: run `make explain` and/or `make loadtest`, save the output, show me the key line.
Make ONE change. Measure again. Append Before / Change / After to docs/performance.md.
```

## End-of-week checkpoint
```
For each row in docs/TOPICS.md, show me the proof (test name or performance.md section) and run that test.
List any topic whose proof is missing or failing.
```

## v2 demo script — target 1:55
| Time | Show |
|---|---|
| 0:00–0:10 | `make up` running: db, redis, api, worker, web |
| 0:10–0:40 | `/import`: drop 3 .docx + 1 .pdf + 1 renamed .exe → progress bars; .exe rejected with reason; others become drafts; open one, show "Images removed" warning, publish |
| 0:40–0:55 | `/me/imports`: download original (link expires in 5 min); My posts: select 3 → Publish; Export → CSV and Excel open |
| 0:55–1:10 | Feed: filter by author + title contains; post page → Download PDF |
| 1:10–1:35 | Terminal / docs/performance.md: one EXPLAIN before (Seq Scan) vs after (Index Scan) with times; query count 21 → 3; gzip bytes before/after |
| 1:35–1:50 | Rate limit: 6 quick logins → 429 toast with countdown; repeat feed request → 304 in DevTools |
| 1:50–1:55 | `make test-api` green; docs/TOPICS.md on screen |

---

# v3 + v4 — Auth/tenancy and RBAC/DevOps weeks

## Start of week 3 (the doc package already contains the T-040 alignment)
```
Read CLAUDE.md, docs/product.md FR-32–FR-39, the v3 sections of docs/architecture.md, BR-29–BR-58 in docs/rules.md.
Without writing code: list every contradiction between them (T-040). Then plan T-041.
```

## Start of week 4
```
Read FR-40–FR-59, the "Authorisation model", "Audit log", "Database roles", "Containers", "CI/CD" and
"Observability" sections of docs/architecture.md, and BR-59–BR-83 incl. the BR-61 mapping table.
Without writing code: (1) list any permission a role holds that it doesn't need (least privilege review),
(2) list routes from week 1–3 that will need a new permission guard, (3) list contradictions between docs.
```
Plan mode for T-061, T-062, T-064, T-067, T-070, T-077. DevOps tasks (T-069–T-078) don't depend on RBAC — if RBAC slips, run them in parallel sessions.

## Checkpoint prompts
```
Print the permission matrix test results as a table: role × permission → expected / actual.
```
```
Run `make up-prod`, then show `docker compose ps` health, `docker image ls` sizes, and `whoami` inside api and web.
```
```
Run `make backup` then `make restore-test` and show the row-count comparison.
```

## v4 demo script — target 1:55
| Time | Show |
|---|---|
| 0:00–0:15 | GitHub: green CI run (lint, tests, migrations, Trivy) → GHCR images tagged with SHA |
| 0:15–0:25 | `make up-prod` → `docker compose ps` all healthy; `/version` shows the same SHA |
| 0:25–0:55 | Three browser profiles: writer (no Edit on others' posts), editor (can edit/publish), owner (Members + Audit tabs). Demote editor → next click is refused |
| 0:55–1:15 | Moderator hides a reported comment; admin tries to open a team draft → Not found; audit log shows both actions and the denial |
| 1:15–1:35 | Grafana dashboard during `make loadtest`; one JSON log line followed by `request_id` into the worker; forced error appears in GlitchTip with release SHA |
| 1:35–1:50 | Stop redis → `/health/ready` 503 `["redis"]`; `make restore-test` result |
| 1:50–1:55 | docs/TOPICS.md week-4 table with proofs filled |

---

# v5 — Foundations, MVC/REST v2 and third-party integrations

## Start
```
Read docs/engineering.md, FR-60–FR-72, the "MVC mapping", "Directory map (v5 target)", v5 data model and
v5 endpoint sections of docs/architecture.md, the v5 coding rules and BR-84–BR-110 in docs/rules.md.
Without writing code: (1) list contradictions between docs, (2) list every current service function that
contains SQL (input for T-085), (3) list any existing v1 route that already violates the v5 REST rules and
say whether it matters (v1 is frozen).
```

## The restructure (T-084–T-086) — keep it boring
```
Plan mode. Move ONE module per commit into app/modules/<feature>/. No logic changes, no renames of
functions, no new features. After each commit: `make test-api`, `make lint`, and diff the OpenAPI JSON
against the pre-restructure snapshot. Stop and show me if anything differs.
```

## Integration tasks — extra rule
```
No real provider calls in tests: use respx fixtures under tests/fixtures/providers/<provider>/.
For each outbound call, show me: timeout, retry decision, rate-limit bucket, and the status we return
to our client when the provider fails.
```

## v5 demo script — target 1:55
| Time | Show |
|---|---|
| 0:00–0:15 | A PR: template filled, commitlint + import-linter + contract tests green, squash-merged |
| 0:15–0:35 | `curl` v2: list posts with `sort` + `cursor` (Link header), PATCH without `If-Match` → 428, stale → 412 problem+json; v1 response showing Deprecation/Sunset |
| 0:35–0:55 | Editor: AI suggestions (accept title, edit excerpt); budget counter |
| 0:55–1:15 | Push a `.md` file to GitHub → post appears/updates via webhook (smee log visible) |
| 1:15–1:30 | Cross-post to Dev.to → draft link; stop network to Dev.to → "retrying" state, core blog unaffected |
| 1:30–1:45 | Publication webhook: test event arrives at `tools/webhook_receiver.py`, signature verified; deliveries log |
| 1:45–1:55 | docs/TOPICS.md v5 tables with proofs; `docs/engineering.md` request lifecycle diagram |
