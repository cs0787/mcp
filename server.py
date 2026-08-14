"""
Notes MCP Server (multi-user bidirectional sync)
------------------------------------------------
Exposes read and write tools for each user's personal Neon Postgres database,
enabling Claude and other AI models to create and update notes, workspaces, and files.
"""

import os
import json
import contextlib
import asyncpg
import uuid

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
        "Tools for searching, reading, creating, and updating the user's personal notes app data. "
        "Use create_note to add new notes or update_note to modify existing ones. "
        "Changes will automatically sync to the user's Android app."
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


# ---------------------------------------------------------------------------
# READ TOOLS (Search & Get)
# ---------------------------------------------------------------------------
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
    """Fuzzy-search notes by title/content."""
    rows = await _fetch_with_trgm_fallback(
        _get_pool(), _NOTES_TRGM_SQL, _NOTES_FALLBACK_SQL, query, limit, workspace_id
    )
    return _rows_to_json(rows)


@mcp.tool()
async def get_note(note_id: str) -> str:
    """Fetch a single note by its exact id."""
    row = await _get_pool().fetchrow("SELECT * FROM notes WHERE id = $1", note_id)
    if not row:
        return json.dumps({"error": f"No note found with id {note_id}"})
    return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)


@mcp.tool()
async def list_recent_notes(limit: int = 20, workspace_id: str | None = None) -> str:
    """List the most recently updated notes."""
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
    """List the user's workspaces."""
    rows = await _get_pool().fetch("SELECT id, name, updated_at FROM workspaces ORDER BY updated_at DESC")
    return _rows_to_json(rows)


# ---------------------------------------------------------------------------
# WRITE TOOLS (Create & Update Notes, Workspaces, Files)
# ---------------------------------------------------------------------------
@mcp.tool()
async def create_note(
    title: str,
    content: str,
    workspace_id: str | None = None,
    workspace_name: str | None = "General",
    type: str = "text",
    color_hex: str | None = "#FFFFFF",
    x: float = 0.0,
    y: float = 0.0
) -> str:
    """Create a new note in the user's database. This will sync to their Android app instantly on next refresh.
    
    Args:
        title: Title of the note
        content: Main body content of the note
        workspace_id: Optional UUID of the workspace
        workspace_name: Name of the workspace (defaults to 'General')
        type: Note type (e.g., text, checklist)
        color_hex: Background color hex code
        x: Canvas X coordinate position
        y: Canvas Y coordinate position
    """
    pool = _get_pool()
    note_id = str(uuid.uuid4())
    ws_id = workspace_id or str(uuid.uuid4())
    
    row = await pool.fetchrow(
        """
        INSERT INTO notes (id, workspace_id, workspace_name, title, content, type, color_hex, x, y, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, (extract(epoch from now()) * 1000)::bigint)
        RETURNING id, workspace_id, workspace_name, title, content, type, color_hex, x, y, updated_at
        """,
        note_id, ws_id, workspace_name, title, content, type, color_hex, x, y
    )
    return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)


@mcp.tool()
async def update_note(
    note_id: str,
    title: str | None = None,
    content: str | None = None,
    color_hex: str | None = None
) -> str:
    """Update an existing note's title, content, or color by its ID. Automatically updates updated_at for sync.
    
    Args:
        note_id: The primary key ID of the note to update
        title: New title (optional)
        content: New content body (optional)
        color_hex: New background color hex code (optional)
    """
    pool = _get_pool()
    existing = await pool.fetchrow("SELECT * FROM notes WHERE id = $1", note_id)
    if not existing:
        return json.dumps({"error": f"No note found with id {note_id}"})
    
    new_title = title if title is not None else existing["title"]
    new_content = content if content is not None else existing["content"]
    new_color = color_hex if color_hex is not None else existing["color_hex"]

    row = await pool.fetchrow(
        """
        UPDATE notes 
        SET title = $1, content = $2, color_hex = $3, updated_at = (extract(epoch from now()) * 1000)::bigint
        WHERE id = $4
        RETURNING id, title, content, color_hex, updated_at
        """,
        new_title, new_content, new_color, note_id
    )
    return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)


