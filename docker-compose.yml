# Base image
FROM python:3.10-slim

# ---- ADD THIS BLOCK (replaces the fixed install) ----
# Installs correct dependencies (libicu, tzdata) based on Debian version (bookworm/trixie)
RUN set -eux; \
    . /etc/os-release; \
    if [ "${VERSION_CODENAME:-}" = "trixie" ]; then \
        apt-get update && apt-get install -y --no-install-recommends ca-certificates libicu76 tzdata; \
    elif [ "${VERSION_CODENAME:-}" = "bookworm" ]; then \
        apt-get update && apt-get install -y --no-install-recommends ca-certificates libicu72 tzdata; \
    else \
        apt-get update && apt-get install -y --no-install-recommends ca-certificates tzdata; \
        # Try a generic 'libicu' if available; otherwise prompt for correct libicuXX
        apt-get install -y --no-install-recommends libicu || \
        (echo "Please install the correct libicuXX for ${VERSION_CODENAME}" && exit 1); \
    fi; \
    rm -rf /var/lib/apt/lists/*
# ---- END BLOCK ----

# Install .NET SDK (Required for F# Engine)
# Note: We explicitly install wget here since the block above cleaned up apt lists
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    wget https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y dotnet-sdk-6.0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Build F# Calculation Engine
COPY calculations/ /app/calculations/
WORKDIR /app/calculations
RUN dotnet build -c Release -o bin/Release/net6.0

# 2. Setup Python App
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
COPY . .

# Environment variable for F# binary path
ENV FSHARP_EXEC_PATH="/app/calculations/bin/Release/net6.0/FinanceCore"
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
