# UI/UX Direction — Blog Platform

## Design intent
Two situations: a reader landing from a link who must see the article immediately, and an author who must
be able to write, publish and find their drafts without hunting. Within 10 seconds anyone must be able to tell
whether they are logged in, what they can do on this post, and how to read more.

## Principles (ranked — when they conflict, higher wins)
1. Reading comfort over density — the article body is the product.
2. Auth state always obvious — header shows who you are or a clear Log in / Sign up.
3. Never show an action the user can't take — hide Edit/Delete for non-owners; show "Log in to like/comment" to anonymous users instead of a dead button.
4. Consistency with shadcn/ui defaults over custom styling.
5. Speed of the demo path — every Must FR reachable in ≤ 2 clicks from the header.

## Visual system
- Component library: shadcn/ui on Tailwind CSS
- Colours: primary `#2563EB`, accent/like `#E11D48`, success `#16A34A`, warn `#D97706`, error `#DC2626`; text `#0F172A` on `#FFFFFF`, muted `#64748B`, borders `#E2E8F0`
- Typography: Inter (UI, 16px base); Source Serif 4 for article body (18px, line-height 1.7, max width 68ch) — self-hosted via `@fontsource`
- Spacing scale: Tailwind 4/8/12/16/24/32/48
- Dark mode: no (out of scope)
- Draft vs published: text badge ("Draft" / "Published") with colour — never colour alone

## Layout & navigation
Single app shell: top header (logo → Home; "Write" button and avatar menu with "My posts" / "Log out" when logged in;
"Log in" / "Sign up" when not). Centered content column, max width 768px. No sidebar.
(v3) Header adds a publication switcher (personal + team publications) for logged-in users.
(v4) Avatar menu shows "Moderation" and/or "Admin" only when `/me/permissions` grants them; admin/moderation pages use a wider (1200px) table layout.

## Screen inventory
| Screen | Route | Purpose | Status |
|---|---|---|---|
| Home feed | `/` | Paginated published posts: title, excerpt, author, date, like & comment counts | planned |
| Post detail | `/p/:slug` | Rendered article, like button, comments list + form | planned |
| Login | `/login` | Email + password | planned |
| Register | `/register` | Email, username, display name, password | planned |
| My posts | `/me/posts` | Table of own posts with status badge, Edit, Publish/Unpublish, Delete | planned |
| Editor | `/write`, `/edit/:id` | Title + Markdown textarea with Write/Preview tabs; Save draft / Publish | planned |
| Author page | `/u/:username` | That author's published posts (FR-14, Could) | planned |
| Import (v2) | `/import` | Drop zone (.docx, .pdf; up to 5), per-file row: upload progress bar → Queued → Converting → Ready ("Review draft") or Failed (plain-language reason) | planned |
| Import history (v2) | `/me/imports` | Table: file, size, status, warnings, link to draft, "Download original", delete | planned |
| Login (v3 update) | `/login` | Adds provider buttons (Google, Microsoft, Yahoo, Apple) above the email form; OAuth error messages | planned |
| Settings (v3) | `/settings/account`, `/settings/security` | Profile, linked accounts, set/change password, active sessions (revoke, log out everywhere), security activity | planned |
| Publication page (v3) | `/pub/:slug` | Public list of a publication's published posts | planned |
| Publication admin (v3/v4) | `/pub/:slug/manage/members`, `/invites`, `/settings`, `/audit` | Members & roles, invite links, settings, publication audit log (tabs shown per permission) | planned |
| Moderation queue (v4) | `/moderation` | Open reports grouped by content, preview, Hide (with reason) / Dismiss; hidden-content list with Unhide | planned |
| Admin: users (v4) | `/admin/users` | Search users, suspend/unsuspend with reason, assign/revoke moderator | planned |
| Admin: audit log (v4) | `/admin/audit` | Filterable audit table (category, actor, publication, outcome, date), row detail with before/after, CSV export | planned |
| Integrations (v5) | `/settings/integrations` | GitHub (Connect/Disconnect, account, status), Dev.to (API key input, last4, status), each with last success/failure and "Reconnect" when `needs_reauth` | planned |
| GitHub sync (v5) | `/pub/:slug/manage/github` | Repo, branch, folder pickers; last sync commit; "Sync now"; list of synced files → posts | planned |
| Webhooks (v5) | `/pub/:slug/manage/webhooks` | Endpoints table (URL, events, active, failures), create (secret shown once with copy button), rotate secret, send test, deliveries log with status/duration | planned |
| Access tokens (v5, Could) | `/settings/tokens` | Create (name, publication, permissions, expiry) → token shown once; list; revoke | planned |
| Not found | `*` | Also used when a draft is requested by a non-owner | planned |

