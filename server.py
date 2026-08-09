"""
Notes MCP Server (multi-user)
------------------------------
Exposes each signed-up user's own Neon Postgres notes database as MCP tools
for Vercel execution.
"""

import os
import json
import contextlib
import asyncpg

from mcp.server.fastmcp import FastMCP
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send

import db_control
import tenant_pools
from auth import BearerAuthMiddleware
from oauth import routes as oauth_routes
from webapp import routes as webapp_routes
from tenant_context import current_pool

mcp = FastMCP(
    "notes-mcp",
    instructions=(
        "Tools for searching and reading the user's personal notes app data. "
        "Use search_all or search_notes first for general questions."
    ),
)


def _get_pool() -> asyncpg.Pool:
    pool = current_pool.get()
    if pool is None:
        raise RuntimeError("No database connection resolved for this request")
    return pool


def _row_to_dict(row) -> dict:
    d = dict(row)
    for k, v in d.items():
        if hasattr(v, "isoformat"):
            d[k] = v.isoformat()
    return d


def _rows_to_json(rows) -> str:
    return json.dumps([_row_to_dict(r) for r in rows], ensure_ascii=False, indent=2)


async def _fetch_with_trgm_fallback(pool: asyncpg.Pool, trgm_sql: str, fallback_sql: str, *args):
    try:
        return await pool.fetch(trgm_sql, *args)
    except asyncpg.exceptions.UndefinedFunctionError:
        return await pool.fetch(fallback_sql, *args)


async def _fetch_optional_table_row(pool: asyncpg.Pool, sql: str, *args):
    try:
        return await pool.fetchrow(sql, *args)
    except asyncpg.exceptions.UndefinedTableError:
        return "unavailable"


async def _fetch_optional_with_trgm_fallback(pool: asyncpg.Pool, trgm_sql: str, fallback_sql: str, *args):
    try:
        return await pool.fetch(trgm_sql, *args)
    except asyncpg.exceptions.UndefinedTableError:
        return None
    except asyncpg.exceptions.UndefinedFunctionError:
        try:
            return await pool.fetch(fallback_sql, *args)
        except asyncpg.exceptions.UndefinedTableError:
            return None


_NOTES_TRGM_SQL = """
    SELECT id, workspace_id, workspace_name, title, content, type,
           media_url, media_name, color_hex, x, y, updated_at,
           similarity(title || ' ' || content, $1) AS score
    FROM notes
    WHERE (title % $1 OR content % $1 OR title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%')
      AND ($3::text IS NULL OR workspace_id = $3)
    ORDER BY score DESC
    LIMIT $2
"""
_NOTES_FALLBACK_SQL = """
    SELECT id, workspace_id, workspace_name, title, content, type,
           media_url, media_name, color_hex, x, y, updated_at
    FROM notes
    WHERE (title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%')
      AND ($3::text IS NULL OR workspace_id = $3)
    ORDER BY updated_at DESC
    LIMIT $2
"""


@mcp.tool()
async def search_notes(query: str, limit: int = 15, workspace_id: str | None = None) -> str:
    rows = await _fetch_with_trgm_fallback(
        _get_pool(), _NOTES_TRGM_SQL, _NOTES_FALLBACK_SQL, query, limit, workspace_id
    )
    return _rows_to_json(rows)


@mcp.tool()
async def get_note(note_id: str) -> str:
    row = await _get_pool().fetchrow("SELECT * FROM notes WHERE id = $1", note_id)
    if not row:
        return json.dumps({"error": f"No note found with id {note_id}"})
    return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)


@mcp.tool()
async def list_recent_notes(limit: int = 20, workspace_id: str | None = None) -> str:
    rows = await _get_pool().fetch(
        """
        SELECT id, workspace_id, workspace_name, title, type, updated_at
        FROM notes
        WHERE $2::text IS NULL OR workspace_id = $2
        ORDER BY updated_at DESC
        LIMIT $1
        """,
        limit, workspace_id,
    )
    return _rows_to_json(rows)


@mcp.tool()
async def list_workspaces() -> str:
    rows = await _get_pool().fetch("SELECT id, name, updated_at FROM workspaces ORDER BY updated_at DESC")
    return _rows_to_json(rows)


@mcp.tool()
async def search_transcripts(query: str, limit: int = 15) -> str:
    rows = await _fetch_optional_with_trgm_fallback(
        _get_pool(),
        """
        SELECT id, title, content, duration_seconds, audio_uri, created_at,
               similarity(title || ' ' || content, $1) AS score
        FROM transcripts
        WHERE title % $1 OR content % $1 OR title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%'
        ORDER BY score DESC
        LIMIT $2
        """,
        """
        SELECT id, title, content, duration_seconds, audio_uri, created_at
        FROM transcripts
        WHERE title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%'
        ORDER BY created_at DESC
        LIMIT $2
        """,
        query, limit,
    )
    if rows is None:
        return json.dumps({"available": False, "reason": "This account has no transcripts table."})
    return _rows_to_json(rows)


