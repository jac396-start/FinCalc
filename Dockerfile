# Base image
FROM python:3.10-slim

# 1. Install System Dependencies & .NET SDK (for F#)
RUN apt-get update && \
    apt-get install -y wget && \
    wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    rm packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install -y dotnet-sdk-6.0 && \
    apt-get clean

WORKDIR /app

# 2. Build F# Calculation Engine
# Copy the calculations folder first
COPY calculations/ /app/calculations/
WORKDIR /app/calculations
# Compile to Release binary
RUN dotnet build -c Release -o bin/Release/net6.0

# 3. Setup Python Environment
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Application Code
COPY . .

# 5. Set Environment Variables
# Point to the compiled F# binary
ENV FSHARP_EXEC_PATH="/app/calculations/bin/Release/net6.0/FinanceCore"
ENV PYTHONUNBUFFERED=1

# 6. Run Application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
