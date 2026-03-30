# Scraprrr API Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY src/ ./src/
COPY mappings/ ./mappings/

# Create results directory
RUN mkdir -p /app/results

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the API server
CMD ["scraprrr-serve", "--host", "0.0.0.0", "--port", "8000", "--selenium-url", "http://selenium:4444/wd/hub"]
