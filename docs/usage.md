# Usage walkthroughs (v1)

Start the app with `cp .env.example .env && make setup`, then open http://localhost:5173.
The demo users below are created by `make seed` and all use the password `demo-password-1`.

| User | Email | Has |
|---|---|---|
| Alice Moreno | alice@example.com | 3 published posts, 1 draft |
| Bob Okafor | bob@example.com | 2 published posts, 1 draft |
| Carol Lindqvist | carol@example.com | 2 published posts, 1 draft |

Tip: use two browser profiles (or a normal and a private window) to be two users at once —
each has its own login cookie.

---

## 1. Reader (not logged in)
1. Open http://localhost:5173. The feed lists published posts, newest first, 10 per page, each
   with its excerpt, author, date, like count and comment count. Use **Next →** at the bottom
   to page through; the page number is in the URL (`?page=2`), so you can share it.
2. Click a title to open the post (`/p/<slug>`). The body is rendered from Markdown. Comments are
   listed oldest first underneath.
3. Where a logged-in user would act, you see **Log in to like** and **Log in to comment** instead
   of buttons. Following either takes you to the login page and back to this post afterwards.
4. Click an author's name to see only their published posts (`/u/<username>`).
5. Drafts never appear. If you guess a draft's URL you get **Not found** — the app never confirms
   that a draft exists.

## 2. Author (Alice)
1. Click **Log in**, sign in as `alice@example.com`. The header now shows her avatar and username.
2. Click **Write**. Enter a title and a Markdown body; switch to **Preview** to see the result.
3. Click **Save draft**. You land on **My posts** (avatar menu → My posts), where the new post
   shows a yellow **Draft** badge. Drafts are only visible to you.
4. Click **Publish** on that row (or open it with **Edit** and click **Publish**). The badge turns
   green **Published** and the post appears at the top of the public feed. Its publish date is set
   now — and kept if you later unpublish and republish.
5. Click **Edit** and change the title. The URL (slug) stays the same, so shared links keep working.
6. **Unpublish** hides the post from everyone else again; its likes and comments are kept and come
   back when you republish.
7. **Delete** asks for confirmation inline ("Delete this post? Yes, delete / Cancel"). Deleting a
   post also deletes its likes and comments.
8. On your own post there is no like button — only the count. You can't like your own work.
9. **Log out** from the avatar menu returns you to the feed as a reader.

## 3. Commenter (Bob, on Alice's post)
1. In a second browser profile, log in as `bob@example.com`.
2. Open one of Alice's posts, e.g. "Why I Switched to Writing in Markdown".
3. Click the **♡** button: the count goes up immediately and the heart fills. Click again to
   unlike. If the server rejects the change, the button rolls back and shows the reason.
4. Type a comment (up to 2,000 characters; the counter shows how many you've used) and click
   **Comment**. It appears at the end of the list.
5. Your own comments show a **Delete** button. Other people's don't.
6. Back in Alice's profile, reload the post: Alice can delete **any** comment on her own post,
   including Bob's. A third user (Carol) can delete neither.

## 4. Doing the same with the API
Everything above is also available over HTTP. See [api.md](api.md) for every endpoint with a
curl example, or open the interactive docs at http://localhost:8000/docs.

```bash
# log in and keep the cookie
curl -c cookies.txt -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","password":"demo-password-1"}' \
  http://localhost:8000/api/v1/auth/login

# create a draft, then publish it (use the "id" from the first response)
curl -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"title":"From curl","body_md":"Hello **API**"}' http://localhost:8000/api/v1/posts
curl -X PATCH -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"status":"published"}' http://localhost:8000/api/v1/posts/<id>
```
