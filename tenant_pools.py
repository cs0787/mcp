"""
One asyncpg pool per USER, not one global pool for the whole server.

Each user has their own Neon connection string (their personal notes DB).
Pools are created lazily on first request and cached by user id. This
keeps things simple on Render's free tier: at most MAX_POOLS small pools
open at once, oldest-idle evicted first.
"""

import asyncio
import time
import asyncpg


class TenantPoolManager:
    def __init__(self, max_pools: int = 50, pool_min_size: int = 1, pool_max_size: int = 3):
        self._pools: dict[str, asyncpg.Pool] = {}
        self._last_used: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._max_pools = max_pools
        self._pool_min_size = pool_min_size
        self._pool_max_size = pool_max_size

    async def get_pool(self, user_id: str, connection_string: str) -> asyncpg.Pool:
        self._last_used[user_id] = time.time()

        existing = self._pools.get(user_id)
        if existing is not None:
            return existing

        lock = self._locks.setdefault(user_id, asyncio.Lock())
        async with lock:
            # Re-check after acquiring the lock in case another request for
            # the same user already created the pool while we were waiting.
            existing = self._pools.get(user_id)
            if existing is not None:
                return existing

            if len(self._pools) >= self._max_pools:
                await self._evict_oldest()

            pool = await asyncpg.create_pool(
                connection_string,
                min_size=self._pool_min_size,
                max_size=self._pool_max_size,
                ssl="require",
            )
            await self._try_enable_trgm(pool)
            self._pools[user_id] = pool
            return pool

    async def invalidate(self, user_id: str) -> None:
        """Call this when a user updates their connection string, so the
        next request reconnects with the new one instead of reusing a pool
        built from the old (possibly now-wrong) credentials."""
        pool = self._pools.pop(user_id, None)
        self._last_used.pop(user_id, None)
        if pool is not None:
            await pool.close()

    async def close_all(self) -> None:
        for pool in list(self._pools.values()):
            await pool.close()
        self._pools.clear()
        self._last_used.clear()

    async def _evict_oldest(self) -> None:
        if not self._pools:
            return
        oldest_user_id = min(self._last_used, key=self._last_used.get)
        pool = self._pools.pop(oldest_user_id, None)
        self._last_used.pop(oldest_user_id, None)
        if pool is not None:
            await pool.close()

    @staticmethod
    async def _try_enable_trgm(pool: asyncpg.Pool) -> None:
        """Best-effort: enables fuzzy-search support in the user's DB. If the
        role Neon gave them can't create extensions, fuzzy search just falls
        back to plain ILIKE (handled at query time in server.py) instead of
        failing the whole connection."""
        try:
            async with pool.acquire() as conn:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        except Exception:
            pass


async def test_connection_string(connection_string: str) -> tuple[bool, str]:
    """Used by the dashboard to validate a connection string before saving it."""
    try:
        conn = await asyncpg.connect(connection_string, timeout=8, ssl="require")
        try:
            await conn.execute("SELECT 1")
        finally:
            await conn.close()
        return True, ""
    except Exception as e:
        return False, str(e)


_manager = TenantPoolManager()


def get_manager() -> TenantPoolManager:
    return _manager