@mcp.tool()
async def get_transcript(transcript_id: str) -> str:
    row = await _fetch_optional_table_row(_get_pool(), "SELECT * FROM transcripts WHERE id = $1", transcript_id)
    if row == "unavailable":
        return json.dumps({"available": False, "reason": "This account has no transcripts table."})
    if row is None:
        return json.dumps({"error": f"No transcript found with id {transcript_id}"})
    return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)


@mcp.tool()
async def search_files(query: str, limit: int = 15) -> str:
    rows = await _fetch_optional_with_trgm_fallback(
        _get_pool(),
        """
        SELECT id, filename, file_type, topic, file_url, created_at,
               similarity(topic || ' ' || ocr_text, $1) AS score
        FROM file_metadata
        WHERE topic % $1 OR ocr_text % $1 OR topic ILIKE '%'||$1||'%' OR ocr_text ILIKE '%'||$1||'%'
        ORDER BY score DESC
        LIMIT $2
        """,
        """
        SELECT id, filename, file_type, topic, file_url, created_at
        FROM file_metadata
        WHERE topic ILIKE '%'||$1||'%' OR ocr_text ILIKE '%'||$1||'%'
        ORDER BY created_at DESC
        LIMIT $2
        """,
        query, limit,
    )
    if rows is None:
        return json.dumps({"available": False, "reason": "This account has no file_metadata table."})
    return _rows_to_json(rows)


@mcp.tool()
async def get_file(file_id: str) -> str:
    row = await _fetch_optional_table_row(_get_pool(), "SELECT * FROM file_metadata WHERE id = $1", file_id)
    if row == "unavailable":
        return json.dumps({"available": False, "reason": "This account has no file_metadata table."})
    if row is None:
        return json.dumps({"error": f"No file found with id {file_id}"})
    return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)


@mcp.tool()
async def search_all(query: str, limit: int = 10) -> str:
    pool = _get_pool()
    notes = await _fetch_with_trgm_fallback(pool, _NOTES_TRGM_SQL, _NOTES_FALLBACK_SQL, query, limit, None)
    transcripts = await _fetch_optional_with_trgm_fallback(
        pool,
        """
        SELECT id, title, content, created_at,
               similarity(title || ' ' || content, $1) AS score
        FROM transcripts
        WHERE title % $1 OR content % $1 OR title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%'
        ORDER BY score DESC
        LIMIT $2
        """,
        """
        SELECT id, title, content, created_at
        FROM transcripts
        WHERE title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%'
        ORDER BY created_at DESC
        LIMIT $2
        """,
        query, limit,
    )
    files = await _fetch_optional_with_trgm_fallback(
        pool,
        """
        SELECT id, filename, topic, file_type, created_at,
               similarity(topic || ' ' || ocr_text, $1) AS score
        FROM file_metadata
        WHERE topic % $1 OR ocr_text % $1 OR topic ILIKE '%'||$1||'%' OR ocr_text ILIKE '%'||$1||'%'
        ORDER BY score DESC
        LIMIT $2
        """,
        """
        SELECT id, filename, topic, file_type, created_at
        FROM file_metadata
        WHERE topic ILIKE '%'||$1||'%' OR ocr_text ILIKE '%'||$1||'%'
        ORDER BY created_at DESC
        LIMIT $2
        """,
        query, limit,
    )

    result = {
        "notes": [_row_to_dict(r) for r in notes],
        "transcripts": [_row_to_dict(r) for r in transcripts] if transcripts is not None else None,
        "files": [_row_to_dict(r) for r in files] if files is not None else None,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# Vercel Serverless Middleware: Guarantees DB control pool initialization on invocation
class DatabaseInitMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            await db_control.init_control_pool()
        await self.app(scope, receive, send)


app = mcp.streamable_http_app()
app.router.routes.extend(oauth_routes)
app.router.routes.extend(webapp_routes)

session_secret = os.environ.get("SESSION_SECRET_KEY")
if not session_secret:
    raise RuntimeError("SESSION_SECRET_KEY environment variable is not set")
https_only = os.environ.get("SESSION_HTTPS_ONLY", "true").lower() != "false"

# Middlewares execution order: DatabaseInitMiddleware runs FIRST on incoming requests
app.add_middleware(SessionMiddleware, secret_key=session_secret, same_site="lax", https_only=https_only)
app.add_middleware(BearerAuthMiddleware)
app.add_middleware(DatabaseInitMiddleware)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
