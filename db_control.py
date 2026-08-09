"""
The control-plane database pool manager for Vercel Serverless.
"""

import os
import asyncio
import asyncpg

_pool: asyncpg.Pool | None = None
_pool_loop: asyncio.AbstractEventLoop | None = None
_init_lock = asyncio.Lock()


async def init_control_pool() -> asyncpg.Pool:
    global _pool, _pool_loop
    current_loop = asyncio.get_running_loop()

    # Reuse pool if active and on the same event loop
    if _pool is not None and _pool_loop == current_loop and not getattr(_pool, "_closed", True):
        return _pool

    async with _init_lock:
        if _pool is not None and _pool_loop == current_loop and not getattr(_pool, "_closed", True):
            return _pool

        control_db_url = os.environ.get("CONTROL_DATABASE_URL")
        if not control_db_url:
            raise RuntimeError("CONTROL_DATABASE_URL environment variable is missing in Vercel settings.")

        # Clean up stale pool if loop changed
        if _pool is not None and not getattr(_pool, "_closed", True):
            try:
                await _pool.close()
            except Exception:
                pass

        _pool = await asyncpg.create_pool(control_db_url, min_size=1, max_size=3, ssl="require")
        _pool_loop = current_loop
        await _init_schema(_pool)
        return _pool


async def close_control_pool() -> None:
    global _pool, _pool_loop
    if _pool is not None:
        await _pool.close()
        _pool = None
        _pool_loop = None


def get_control_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Control pool not initialized.")
    return _pool


async def _init_schema(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                connection_string_encrypted TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                key_hash TEXT UNIQUE NOT NULL,
                label TEXT NOT NULL DEFAULT 'API key',
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                last_used_at TIMESTAMPTZ,
                revoked_at TIMESTAMPTZ
            )
            """
        )
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)")


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
async def create_user(pool: asyncpg.Pool, email: str, password_hash: str) -> str:
    row = await pool.fetchrow(
        "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id",
        email.strip().lower(),
        password_hash,
    )
    return str(row["id"])


async def get_user_by_email(pool: asyncpg.Pool, email: str):
    return await pool.fetchrow("SELECT * FROM users WHERE email = $1", email.strip().lower())


async def get_user_by_id(pool: asyncpg.Pool, user_id: str):
    return await pool.fetchrow("SELECT * FROM users WHERE id = $1", user_id)


async def set_connection_string(pool: asyncpg.Pool, user_id: str, encrypted_connection_string: str) -> None:
    await pool.execute(
        "UPDATE users SET connection_string_encrypted = $1, updated_at = now() WHERE id = $2",
        encrypted_connection_string,
        user_id,
    )


# ---------------------------------------------------------------------------
# API keys
# ---------------------------------------------------------------------------
async def create_api_key(pool: asyncpg.Pool, user_id: str, key_hash: str, label: str) -> str:
    row = await pool.fetchrow(
        "INSERT INTO api_keys (user_id, key_hash, label) VALUES ($1, $2, $3) RETURNING id",
        user_id, key_hash, label,
    )
    return str(row["id"])


async def get_active_key_owner(pool: asyncpg.Pool, key_hash: str):
    return await pool.fetchrow(
        """
        SELECT u.id AS user_id, u.email, u.connection_string_encrypted, k.id AS api_key_id
        FROM api_keys k
        JOIN users u ON u.id = k.user_id
        WHERE k.key_hash = $1 AND k.revoked_at IS NULL
        """,
        key_hash,
    )


async def touch_api_key_last_used(pool: asyncpg.Pool, api_key_id: str) -> None:
    await pool.execute("UPDATE api_keys SET last_used_at = now() WHERE id = $1", api_key_id)


async def list_api_keys(pool: asyncpg.Pool, user_id: str):
    return await pool.fetch(
        """
        SELECT id, label, created_at, last_used_at, revoked_at
        FROM api_keys
        WHERE user_id = $1
        ORDER BY created_at DESC
        """,
        user_id,
    )


async def revoke_api_key(pool: asyncpg.Pool, user_id: str, api_key_id: str) -> bool:
    result = await pool.execute(
        "UPDATE api_keys SET revoked_at = now() WHERE id = $1 AND user_id = $2 AND revoked_at IS NULL",
        api_key_id, user_id,
    )
    return result.endswith("1")
