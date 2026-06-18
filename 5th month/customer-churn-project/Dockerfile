# ──────────────────────────────────────────────────────────────────────
# Dockerfile — Customer Churn Prediction Service
# Multi-stage build: keeps the final image lean by discarding build
# tooling (compilers, headers) that's only needed to install wheels.
# ──────────────────────────────────────────────────────────────────────

# ---- Stage 1: builder ---------------------------------------------------
FROM python:3.10-slim AS builder

WORKDIR /build

# System deps needed only to compile certain Python wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Stage 2: runtime ----------------------------------------------------
FROM python:3.10-slim AS runtime

LABEL maintainer="data-science-team"
LABEL description="Customer Churn Prediction API — production inference service"

# Create non-root user (security best practice)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/

# Create writable directories for logs/reports at runtime
RUN mkdir -p logs reports && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Container-level health check — restarts the container if the API
# stops responding, which orchestrators (Swarm/K8s) watch for.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
