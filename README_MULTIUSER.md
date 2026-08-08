# Multi-user setup

## What changed from the single-user version

- No more one global `DATABASE_URL` / `MCP_API_KEY` pair. Instead there's a
  small **control-plane database** (`CONTROL_DATABASE_URL`) that this
  service owns, holding one row per signed-up user: email, hashed password,
  hashed API key, and their **encrypted** personal Neon connection string.
- New pages: `/signup`, `/login`, `/dashboard`, `/logout`. A user signs up,
  gets an API key immediately, and pastes their own Neon connection string
  (the same one their Android app uses) into the dashboard.
- `auth.py`'s `BearerAuthMiddleware` now hashes the incoming
  `Authorization: Bearer <key>` and looks up *which user* it belongs to,
  then hands that request the right database pool (`tenant_pools.py`
  caches one pool per user, not one global pool).
- `oauth.py` (the OAuth 2.1 shim Claude's connector UI needs) now validates
  the key someone types into the "Authorize" page against the control-plane
  DB instead of a single hardcoded value, so it works for any signed-up user.
- **Bug fix:** the old `notes` queries selected a `created_at` column that
  your Android app's `notes` table (see `CloudSyncWorker.kt`) never
  creates -- this would have thrown a Postgres error for every real user.
  Queries now match the actual schema (`workspace_id`, `workspace_name`,
  `title`, `content`, `type`, `media_url`, `media_name`, `color_hex`, `x`,
  `y`, `updated_at`).
- `search_transcripts` / `get_transcript` / `search_files` / `get_file`
  degrade gracefully (`{"available": false, ...}`) instead of crashing for
  accounts whose database doesn't have those tables -- which is every
  account created by the current Android app, since it only creates
  `workspaces` and `notes`.
- Fuzzy search (`pg_trgm` / `similarity()`) is attempted per-user on first
  connection; if a user's Neon role can't create the extension, search
  automatically falls back to plain `ILIKE` instead of failing.

## Required environment variables (set these on Render)

| Variable | What it is | How to generate |
|---|---|---|
| `CONTROL_DATABASE_URL` | Connection string for **this app's own** accounts DB. Create a **separate** Neon project for this -- do not point it at any user's personal notes DB. | From the Neon dashboard, like any connection string |
| `ENCRYPTION_KEY` | Symmetric key used to encrypt stored connection strings at rest | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `SESSION_SECRET_KEY` | Signs the browser session cookie for signup/login/dashboard | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `BASE_URL` | Only needed for local testing -- Render sets `RENDER_EXTERNAL_URL` automatically | -- |

The old `DATABASE_URL` and `MCP_API_KEY` env vars are no longer used and
can be removed from Render.

## Deploying

1. Create a new, separate Neon project for the control-plane DB (small --
   it only ever stores account rows, not notes).
2. Set the four env vars above in the Render dashboard.
3. Deploy. On first startup the server automatically creates the `users`
   table in the control-plane DB (see `db_control.py`, idempotent
   `CREATE TABLE IF NOT EXISTS`).
4. Visit `https://<your-app>.onrender.com/signup` to create the first
   account, get an API key, and paste in a Neon connection string.

## Connecting an AI app

- **Direct bearer token** (apps that support it): server URL
  `https://<your-app>.onrender.com/mcp`, header
  `Authorization: Bearer <your API key>`.
- **Claude's connector UI**: it'll walk through an OAuth screen; the
  "password" it asks for on that screen is the same API key from your
  dashboard.

## Testing your changes

`tests/smoke_test.py` is a self-contained smoke test (no live Postgres
needed -- it mocks the control-plane DB and the per-user pool) covering
signup/login/dashboard, API key regeneration, the auth middleware's 401
behavior, and the notes-tool fallback logic. Run it after any change:

```
pip install -r requirements.txt httpx
python tests/smoke_test.py
```

## Things worth doing next (not included here)

- **Rate limiting** on `/signup` and `/login` to slow down brute-forcing.
- **Password reset** flow (currently none -- a user who forgets their
  password has no self-serve recovery).
- **Multiple API keys per user** if you want per-app revocation instead of
  one shared key for every connected AI app.
- Consider whether you want email verification before an account can save
  a connection string.
