# PriceFinder 🏷️

A production-grade hybrid price comparison engine for the Indian market.  
Compares prices across Amazon, Flipkart, Myntra, Nykaa, Blinkit, BigBasket and more.

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn (async, 4 workers) |
| Cache | Redis (45-min TTL, LRU eviction) |
| Database | PostgreSQL 15 (async SQLAlchemy) |
| Background Jobs | Celery + Redis broker |
| Rate Limiting | slowapi (25 req/min per IP) |
| Frontend | HTML/CSS/JS (Vanilla) |
| Container | Docker + Docker Compose |

---

## Quick Start (Docker — Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed

### Run everything with one command
```bash
git clone <your-repo-url>
cd Project
cp .env.example .env       # Edit .env if needed

docker-compose up --build  # Starts postgres + redis + web + celery + flower
```

| Service | URL |
|---|---|
| Frontend | http://localhost:8080 |
| API | http://localhost:5001 |
| API Docs | http://localhost:5001/docs |
| Celery Dashboard | http://localhost:5555 |

---

## Local Development (Without Docker)

```bash
# Create and activate virtualenv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Redis locally (requires Redis installed)
redis-server &

# Start FastAPI
uvicorn backend_server:app --host 0.0.0.0 --port 5001 --reload

# Start Celery worker (separate terminal)
celery -A celery_app worker --loglevel=info

# Start frontend
python3 -m http.server 8080
```

---

## Deployment (Cloud)

### Option 1: Railway (Free Tier)
1. Push to GitHub
2. Connect repo at [railway.app](https://railway.app)
3. Add PostgreSQL + Redis plugins
4. Set environment variables from `.env.example`

### Option 2: AWS / GCP / Render
- Use the provided `Dockerfile` and `docker-compose.yml`
- Point `DATABASE_URL` and `REDIS_URL` to your managed services

---

## Cloudflare Setup (After Deployment)

1. Buy a domain (e.g. pricefinder.in on GoDaddy)
2. Sign up at [cloudflare.com](https://cloudflare.com) (free tier)
3. Add your site → change nameservers to Cloudflare's
4. Enable: **WAF → Rate Limiting** → 30 req / 10 sec per IP → Block
5. Enable: **Caching** → Cache Level: Standard
6. Enable: **DDoS Protection** → Auto

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | SQLite (local fallback) |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `CACHE_TTL_SECONDS` | Cache duration in seconds | `2700` (45 min) |
| `ENVIRONMENT` | `development` or `production` | `development` |

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/search?q=iphone` | Search products |
| `GET /health` | Health check |
| `GET /api/task/{id}` | Celery task status |
| `GET /docs` | Interactive API docs (Swagger) |

---

## How to Earn

- Apply for **Amazon Affiliate** → [affiliate-program.amazon.in](https://affiliate-program.amazon.in)
- Apply for **Flipkart Affiliate** → [affiliate.flipkart.com](https://affiliate.flipkart.com)
- Add **Google AdSense** to `index.html`
- Commission rates: 1–15% per sale depending on category