@mcp.tool()
async def create_workspace(name: str) -> str:
    """Create a new workspace to group notes.
    
    Args:
        name: Name of the workspace
    """
    pool = _get_pool()
    ws_id = str(uuid.uuid4())
    row = await pool.fetchrow(
        """
        INSERT INTO workspaces (id, name, updated_at)
        VALUES ($1, $2, (extract(epoch from now()) * 1000)::bigint)
        RETURNING id, name, updated_at
        """,
        ws_id, name
    )
    return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)


@mcp.tool()
async def create_file_metadata(
    filename: str,
    file_type: str,
    topic: str,
    file_url: str,
    ocr_text: str | None = None
) -> str:
    """Store metadata and OCR text for a file or PDF in the user's database.
    
    Args:
        filename: Name of the file
        file_type: Type of file (e.g., pdf, image)
        topic: Topic description
        file_url: Storage link or URI
        ocr_text: Optional extracted text from OCR
    """
    pool = _get_pool()
    file_id = str(uuid.uuid4())
    try:
        row = await pool.fetchrow(
            """
            INSERT INTO file_metadata (id, filename, file_type, topic, file_url, ocr_text, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, (extract(epoch from now()) * 1000)::bigint)
            RETURNING id, filename, topic, created_at
            """,
            file_id, filename, file_type, topic, file_url, ocr_text
        )
        return json.dumps(_row_to_dict(row), ensure_ascii=False, indent=2)
    except asyncpg.exceptions.UndefinedTableError:
        return json.dumps({"available": False, "reason": "This account has no file_metadata table."})


# ---------------------------------------------------------------------------
# Unified search across available tables
# ---------------------------------------------------------------------------
@mcp.tool()
async def search_all(query: str, limit: int = 10) -> str:
    """Fuzzy-search notes, transcripts, and file OCR text all at once."""
    pool = _get_pool()
    notes = await _fetch_with_trgm_fallback(pool, _NOTES_TRGM_SQL, _NOTES_FALLBACK_SQL, query, limit, None)
    
    transcripts = await _fetch_optional_with_trgm_fallback(
        pool,
        """
        SELECT id, title, content, created_at, similarity(title || ' ' || content, $1) AS score
        FROM transcripts WHERE title % $1 OR content % $1 OR title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%'
        ORDER BY score DESC LIMIT $2
        """,
        """
        SELECT id, title, content, created_at FROM transcripts
        WHERE title ILIKE '%'||$1||'%' OR content ILIKE '%'||$1||'%'
        ORDER BY created_at DESC LIMIT $2
        """,
        query, limit,
    )
    
    files = await _fetch_optional_with_trgm_fallback(
        pool,
        """
        SELECT id, filename, topic, file_type, created_at, similarity(topic || ' ' || ocr_text, $1) AS score
        FROM file_metadata WHERE topic % $1 OR ocr_text % $1 OR topic ILIKE '%'||$1||'%' OR ocr_text ILIKE '%'||$1||'%'
        ORDER BY score DESC LIMIT $2
        """,
        """
        SELECT id, filename, topic, file_type, created_at FROM file_metadata
        WHERE topic ILIKE '%'||$1||'%' OR ocr_text ILIKE '%'||$1||'%'
        ORDER BY created_at DESC LIMIT $2
        """,
        query, limit,
    )

    result = {
        "notes": [_row_to_dict(r) for r in notes],
        "transcripts": [_row_to_dict(r) for r in transcripts] if transcripts is not None else None,
        "files": [_row_to_dict(r) for r in files] if files is not None else None,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# App Initialization & Middleware Setup
# ---------------------------------------------------------------------------
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

app.add_middleware(SessionMiddleware, secret_key=session_secret, same_site="lax", https_only=https_only)
app.add_middleware(BearerAuthMiddleware)
app.add_middleware(DatabaseInitMiddleware)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
