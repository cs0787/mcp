"""
The control-plane database.

This is a SEPARATE, small Postgres/Neon database that belongs to this MCP
service itself -- it is NOT any user's personal notes database. It stores
one row per signed-up user: their login, their hashed API key, and their
(encrypted) personal Neon connection string.

Set CONTROL_DATABASE_URL to this database's connection string. Don't reuse
a user's own notes DB for this.
"""

import os
import asyncpg

CONTROL_DATABASE_URL = os.environ.get("CONTROL_DATABASE_URL")

_pool: asyncpg.Pool | None = None


async def init_control_pool() -> asyncpg.Pool:
    global _pool
    if not CONTROL_DATABASE_URL:
        raise RuntimeError("CONTROL_DATABASE_URL environment variable is not set")
    _pool = await asyncpg.create_pool(CONTROL_DATABASE_URL, min_size=1, max_size=5, ssl="require")
    await _init_schema(_pool)
    return _pool


async def close_control_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_control_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Control pool not initialized -- init_control_pool() must run at startup")
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
                api_key_hash TEXT UNIQUE,
                connection_string_encrypted TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )


# ---------------------------------------------------------------------------
# Queries
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


async def get_user_by_api_key_hash(pool: asyncpg.Pool, api_key_hash: str):
    return await pool.fetchrow("SELECT * FROM users WHERE api_key_hash = $1", api_key_hash)


async def set_api_key_hash(pool: asyncpg.Pool, user_id: str, api_key_hash: str) -> None:
    await pool.execute(
        "UPDATE users SET api_key_hash = $1, updated_at = now() WHERE id = $2",
        api_key_hash,
        user_id,
    )


async def set_connection_string(pool: asyncpg.Pool, user_id: str, encrypted_connection_string: str) -> None:
    await pool.execute(
        "UPDATE users SET connection_string_encrypted = $1, updated_at = now() WHERE id = $2",
        encrypted_connection_string,
        user_id,
    )
