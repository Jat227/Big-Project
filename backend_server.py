"""
FastAPI backend — production-grade, async, rate-limited.
Replaces Flask backend_server.py.

Run with:
    ./venv/bin/uvicorn backend_server:app --host 0.0.0.0 --port 5001 --reload
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv()

# ── Rate limiter (25 searches/min per IP) ────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["25/minute"])

# ── App lifespan (startup / shutdown hooks) ───────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 PriceFinder API starting up...")
    yield
    print("🛑 PriceFinder API shutting down...")

app = FastAPI(
    title="PriceFinder API",
    description="Hybrid price comparison engine for the Indian market",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── Rate limit error handler ──────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Import after app init to avoid circular deps ──────────────────────────────
from redis_cache import get_cached, set_cache
from tasks import scrape_and_cache
import asyncio

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}


# ── Main search endpoint ──────────────────────────────────────────────────────
@app.get("/api/search")
@limiter.limit("25/minute")
async def search_products(request: Request, q: str = ""):
    query = q.strip().lower()
    if not query:
        return JSONResponse(content=[], status_code=200)

    # 1. Check Redis cache first — return instantly if hit
    cached = await get_cached(query)
    if cached is not None:
        print(f"✅ Redis HIT  for '{query}'  ({len(cached)} products)")
        return JSONResponse(content=cached)

    print(f"❌ Redis MISS for '{query}' — dispatching Celery task...")

    # 2. Dispatch Celery task to scrape in background, but also
    #    run scraper inline for the first request so user gets data.
    loop = asyncio.get_event_loop()
    from scraper import scrape_all

    products = await loop.run_in_executor(None, scrape_all, query)

    # 3. Store in Redis for future requests
    await set_cache(query, products)

    # 4. Also kick off a Celery task to keep cache warm in background
    try:
        scrape_and_cache.apply_async(args=[query], countdown=2500)
    except Exception:
        pass  # Celery broker not running in local dev — that's fine

    print(f"🔄 Scraped and cached {len(products)} products for '{query}'")
    return JSONResponse(content=products)


# ── Task status endpoint (for future polling support) ─────────────────────────
@app.get("/api/task/{task_id}")
async def task_status(task_id: str):
    from celery_app import celery_app
    result = celery_app.AsyncResult(task_id)
    return {"task_id": task_id, "status": result.status, "result": result.result}

# ── Serve Frontend ────────────────────────────────────────────────────────────
# Mount current directory to serve CSS/JS/Images
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/", methods=["GET", "HEAD"])
async def read_index():
    return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    # Use environment variables for Port (important for Render) or fallback to 5001
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
