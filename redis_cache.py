"""
Redis cache helper.
- In production (Docker): connects to real Redis
- In local dev without Redis: auto-falls back to fakeredis (in-memory, same API)
"""
import json
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", 2700))  # 45 minutes

_redis_client = None

async def get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    # Try real Redis first
    try:
        import redis.asyncio as aioredis
        client = await aioredis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1)
        await client.ping()
        print("✅ Connected to real Redis")
        _redis_client = client
    except Exception:
        # Fallback to fakeredis (in-memory, no server required)
        print("⚠️  Real Redis unavailable — using fakeredis (in-memory cache)")
        import fakeredis.aioredis as fakeredis
        _redis_client = fakeredis.FakeRedis(decode_responses=True)

    return _redis_client

def _cache_key(query: str) -> str:
    h = hashlib.md5(query.strip().lower().encode()).hexdigest()
    return f"search:{h}"

async def get_cached(query: str):
    """Return cached results, or None on miss."""
    try:
        r = await get_redis()
        data = await r.get(_cache_key(query))
        if data:
            return json.loads(data)
    except Exception as e:
        print(f"[Cache] get error: {e}")
    return None

async def set_cache(query: str, data: list, ttl: int = CACHE_TTL):
    """Store results with TTL."""
    try:
        r = await get_redis()
        await r.setex(_cache_key(query), ttl, json.dumps(data))
    except Exception as e:
        print(f"[Cache] set error: {e}")

async def invalidate(query: str):
    """Remove a query from cache."""
    try:
        r = await get_redis()
        await r.delete(_cache_key(query))
    except Exception as e:
        print(f"[Cache] invalidate error: {e}")
