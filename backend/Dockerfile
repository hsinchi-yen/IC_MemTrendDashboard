FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required by asyncpg / psycopg build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer cache-friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

EXPOSE 3000

# Docker liveness probe – uses stdlib only, no extra deps
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
