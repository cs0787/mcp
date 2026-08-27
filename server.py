"""
Notes & Codebase Architecture MCP Server (Multi-User Bidirectional Sync)
------------------------------------------------------------------------
Exposes tools for personal notes synchronization and codebase architectural memory:
- High-level architectural decision tracking without storing raw code files.
- Linear sequence chaining of code modifications (1 -> 2 -> 3).
- Hub-and-Spoke concept graphs and upstream/downstream ripple effect analysis.
- Instant project status and decision snapshotting for AI onboarding.
"""

import os
import json
import uuid
import time
import asyncpg
from typing import List, Optional

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
    "notes-codebase-mcp",
    instructions=(
        "Tools for personal notes sync and structured codebase architectural management. "
        "Use log_sequential_codebase_change to record plain-English summaries, rationale, and "
        "impact analysis of codebase changes in a linear timeline without passing raw code. "
        "Use create_or_connect_hub_concept to form conceptual topic graphs, and search_notes or "
        "get_codebase_context to inspect past architecture decisions."
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
        elif isinstance(v, uuid.UUID):
            d[k] = str(v)
    return d


def _rows_to_json(rows) -> str:
    return json.dumps([_row_to_dict(r) for r in rows], ensure_ascii=False, indent=2)


def _sanitize_summary(text: Optional[str]) -> str:
    if not text:
        return ""
    # Strip accidental markdown code blocks
    if "```" in text:
        lines = [l for l in text.splitlines() if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return text.strip()[:4000]


async def _ensure_codebase_tables(pool: asyncpg.Pool) -> None:
    """Auto-creates the project_nodes and project_edges tables on first use."""
    async with pool.acquire() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_nodes (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workspace VARCHAR(255) NOT NULL,
                node_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                summary TEXT NOT NULL,
                rationale TEXT,
                impact_analysis TEXT,
                sequence_index INT,
                previous_node_id UUID,
                central_hub_id UUID,
                affected_components TEXT[] DEFAULT '{}',
                status VARCHAR(50) DEFAULT 'completed',
                created_at TIMESTAMPTZ DEFAULT now(),
                updated_at BIGINT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS project_edges (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workspace VARCHAR(255) NOT NULL,
                source_node_id UUID REFERENCES project_nodes(id) ON DELETE CASCADE,
                target_node_id UUID REFERENCES project_nodes(id) ON DELETE CASCADE,
                relation_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_nodes_workspace_seq ON project_nodes(workspace, sequence_index);
            CREATE INDEX IF NOT EXISTS idx_edges_source_target ON project_edges(source_node_id, target_node_id);
            """
        )


async def _fetch_with_trgm_fallback(pool: asyncpg.Pool, trgm_sql: str, fallback_sql: str, *args):
    try:
        return await pool.fetch(trgm_sql, *args)
    except asyncpg.exceptions.UndefinedFunctionError:
        return await pool.fetch(fallback_sql, *args)


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
# NOTES READ TOOLS (Search & Get)
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
# NOTES WRITE TOOLS (Create & Update Notes, Workspaces, Files)
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
    """Create a new note in the user's database."""
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
    """Update an existing note's title, content, or color by its ID."""
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
    """Create a new workspace to group notes."""
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
    """Store metadata and OCR text for a file or PDF in the user's database."""
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
# CODEBASE MANAGEMENT & GRAPH STRUCTURING TOOLS
# ---------------------------------------------------------------------------
@mcp.tool()
async def log_sequential_codebase_change(
    workspace: str,
    title: str,
    what_changed: str,
    why: str,
    impact_on_project: str,
    affected_modules: List[str],
    status: str = "completed"
) -> str:
    """
    Logs a codebase change into an immutable chronological linear chain (1 -> 2 -> 3).
    Automatically links to the previous change in the repository.
    
    IMPORTANT: Never pass raw code syntax blocks. Summarize strictly in plain English:
    (1) What logic changed, (2) Why it was altered, and (3) Downstream project impact.
    """
    pool = _get_pool()
    await _ensure_codebase_tables(pool)

    cleaned_summary = _sanitize_summary(what_changed)
    cleaned_why = _sanitize_summary(why)
    cleaned_impact = _sanitize_summary(impact_on_project)
    now_epoch = int(time.time() * 1000)

    async with pool.acquire() as conn:
        async with conn.transaction():
            last_change = await conn.fetchrow(
                """
                SELECT id, sequence_index 
                FROM project_nodes 
                WHERE workspace = $1 AND node_type = 'codebase_change'
                ORDER BY sequence_index DESC NULLS LAST, created_at DESC 
                LIMIT 1;
                """,
                workspace
            )

            prev_id = last_change["id"] if last_change else None
            next_seq = (last_change["sequence_index"] + 1) if (last_change and last_change["sequence_index"]) else 1

            insert_query = """
                INSERT INTO project_nodes (
                    workspace, node_type, title, summary, rationale, impact_analysis,
                    sequence_index, previous_node_id, affected_components, status, updated_at
                ) VALUES ($1, 'codebase_change', $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id, sequence_index, title, created_at;
            """
            new_node = await conn.fetchrow(
                insert_query,
                workspace,
                title,
                cleaned_summary,
                cleaned_why,
                cleaned_impact,
                next_seq,
                prev_id,
                affected_modules,
                status,
                now_epoch
            )

            if prev_id:
                await conn.execute(
                    """
                    INSERT INTO project_edges (workspace, source_node_id, target_node_id, relation_type)
                    VALUES ($1, $2, $3, 'next_step');
                    """,
                    workspace,
                    prev_id,
                    new_node["id"]
                )

    result = {
        "status": "success",
        "step_number": new_node["sequence_index"],
        "node_id": str(new_node["id"]),
        "previous_step_id": str(prev_id) if prev_id else None,
        "title": new_node["title"],
        "logged_at": new_node["created_at"].isoformat()
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_linear_codebase_timeline(workspace: str, limit: int = 25) -> str:
    """
    Returns the ordered step-by-step linear change chain (Step 1 -> Step 2 -> Step 3).
    Allows AI agents to quickly understand the entire chronological evolution of a repository.
    """
    pool = _get_pool()
    await _ensure_codebase_tables(pool)

    query = """
        SELECT sequence_index, id, previous_node_id, title, summary, rationale,
               impact_analysis, affected_components, status, created_at
        FROM project_nodes
        WHERE workspace = $1 AND node_type = 'codebase_change'
        ORDER BY sequence_index ASC
        LIMIT $2;
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, workspace, limit)

    result = [
        {
            "step": r["sequence_index"],
            "id": str(r["id"]),
            "linked_from_step": str(r["previous_node_id"]) if r["previous_node_id"] else "ROOT (Initial State)",
            "title": r["title"],
            "what_changed": r["summary"],
            "why": r["rationale"],
            "project_impact": r["impact_analysis"],
            "affected_modules": r["affected_components"],
            "status": r["status"],
            "timestamp": r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        }
        for r in rows
    ]
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def create_or_connect_hub_concept(
    workspace: str,
    title: str,
    summary: str,
    is_central_hub: bool = False,
    central_hub_id: Optional[str] = None
) -> str:
    """
    Creates a central anchor hub node or connects radial spoke concept nodes to a central hub.
    Use this for high-level module architecture mapping and domain grouping.
    """
    pool = _get_pool()
    await _ensure_codebase_tables(pool)

    cleaned_summary = _sanitize_summary(summary)
    now_epoch = int(time.time() * 1000)
    node_type = "hub" if is_central_hub else "concept"
    hub_uuid = uuid.UUID(central_hub_id) if central_hub_id else None

    async with pool.acquire() as conn:
        async with conn.transaction():
            new_node = await conn.fetchrow(
                """
                INSERT INTO project_nodes (
                    workspace, node_type, title, summary, central_hub_id, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, title, node_type;
                """,
                workspace,
                node_type,
                title,
                cleaned_summary,
                hub_uuid,
                now_epoch
            )

            if hub_uuid and not is_central_hub:
                await conn.execute(
                    """
                    INSERT INTO project_edges (workspace, source_node_id, target_node_id, relation_type)
                    VALUES ($1, $2, $3, 'belongs_to_hub');
                    """,
                    workspace,
                    hub_uuid,
                    new_node["id"]
                )

    result = {
        "status": "success",
        "node_id": str(new_node["id"]),
        "title": new_node["title"],
        "node_type": new_node["node_type"],
        "connected_hub_id": central_hub_id
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_impact_graph(workspace: str, target_module_or_component: str) -> str:
    """
    Traces upstream decisions and downstream ripple effects for a given module or component.
    """
    pool = _get_pool()
    await _ensure_codebase_tables(pool)

    query = """
        SELECT id, sequence_index, title, summary, rationale, impact_analysis, affected_components, created_at
        FROM project_nodes
        WHERE workspace = $1 
          AND (title ILIKE '%' || $2 || '%' OR $2 = ANY(affected_components))
        ORDER BY created_at DESC
        LIMIT 20;
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, workspace, target_module_or_component)

    direct_changes = []
    indirect_effects = []

    for r in rows:
        item = {
            "step": r["sequence_index"],
            "id": str(r["id"]),
            "title": r["title"],
            "summary": r["summary"],
            "impact": r["impact_analysis"]
        }
        if target_module_or_component.lower() in r["title"].lower():
            direct_changes.append(item)
        else:
            indirect_effects.append(item)

    result = {
        "workspace": workspace,
        "target": target_module_or_component,
        "direct_module_decisions": direct_changes,
        "upstream_downstream_ripple_effects": indirect_effects
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_project_progress_snapshot(workspace: str) -> str:
    """
    Returns an instant executive snapshot of project progress, active steps, and recent architectural rationales.
    """
    pool = _get_pool()
    await _ensure_codebase_tables(pool)

    status_query = """
        SELECT status, COUNT(*) as count
        FROM project_nodes
        WHERE workspace = $1
        GROUP BY status;
    """

    recent_query = """
        SELECT sequence_index, title, summary, rationale, impact_analysis, status, created_at
        FROM project_nodes
        WHERE workspace = $1
        ORDER BY created_at DESC
        LIMIT 6;
    """

    async with pool.acquire() as conn:
        counts = await conn.fetch(status_query, workspace)
        recents = await conn.fetch(recent_query, workspace)

    result = {
        "workspace": workspace,
        "status_distribution": {r["status"]: r["count"] for r in counts},
        "latest_architecture_decisions": [
            {
                "step": r["sequence_index"],
                "title": r["title"],
                "summary": r["summary"],
                "why": r["rationale"],
                "impact": r["impact_analysis"],
                "status": r["status"],
                "timestamp": r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            }
            for r in recents
        ]
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
