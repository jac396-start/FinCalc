# ---------- Stage 1: Build & publish F# engine with .NET 10 (LTS)
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS fs-build
WORKDIR /src

# Copy only the F# engine project to leverage Docker cache effectively
COPY calculations/ ./calculations/

# Restore & publish self-contained for Linux x64
RUN dotnet restore ./calculations \
 && dotnet publish ./calculations -c Release \
      -r linux-x64 \
      --self-contained true \
      /p:PublishSingleFile=true

# ---------- Stage 2: FastAPI app (Python) + engine artifacts
FROM python:3.10-slim

# Avoid interactive debconf prompts in CI
ENV DEBIAN_FRONTEND=noninteractive

# If the engine uses globalization (dates, sorting, cultures), keep ICU & tzdata.
# If you set InvariantGlobalization=true in the F# project, you can remove these to shrink the image.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates libicu tzdata \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the published engine from the SDK stage
COPY --from=fs-build /src/calculations/bin/Release/net10.0/linux-x64/publish/ /app/engine/

# Path to the engine binary (adjust name if your output differs)
ENV FSHARP_EXEC_PATH=/app/engine/FinanceCore

# Copy the rest of the FastAPI app
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

