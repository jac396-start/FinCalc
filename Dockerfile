FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies with version-aware libicu handling
RUN set -eux; \
    . /etc/os-release; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        libpq-dev \
        curl \
        ca-certificates; \
    if [ "${VERSION_CODENAME:-}" = "trixie" ]; then \
        apt-get install -y --no-install-recommends libicu76 tzdata; \
    elif [ "${VERSION_CODENAME:-}" = "bookworm" ]; then \
        apt-get install -y --no-install-recommends libicu72 tzdata; \
    else \
        apt-get install -y --no-install-recommends tzdata; \
        apt-get install -y --no-install-recommends libicu || true; \
    fi; \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/static /app/templates /app/logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
