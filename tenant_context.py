"""
Per-request tenant context.

BearerAuthMiddleware resolves *which user's* Neon connection string a
request should use, then sets these contextvars before calling into the
rest of the app. Tool functions in server.py read them back out.

Why contextvars instead of threading state through FastMCP's Context /
lifespan_context: FastMCP's lifespan context is created once at process
startup and is meant for things shared across ALL requests (a single DB
pool, in the old single-user version). We now need something that varies
per-request (per-user), which is exactly what contextvars are for -- they
propagate down through awaited calls within the same request's task,
without needing to know anything about FastMCP's internal call graph.
"""

import contextvars

# The authenticated user's id (str(uuid)) for the current request.
current_user_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_user_id", default=None
)

# The asyncpg.Pool connected to *that user's* personal Neon database
# (the one holding their notes/workspaces tables), for the current request.
current_pool: contextvars.ContextVar = contextvars.ContextVar(
    "current_pool", default=None
)
