# Multi-user setup

## How it works, end to end

1. A user visits `/signup`, creates an account (email + password), and pastes
   their Neon connection string (the same one their Android app uses) into
   `/dashboard`. No API key exists yet at this point.
2. They add this server (`https://<your-app>.onrender.com/mcp`) as a
   connector in Claude.
3. Claude opens `/authorize` in a browser. If there's no session cookie,
   the user is sent to `/login?next=/authorize?...` first -- they log in (or
   sign up) with their **website account**, and land right back on the same
   consent screen they were headed to, not a generic dashboard.
4. The consent screen says "Allow access to your notes?" -- no key to type
   or copy-paste anywhere. Clicking **Allow** mints a *fresh* API key scoped
   to that one connection (labeled with the connecting app's client id) and
   redirects back to Claude with an authorization code.
5. Claude exchanges that code (with PKCE) for the freshly minted key at
   `/token`. From then on, every `/mcp` request from Claude carries that key,
   and `BearerAuthMiddleware` (`auth.py`) hashes it, looks up which user it
   belongs to, decrypts *their* Neon connection string, and routes the
   request to *their* database pool.

Connecting a second AI app repeats step 3 onward and mints a second,
independent key -- revoking one from the dashboard never breaks the other.

Two different users repeating this whole flow each get their own row in the
control-plane DB and their own key(s), each pointing at their own separate
Neon database. One running server, many isolated tenants.

## What's in the control-plane database

A **separate** small Neon project (`CONTROL_DATABASE_URL`) that belongs to
this service, not to any user's notes:

- `users` -- email, hashed password, encrypted personal Neon connection string
- `api_keys` -- one row per issued key: which user it belongs to, its hash
  (never the raw key), a label, and `revoked_at`. A user can have several --
  typically one per connected AI app.

## Required environment variables (set these on Render)

| Variable | What it is | How to generate |
|---|---|---|
| `CONTROL_DATABASE_URL` | Connection string for **this app's own** accounts DB -- a separate Neon project, not any user's notes DB | From the Neon dashboard |
| `ENCRYPTION_KEY` | Symmetric key encrypting stored connection strings at rest | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `SESSION_SECRET_KEY` | Signs the browser session cookie for signup/login/dashboard | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `BASE_URL` | Only needed for local testing -- Render sets `RENDER_EXTERNAL_URL` automatically | -- |

The old `DATABASE_URL` and `MCP_API_KEY` env vars are no longer used.

## Deploying

1. Create a separate Neon project for the control-plane DB.
2. Set the env vars above on Render.
3. Deploy -- `users`/`api_keys` tables are created automatically on startup
   (idempotent `CREATE TABLE IF NOT EXISTS`).
4. Visit `/signup`, create an account, paste in a Neon connection string,
   then add the connector in Claude and go through Allow.

## Connecting an AI app

- **Apps with an OAuth "Add connector" flow** (Claude): just log in and click
  Allow -- no key to handle.
- **Apps that want a raw bearer token pasted directly**: click "Generate a
  key manually" on the dashboard, copy it once, use it as
  `Authorization: Bearer <key>` against `https://<your-app>.onrender.com/mcp`.

## Managing keys

The dashboard lists every active key (its label, when it was created, when
it was last used) with a **Revoke** button next to each. Revoking is
immediate and only affects that one key.

## Testing your changes

`tests/smoke_test.py` is self-contained (mocks the control-plane DB and the
per-user pool -- no live Postgres needed) and covers signup/login, the full
OAuth session-login-to-token flow with PKCE, independent key revocation, the
auth middleware's 401 behavior, and the notes-tool fallback logic:

```
pip install -r requirements.txt httpx
python tests/smoke_test.py
```

## Things worth doing next (not included here)

- **Rate limiting** on `/signup` and `/login`.
- **Password reset** flow (currently none).
- Consider email verification before an account can save a connection string.
