# Performance evidence — Blog Platform
_Claude: append, don't rewrite. Every optimisation gets a Before, an After, and the one change in between._

## Setup
- Dataset: `make seed-perf` → 100k posts, 500 users, 500k likes, 200k comments. Run `ANALYZE` afterwards.
- Machine: <CPU / RAM / Docker resources>
- Load test: `make loadtest` — Locust, 50 users, 60 s, anonymous feed + post detail mix.

## Summary (fill at T-037)
| Query / endpoint | Before p95 | After p95 | Queries before → after | Change that made the difference |
|---|---|---|---|---|
| Feed page 1 | | | | |
| Feed page 500 (offset) vs keyset | | | | |
| Post detail | | | | |
| Author page | | | | |
| Title filter `q=` | | | | |
| My posts | | | | |
| Feed payload (bytes, raw → gzip → fields) | | | | |

## Log
<!-- ### YYYY-MM-DD — <query> — T-0XX
Before: plan file + key line (e.g. Seq Scan on posts, 412 ms)
Change: <one change>
After: plan file + key line (e.g. Index Scan using ix_posts_author_status_published, 3.1 ms) -->
