"""
Celery background tasks for PriceFinder.
Workers run scraping jobs so web requests return instantly.
"""
import asyncio
import json
from celery_app import celery_app
from scraper import scrape_all

# Use a simple sync Redis client for Celery tasks (not async)
import redis as sync_redis
import hashlib
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL  = int(os.getenv("CACHE_TTL_SECONDS", 2700))  # 45 min

def _cache_key(query: str) -> str:
    h = hashlib.md5(query.strip().lower().encode()).hexdigest()
    return f"search:{h}"

@celery_app.task(bind=True, max_retries=3)
def scrape_and_cache(self, query: str):
    """Scrape all platforms for `query` and store results in Redis."""
    try:
        # scrape_all is sync (requests-based); run directly
        products = scrape_all(query)

        r = sync_redis.from_url(REDIS_URL, decode_responses=True)
        r.setex(_cache_key(query), CACHE_TTL, json.dumps(products))
        print(f"[Celery] Cached {len(products)} products for '{query}'")
        return {"status": "ok", "count": len(products)}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
