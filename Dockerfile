# OmniAudit-GEO — Production Dockerfile for DigitalOcean & Containerized Environments
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Install curl for container health check
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root application user for container security
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -s /bin/bash appuser

WORKDIR /app

# Install Python dependencies first for optimal Docker layer caching
COPY omniaudit-geo/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application, documentation, skills, scripts, and marketplace manifest
COPY marketplace.json ./marketplace.json
COPY README.md ./README.md
COPY AGENTS.md ./AGENTS.md
COPY CLAUDE.md ./CLAUDE.md
COPY CONTRIBUTING.md ./CONTRIBUTING.md
COPY SECURITY.md ./SECURITY.md
COPY CODE_OF_CONDUCT.md ./CODE_OF_CONDUCT.md
COPY LICENSE ./LICENSE
COPY pyproject.toml ./pyproject.toml
COPY setup.py ./setup.py
COPY app.py ./app.py
COPY cli.py ./cli.py
COPY streamlit_app.py ./streamlit_app.py
COPY .streamlit/ ./.streamlit/
COPY docs/ ./docs/
COPY skills/ ./skills/
COPY scripts/ ./scripts/
COPY omniaudit-geo/ ./omniaudit-geo/

# Set ownership to non-root user
RUN chown -R appuser:appgroup /app

USER appuser

# Expose default port
EXPOSE 8000

# Healthcheck for container orchestration (DigitalOcean App Platform / Droplet / Kubernetes)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Start Uvicorn ASGI server with dynamic port support (DigitalOcean injects $PORT)
CMD ["sh", "-c", "python3 -m uvicorn main:app --app-dir omniaudit-geo --host 0.0.0.0 --port ${PORT}"]