## Patterns to reuse
- Lists: numbered pagination (Prev / Next + page number), not infinite scroll. Empty state with a one-line message and a primary action ("Write your first post").
- Forms: validate on blur and on submit; show server 422 field errors under the field; disable submit while pending.
- Loading/empty/error states: required on every data view. Skeletons for feed and post; error state shows message + Retry.
- Like button: optimistic toggle, rolled back on error; shows count; `aria-pressed`.
- Destructive actions (delete post/comment): inline confirm (shadcn AlertDialog is allowed only here).
- After login/register: return the user to the page they came from.
- (v2) Upload: validate type/size in the browser for fast feedback, but always show the server's verdict per file. Rejected files stay listed with the reason; accepted ones keep going.
- (v2) Import warnings shown as a yellow notice at the top of the imported draft in the editor ("Images were removed from this document").
- (v2) Imported posts show an "Imported" badge in My posts and, if set, "Originally published 12 Mar 2019" under the title.
- (v2) My posts: row checkboxes + sticky batch bar (Publish, Unpublish, Delete) with per-row result after the action; Export menu (CSV, Excel).
- (v2) Post detail: "Download PDF" link in the post footer.
- (v2) Feed filter bar above the list: author, date from/to, title contains, Imported/Native, sort (Newest, Most liked). Filters live in the URL query string so they are shareable and cacheable.
- (v2) 429: toast "Too many attempts — try again in N seconds" using `Retry-After`; disable the triggering button for that time.
- (v3) Provider buttons follow each provider's published brand guidelines (logo, wording "Sign in with …", colours); never restyle provider logos.
- (v3) Re-auth prompt: sensitive actions (BR-35) open a small re-auth page/step ("Confirm it's you") and then complete the original action.
- (v4) Permission-based rendering: wrap every action in `<Can permission="post:update" resource={post}>`; nav items, tabs and bulk-action buttons included. Route guard `<RequirePermission>` redirects to Not found (not "Forbidden") when a page's permission is missing.
- (v4) Disabled vs hidden: hide actions the user can never take; show but disable (with a tooltip reason) only when the user holds the permission but the resource state blocks it (e.g. "Publish" on a hidden post).
- (v4) Role badges in member lists and a plain-language "What can this role do?" popover generated from `docs/permissions.md` data.
- (v4) Report: "Report" in a post's/comment's overflow menu → small form (reason radio + optional note); success toast; the item shows "Reported" for that user.
- (v4) Hidden content: author sees a red banner "Hidden by moderation: <reason>"; readers get Not found.
- (v4) Audit tables: newest first, relative time with exact timestamp on hover, outcome as text badge (Allowed / Denied / Failed), request ID copyable for support.
- (v4) "View as" (Could): owner can toggle "View as Writer / Editor / Reader" on publication pages — UI-only preview banner; the API is still called as the real user.
- (v5) Editor AI panel: "Suggest title & excerpt" button → loading state (max 30 s, cancellable) → three suggestion cards (title, excerpt, SEO description) each with Use / Edit / Dismiss; shows remaining daily requests; first use shows "Your draft text is sent to Anthropic to generate suggestions." with a link to the privacy note.
- (v5) Cross-post panel on a published post: "Cross-post to Dev.to" (checkbox "Publish on Dev.to", default off) → status chip Pending → Synced (link) / Failed (reason + Retry). If not connected: link to Settings → Integrations.
- (v5) GitHub-managed posts: editor is read-only with banner "Managed in GitHub — edit `<path>` in `<repo>`" and a link to the file.
- (v5) Upstream failures: one consistent pattern — inline notice "Dev.to is not responding. We'll retry automatically." (jobs) or "AI suggestions are unavailable right now." (sync); never a raw error or stack trace.
- (v5) Secrets in UI: API keys and webhook secrets are write-only inputs; after save only `••••last4` is shown; one-time secrets have a copy button and a "You won't see this again" warning.
- (v4) Version footer: small `vX.Y.Z · <short SHA>` from `/version` on admin pages, to match errors in GlitchTip with releases.

## Accessibility
- WCAG AA contrast; all interactive elements keyboard reachable with visible focus ring.
- Every input has a `<label>`; errors linked with `aria-describedby`.
- Status never conveyed by colour alone.

## Do not
- No modals for primary flows (login, editor) — use pages.
- No WYSIWYG editor, no image upload UI (document upload on `/import` only).
- No custom icon sets — use lucide-react (ships with shadcn/ui).
- No rendering of raw HTML from post bodies.

## References
- Medium / dev.to article layout for reading width and typography.
