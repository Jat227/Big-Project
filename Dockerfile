# ---- Builder stage ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Runtime stage ----
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Run FastAPI with uvicorn, using the PORT environment variable provided by the host (Render)
CMD uvicorn backend_server:app --host 0.0.0.0 --port ${PORT:-5001}
