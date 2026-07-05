FROM python:3.12-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install dependencies using pip
RUN pip install --no-cache-dir .

# Install Playwright and chromium browser + system dependencies
RUN playwright install chromium --with-deps

# Copy the application code
COPY marketing_agent ./marketing_agent

EXPOSE 8000

# Start command
CMD ["uvicorn", "marketing_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
