# Stage 1: Build stage
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_CACHE=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files and sync virtualenv
COPY pyproject.toml /app/
RUN uv sync --no-dev

# Copy project files
COPY . /app/

# Build Tailwind CSS (standalone mode) and collect static files
RUN uv run python manage.py tailwind build && \
    uv run python manage.py collectstatic --no-input

# Stage 2: Runtime stage
FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/appuser \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built environment and app code from builder
COPY --from=builder /app /app

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system --group --home /home/appuser appuser \
    && chown -R appuser:appgroup /app /home/appuser

USER appuser

EXPOSE 8000

CMD ["gunicorn", "-w", "3", "--bind", "0.0.0.0:8000", "stevillis_site.wsgi:application"]
