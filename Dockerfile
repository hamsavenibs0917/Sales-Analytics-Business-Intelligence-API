# Multi-stage production container for Sales Analytics & BI REST API
FROM python:3.13-slim as builder

WORKDIR /app

# Install system build dependencies for psycopg2 and extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment in /opt/venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final production stage
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy isolated virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Copy application source code
COPY . .

# Create non-root user and grant full access to app and virtualenv
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app /opt/venv

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT:-5000}/health || exit 1

# Start Gunicorn binding dynamically to Render's $PORT (fallback to 5000)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} run:app --workers 2 --threads 4 --timeout 120"]
