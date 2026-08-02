import os
import logging
from typing import Optional
import asyncpg
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from fastmcp import FastMCP

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


# Health check endpoint for root path
async def homepage(request):
    return JSONResponse({"status": "healthy", "service": "AndroidSecondBrain MCP Server"})


if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 10000))
    
    # Run FastMCP directly on 0.0.0.0
    mcp.run(transport="sse", port=server_port, host="0.0.0.0")
