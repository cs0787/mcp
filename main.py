import os
import logging
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastmcp import FastMCP
import asyncpg

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AndroidSecondBrain")

# Environment Variables
MCP_SECRET_KEY = os.getenv("MCP_SECRET_KEY")
NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")

# Initialize FastMCP Server
mcp = FastMCP("AndroidSecondBrain")

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
# MCP TOOLS DEFINITION
# ============================================================================

@mcp.tool()
async def search_text_notes(query: str) -> str:
    """Searches text notes in the Neon database matching a specific query string.

    Args:
        query: The search term to match against note content or title.
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            formatted_query = f"%{query}%"
            rows = await conn.fetch(
                """
                SELECT title, content 
                FROM notes 
                WHERE content ILIKE $1 OR title ILIKE $1
                ORDER BY created_at DESC 
                LIMIT 10
                """,
                formatted_query
            )
            if not rows:
                return f"No text notes found matching query: '{query}'."

            results = [f"Title: {row['title']}\nContent: {row['content']}" for row in rows]
            return "\n\n---\n\n".join(results)

    except Exception as e:
        logger.error(f"Error in search_text_notes tool: {e}")
        return f"Error executing search_text_notes query: {str(e)}"


@mcp.tool()
async def get_voice_transcripts(keyword: str) -> str:
    """Fetches text logs and transcripts of voice memos matching a keyword.

    Args:
        keyword: The keyword to search for within voice memo transcripts.
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            formatted_keyword = f"%{keyword}%"
            rows = await conn.fetch(
                """
                SELECT title, transcript, created_at 
                FROM transcripts 
                WHERE transcript ILIKE $1 OR title ILIKE $1
                ORDER BY created_at DESC 
                LIMIT 10
                """,
                formatted_keyword
            )
            if not rows:
                return f"No voice transcripts found matching keyword: '{keyword}'."

            results = [
                f"Title: {row['title']}\nTranscript: {row['transcript']}\nRecorded: {row['created_at']}"
                for row in rows
            ]
            return "\n\n---\n\n".join(results)

    except Exception as e:
        logger.error(f"Error in get_voice_transcripts tool: {e}")
        return f"Error executing get_voice_transcripts query: {str(e)}"


@mcp.tool()
async def extract_file_knowledge(topic: str) -> str:
    """Pulls OCR text or parsed contents from uploaded documents and images matching a topic.

    Args:
        topic: The topic or term to match against extracted file metadata and text.
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            formatted_topic = f"%{topic}%"
            rows = await conn.fetch(
                """
                SELECT file_name, file_type, extracted_text, created_at 
                FROM file_metadata 
                WHERE extracted_text ILIKE $1 OR file_name ILIKE $1
                ORDER BY created_at DESC 
                LIMIT 10
                """,
                formatted_topic
            )
            if not rows:
                return f"No parsed file knowledge found matching topic: '{topic}'."

            results = [
                f"File: {row['file_name']} ({row['file_type']})\nExtracted Text: {row['extracted_text']}"
                for row in rows
            ]
            return "\n\n---\n\n".join(results)

    except Exception as e:
        logger.error(f"Error in extract_file_knowledge tool: {e}")
        return f"Error executing extract_file_knowledge query: {str(e)}"


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
    # Allow health checks without authentication
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header."
        )

    token = auth_header.split(" ")[1]
    if token != MCP_SECRET_KEY:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden: Invalid MCP Secret Key."
        )

    return await call_next(request)


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


# Mount FastMCP Server via SSE transport
app.mount("/sse", mcp.sse_app())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)