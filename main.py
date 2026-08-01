import os
import logging
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg

# Import official low-level MCP SDK tools instead of FastMCP
from mcp.server.fastapi import FastApiServer
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AndroidSecondBrain")

# Environment Variables
MCP_SECRET_KEY = os.getenv("MCP_SECRET_KEY")
NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")

# Initialize the real, standard MCP Server instance
mcp_server = Server("AndroidSecondBrain")

# Database Connection Pool Global Variable
db_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Initializes and returns an asyncpg pool connected to the Neon PostgreSQL database."""
    global db_pool
    if db_pool is None:
        if not NEON_DATABASE_URL:
            raise ValueError("NEON_DATABASE_URL environment variable is not configured.")
        try:
            db_pool = await asyncpg.create_pool(
                dsn=NEON_DATABASE_URL,
                min_size=1,
                max_size=10,
                timeout=10.0
            )
            logger.info("Successfully established connection pool to Neon PostgreSQL.")
        except Exception as e:
            logger.error(f"Failed to connect to Neon PostgreSQL: {e}")
            raise
    return db_pool


# ============================================================================
# MCP TOOLS DEFINITION (Standard low-level schema registry)
# ============================================================================

@mcp_server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Exposes and explains your tools clearly to ChatGPT/Claude mobile clients."""
    return [
        Tool(
            name="search_text_notes",
            description="Searches text notes in the Neon database matching a specific query string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search term to match against note content or title."}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_voice_transcripts",
            description="Fetches text logs and transcripts of voice memos matching a keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "The keyword to search for within voice memo transcripts."}
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="extract_file_knowledge",
            description="Pulls OCR text or parsed contents from uploaded documents and images matching a topic.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The topic or term to match against extracted file metadata and text."}
                },
                "required": ["topic"]
            }
        )
    ]


@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Router function that gets invoked whenever an external AI calls a tool."""
    try:
        pool = await get_db_pool()
        
        # 1. Handle Text Notes Search
        if name == "search_text_notes":
            query = arguments.get("query", "")
            formatted_query = f"%{query}%"
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT title, content FROM notes WHERE content ILIKE $1 OR title ILIKE $1 ORDER BY created_at DESC LIMIT 10",
                    formatted_query
                )
                if not rows:
                    return [TextContent(type="text", text=f"No text notes found matching query: '{query}'.")]
                results = [f"Title: {row['title']}\nContent: {row['content']}" for row in rows]
                return [TextContent(type="text", text="\n\n---\n\n".join(results))]

        # 2. Handle Voice Memos Transcripts Search
        elif name == "get_voice_transcripts":
            keyword = arguments.get("keyword", "")
            formatted_keyword = f"%{keyword}%"
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT title, transcript, created_at FROM transcripts WHERE transcript ILIKE $1 OR title ILIKE $1 ORDER BY created_at DESC LIMIT 10",
                    formatted_keyword
                )
                if not rows:
                    return [TextContent(type="text", text=f"No voice transcripts found matching keyword: '{keyword}'.")]
                results = [f"Title: {row['title']}\nTranscript: {row['transcript']}\nRecorded: {row['created_at']}" for row in rows]
                return [TextContent(type="text", text="\n\n---\n\n".join(results))]

        # 3. Handle PDF and Image File Context Search
        elif name == "extract_file_knowledge":
            topic = arguments.get("topic", "")
            formatted_topic = f"%{topic}%"
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT file_name, file_type, extracted_text FROM file_metadata WHERE extracted_text ILIKE $1 OR file_name ILIKE $1 ORDER BY created_at DESC LIMIT 10",
                    formatted_topic
                )
                if not rows:
                    return [TextContent(type="text", text=f"No parsed file knowledge found matching topic: '{topic}'.")]
                results = [f"File: {row['file_name']} ({row['file_type']})\nExtracted Text: {row['extracted_text']}" for row in rows]
                return [TextContent(type="text", text="\n\n---\n\n".join(results))]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(type="text", text=f"Internal database query handling exception: {str(e)}")]

    return [TextContent(type="text", text="Error: Requested tool function target was not found.")]


# ============================================================================
# FASTAPI APPLICATION & SECURITY MIDDLEWARE
# ============================================================================

app = FastAPI(
    title="Android Second Brain MCP Server",
    description="MCP Server providing mobile AI assistants access to cloud-stored Second Brain data",
    version="1.0.0"
)

security = HTTPBearer()


async def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validates the incoming Bearer token against the configured MCP_SECRET_KEY."""
    if not MCP_SECRET_KEY:
        logger.warning("MCP_SECRET_KEY is not set. All incoming requests will be rejected.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server security configuration error."
        )
    if credentials.credentials != MCP_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid Bearer Token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.middleware("http")
async def enforce_mcp_authentication(request: Request, call_next):
    """Enforces authentication check for all SSE and MCP endpoints."""
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # Return standard response object instead of bare exception inside middleware
        return json_error_response(status.HTTP_401_UNAUTHORIZED, "Missing or invalid Authorization header.")

    token = auth_header.split(" ")[1]
    if token != MCP_SECRET_KEY:
        return json_error_response(status.HTTP_401_UNAUTHORIZED, "Forbidden: Invalid MCP Secret Key.")

    return await call_next(request)


def json_error_response(status_code: int, msg: str):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=status_code, content={"detail": msg})


@app.on_event("startup")
async def on_startup():
    logger.info("Initializing database pool during server startup...")
    if NEON_DATABASE_URL:
        await get_db_pool()


@app.on_event("shutdown")
async def on_shutdown():
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("Database connection pool closed.")


@app.get("/health")
async def health_check():
    """Health check endpoint for cloud monitoring."""
    return {"status": "healthy", "service": "AndroidSecondBrain"}


# Connect the standard mcp server instance safely into standard FastAPI endpoints
mcp_api_server = FastApiServer(mcp_server)

@app.post("/sse")
async def handle_sse_endpoint():
    """Handles the streaming initialization connection from mobile apps securely"""
    return await mcp_api_server.handle_sse()


if __name__ == "__main__":
    import uvicorn
    # Render binds dynamically using the $PORT environment variable, default to 10000 on Render
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
