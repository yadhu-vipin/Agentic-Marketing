FROM python:3.12-slim

WORKDIR /app

# System dependencies for Playwright Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies before copying source (layer cache)
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[prod]"

# Install Playwright browser binaries
RUN playwright install chromium --with-deps

# Copy source
COPY marketing_agent/ ./marketing_agent/

ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "marketing_agent.api.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
