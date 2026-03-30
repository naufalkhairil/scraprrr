# Scraprrr API Quickstart Guide

Get up and running with the Scraprrr REST API in minutes.

## Prerequisites

- Python 3.9+
- Docker and Docker Compose (for Selenium Grid)
- Virtual environment activated

## Quick Start (5 minutes)

### Step 1: Start Selenium Grid

```bash
# Using Docker Compose
docker-compose -f docker/selenium-grid/docker-compose.yml up -d

# Verify it's running
docker ps | grep selenium
```

You should see the Selenium container running.

### Step 2: Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install with API dependencies
pip install -e ".[dev]"
```

### Step 3: Start the API Server

```bash
# Start with default settings (port 8000)
scraprrr-serve

# Or start with auto-reload for development
scraprrr-serve --reload
```

The server will start at `http://localhost:8000`

### Step 4: Verify Installation

Open your browser and visit:
- **API Root**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Interactive Docs**: http://localhost:8000/docs

You should see:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "selenium_connected": true
}
```

---

## Making Your First API Calls

### Option 1: Using the Interactive Docs (Easiest)

1. Go to http://localhost:8000/docs
2. Click on `POST /api/v1/flights/search`
3. Click "Try it out"
4. Enter:
   ```json
   {
     "origin": "CGK",
     "destination": "DPS"
   }
   ```
5. Click "Execute"
6. Wait 30-60 seconds for results

### Option 2: Using cURL

```bash
# Search for flights
curl -X POST http://localhost:8000/api/v1/flights/search \
  -H "Content-Type: application/json" \
  -d '{"origin":"CGK","destination":"DPS"}'

# Search for hotels
curl -X POST http://localhost:8000/api/v1/hotels/search \
  -H "Content-Type: application/json" \
  -d '{"location":"Jakarta"}'
```

### Option 3: Using Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Search flights
response = requests.post(
    f"{BASE_URL}/flights/search",
    json={"origin": "CGK", "destination": "DPS"}
)
flights = response.json()
print(f"Found {flights['total_results']} flights")

# Search hotels
response = requests.post(
    f"{BASE_URL}/hotels/search",
    json={"location": "Jakarta"}
)
hotels = response.json()
print(f"Found {hotels['total_results']} hotels")
```

---

## Using Async Endpoints (Recommended for Production)

Synchronous searches block for 30-60 seconds. For better performance, use async endpoints:

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# Start async job
response = requests.post(
    f"{BASE_URL}/flights/search/async",
    json={"origin": "CGK", "destination": "DPS"}
)
job = response.json()
job_id = job["job_id"]
print(f"Job started: {job_id}")

# Poll for results
while True:
    response = requests.get(f"{BASE_URL}/flights/job/{job_id}")
    job = response.json()
    
    if job["status"] == "completed":
        print(f"Found {job['result']['total_results']} flights")
        break
    elif job["status"] == "failed":
        print(f"Job failed: {job['error']}")
        break
    
    time.sleep(2)  # Wait 2 seconds before polling again
```

---

## Running with Docker Compose (All-in-One)

For a complete setup with API and Selenium in containers:

```bash
# Start both API and Selenium
docker-compose -f docker/api/docker-compose.yml up -d

# Check logs
docker-compose -f docker/api/docker-compose.yml logs -f api

# Stop everything
docker-compose -f docker/api/docker-compose.yml down
```

The API will be available at http://localhost:8000

---

## Common Commands

### Server Management

```bash
# Start server on custom port
scraprrr-serve --port 8080

# Start with debug logging
scraprrr-serve --log-level debug

# Start with multiple workers (production)
scraprrr-serve --workers 4
```

### Job Management

```bash
# List all jobs
curl http://localhost:8000/api/v1/jobs

# Get job statistics
curl http://localhost:8000/api/v1/jobs/stats

# Cancel a running job
curl -X DELETE http://localhost:8000/api/v1/jobs/{job_id}

# Cleanup old jobs
curl -X POST "http://localhost:8000/api/v1/jobs/cleanup?max_age_seconds=3600"
```

---

## Troubleshooting

### Selenium Not Connected

**Problem:** Health check shows `"selenium_connected": false`

**Solution:**
```bash
# Check if Selenium container is running
docker ps | grep selenium

# Restart Selenium
docker-compose -f docker/selenium-grid/docker-compose.yml restart

# Check Selenium logs
docker-compose -f docker/selenium-grid/docker-compose.yml logs selenium
```

### Port Already in Use

**Problem:** `Address already in use` error

**Solution:**
```bash
# Use a different port
scraprrr-serve --port 8080

# Or kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -e ".[dev]"
```

### Job Fails Immediately

**Problem:** Job status changes to "failed" immediately

**Solution:**
1. Check server logs for detailed error messages
2. Verify Selenium is running: http://localhost:4444
3. Use valid airport codes (e.g., CGK, DPS, SIN)
4. Ensure origin and destination are different

---

## Next Steps

- **Full Documentation**: See [API.md](API.md) for complete API reference
- **Example Code**: Check [examples/api_usage.py](examples/api_usage.py) for more examples
- **Interactive Docs**: Explore all endpoints at http://localhost:8000/docs

---

## Support

- **Issues**: https://github.com/yourusername/scraprrr/issues
- **Documentation**: https://github.com/yourusername/scraprrr/tree/main/API.md
