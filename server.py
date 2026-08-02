"""
Second Brain MCP Server
------------------------
Exposes your Neon Postgres "second brain" (notes, transcripts, file_metadata)
as MCP tools that Claude, ChatGPT, Gemini, etc. can call as a remote connector.

Transport: streamable-http (works as a remote connector, not just local stdio)
Auth: simple bearer token via MCP_API_KEY (see auth.py)
"""

import os
import json
import asyncpg
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP, Context

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")


@dataclass
class AppContext:
    pool: asyncpg.Pool


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    # Neon works great with a small pool since it's serverless on their end too
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5, ssl="require")
    try:
        yield AppContext(pool=pool)
    finally:
        await pool.close()


mcp = FastMCP(
    "second-brain",
    instructions=(
        "Tools for searching and reading the user's personal 'second brain': "
        "text notes, voice memo transcripts, and OCR'd files/PDFs. "
        "Use search_all first for general questions. Use the more specific "
        "search/get tools when the user names a content type explicitly."
    ),
    lifespan=lifespan,
)


def _row_to_dict(row) -> dict:
    d = dict(row)
    for k, v in d.items():
        # datetimes aren't JSON serializable by default
        if hasattr(v, "isoformat"):
            d[k] = v.isoformat()
    return d


def _rows_to_json(rows) -> str:
    return json.dumps([_row_to_dict(r) for r in rows], ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Unified search across all three tables
# ---------------------------------------------------------------------------
@mcp.tool()
async def search_all(ctx: Context, query: str, limit: int = 10) -> str:
    """Fuzzy-search notes, voice transcripts, and file/PDF OCR text all at once.

    Use this as the default search tool for any general question like
    "what do I know about X" or "find my notes on Y".

    Args:
        query: search text (matched fuzzily against titles/content/OCR text)
        limit: max results per content type (default 10)
    """
    pool = ctx.request_context.lifespan_context.pool
    async with pool.acquire() as conn:
        notes = await conn.fetch(
            """
            SELECT id, title, content, type, created_at,
                   similarity(title || ' ' || content, $1) AS score
            FROM notes
            WHERE title % $1 OR content % $1 OR title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%'
            ORDER BY score DESC
            LIMIT $2
            """,
            query, limit,
        )
        transcripts = await conn.fetch(
            """
            SELECT id, title, content, created_at,
                   similarity(title || ' ' || content, $1) AS score
            FROM transcripts
            WHERE title % $1 OR content % $1 OR title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%'
            ORDER BY score DESC
            LIMIT $2
            """,
            query, limit,
        )
        files = await conn.fetch(
            """
            SELECT id, filename, topic, file_type, created_at,
                   similarity(topic || ' ' || ocr_text, $1) AS score
            FROM file_metadata
            WHERE topic % $1 OR ocr_text % $1 OR topic ILIKE '%'||$1||'%' OR ocr_text ILIKE '%'||$1||'%'
            ORDER BY score DESC
            LIMIT $2
            """,
            query, limit,
        )

    result = {
        "notes": [_row_to_dict(r) for r in notes],
        "transcripts": [_row_to_dict(r) for r in transcripts],
        "files": [_row_to_dict(r) for r in files],
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------
@mcp.tool()
async def search_notes(ctx: Context, query: str, limit: int = 15) -> str:
    """Fuzzy-search only text notes by title/content.

    Args:
        query: search text
        limit: max results (default 15)
    """
    pool = ctx.request_context.lifespan_context.pool
    rows = await pool.fetch(
        """
        SELECT id, title, content, type, created_at, updated_at,
               similarity(title || ' ' || content, $1) AS score
        FROM notes
        WHERE title % $1 OR content % $1 OR title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%'
        ORDER BY score DESC
        LIMIT $2
        """,
        query, limit,
    )
    return _rows_to_json(rows)


@mcp.tool()
async def get_note(ctx: Context, note_id: str) -> str:
    """Fetch a single note by its exact id.

    Args:
        note_id: the note's primary key
    """
    pool = ctx.request_context.lifespan_context.pool
    row = await pool.fetchrow("SELECT * FROM notes WHERE id = $1", note_id)
    if not row:
        return json.dumps({"error": f"No note found with id {note_id}"})
    return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)


@mcp.tool()
async def list_recent_notes(ctx: Context, limit: int = 20) -> str:
    """List the most recently updated notes.

    Args:
        limit: max results (default 20)
    """
    pool = ctx.request_context.lifespan_context.pool
    rows = await pool.fetch(
        "SELECT id, title, type, updated_at FROM notes ORDER BY updated_at DESC LIMIT $1",
        limit,
    )
    return _rows_to_json(rows)


# ---------------------------------------------------------------------------
# Transcripts (voice memos)
# ---------------------------------------------------------------------------
@mcp.tool()
async def search_transcripts(ctx: Context, query: str, limit: int = 15) -> str:
    """Fuzzy-search voice memo transcripts by title/content.

    Args:
        query: search text
        limit: max results (default 15)
    """
    pool = ctx.request_context.lifespan_context.pool
    rows = await pool.fetch(
        """
        SELECT id, title, content, duration_seconds, audio_uri, created_at,
               similarity(title || ' ' || content, $1) AS score
        FROM transcripts
        WHERE title % $1 OR content % $1 OR title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%'
        ORDER BY score DESC
        LIMIT $2
        """,
        query, limit,
    )
    return _rows_to_json(rows)


@mcp.tool()
async def get_transcript(ctx: Context, transcript_id: str) -> str:
    """Fetch a single voice transcript by its exact id.

    Args:
        transcript_id: the transcript's primary key
    """
    pool = ctx.request_context.lifespan_context.pool
    row = await pool.fetchrow("SELECT * FROM transcripts WHERE id = $1", transcript_id)
    if not row:
        return json.dumps({"error": f"No transcript found with id {transcript_id}"})
    return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Files / PDFs (OCR)
# ---------------------------------------------------------------------------
@mcp.tool()
async def search_files(ctx: Context, query: str, limit: int = 15) -> str:
    """Fuzzy-search PDFs/images by topic or OCR'd text content.

    Args:
        query: search text
        limit: max results (default 15)
    """
    pool = ctx.request_context.lifespan_context.pool
    rows = await pool.fetch(
        """
        SELECT id, filename, file_type, topic, file_url, created_at,
               similarity(topic || ' ' || ocr_text, $1) AS score
        FROM file_metadata
        WHERE topic % $1 OR ocr_text % $1 OR topic ILIKE '%'||$1||'%' OR ocr_text ILIKE '%'||$1||'%'
        ORDER BY score DESC
        LIMIT $2
        """,
        query, limit,
    )
    return _rows_to_json(rows)


@mcp.tool()
async def get_file(ctx: Context, file_id: str) -> str:
    """Fetch full metadata + OCR text for one file by its exact id.

    Args:
        file_id: the file_metadata primary key
    """
    pool = ctx.request_context.lifespan_context.pool
    row = await pool.fetchrow("SELECT * FROM file_metadata WHERE id = $1", file_id)
    if not row:
        return json.dumps({"error": f"No file found with id {file_id}"})
    return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import uvicorn
    from auth import BearerAuthMiddleware

    app = mcp.streamable_http_app()
    app.add_middleware(BearerAuthMiddleware)

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
