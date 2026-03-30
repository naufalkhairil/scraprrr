# Scraprrr API Documentation

REST API for Traveloka flight and hotel scraping powered by FastAPI.

## Quick Start

### 1. Start Selenium Grid

```bash
docker-compose -f docker/selenium-grid/docker-compose.yml up -d
```

### 2. Start the API Server

```bash
# Install dependencies (if not already done)
pip install -e ".[dev]"

# Start the server
scraprrr-serve

# Or with custom options
scraprrr-serve --host 0.0.0.0 --port 8080 --reload
```

### 3. Access the API

- **API Root**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Base URL

```
http://localhost:8000/api/v1
```

---

## Flight Endpoints

### Search Flights (Synchronous)

**POST** `/flights/search`

Search for flights between origin and destination. Blocks until search completes (30-60 seconds).

**Request Body:**
```json
{
  "origin": "CGK",
  "destination": "DPS",
  "origin_name": "Jakarta",
  "destination_name": "Bali",
  "save_results": true
}
```

**Response:** `FlightSearchResult`
```json
{
  "origin": {"code": "CGK", "name": "Jakarta"},
  "destination": {"code": "DPS", "name": "Bali"},
  "search_timestamp": "2026-03-30T10:00:00",
  "status": "success",
  "total_results": 50,
  "tickets": [
    {
      "airline_name": "Garuda Indonesia",
      "departure_time": "08:00",
      "departure_airport": "CGK",
      "arrival_time": "10:30",
      "arrival_airport": "DPS",
      "duration": "2h 30m",
      "flight_type": "Direct",
      "price": "Rp 1.500.000",
      "baggage": "20 kg",
      "promos": [],
      "extracted_at": "2026-03-30T10:00:00"
    }
  ]
}
```

---

### Search Flights (Asynchronous)

**POST** `/flights/search/async`

Start an asynchronous flight search. Returns immediately with a job ID.

**Request Body:**
```json
{
  "origin": "CGK",
  "destination": "DPS",
  "save_results": true
}
```

**Response:** `JobStatusResponse`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_type": "flight_search",
  "status": "pending",
  "params": {"origin": "CGK", "destination": "DPS"},
  "created_at": "2026-03-30T10:00:00",
  "progress": 0
}
```

---

### Get Flight Job Status

**GET** `/flights/job/{job_id}`

Get the status and results of a flight search job.

**Response:** `JobStatusResponse`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_type": "flight_search",
  "status": "completed",
  "params": {"origin": "CGK", "destination": "DPS"},
  "created_at": "2026-03-30T10:00:00",
  "started_at": "2026-03-30T10:00:01",
  "completed_at": "2026-03-30T10:01:00",
  "result": {
    "origin": {"code": "CGK", "name": "Jakarta"},
    "destination": {"code": "DPS", "name": "Bali"},
    "total_results": 50,
    "tickets": [...]
  },
  "progress": 100
}
```

---

### Cancel Flight Job

**DELETE** `/flights/job/{job_id}`

Cancel a running flight search job.

**Response:** `204 No Content`

---

### List Airports

**GET** `/flights/airports`

Get list of supported airports with IATA codes.

**Response:**
```json
{
  "CGK": "Soekarno-Hatta International Airport (Jakarta)",
  "DPS": "Ngurah Rai International Airport (Bali)",
  "SUB": "Juanda International Airport (Surabaya)",
  "SIN": "Changi Airport (Singapore)"
}
```

---

## Hotel Endpoints

### Search Hotels (Synchronous)

**POST** `/hotels/search`

Search for hotels in a location. Blocks until search completes (30-60 seconds).

**Request Body:**
```json
{
  "location": "Jakarta",
  "save_results": true
}
```

**Response:** `HotelSearchResult`
```json
{
  "location": "Jakarta",
  "search_timestamp": "2026-03-30T10:00:00",
  "status": "success",
  "total_results": 100,
  "hotels": [
    {
      "hotel_name": "Mercure Jakarta",
      "location": "Gatot Subroto, South Jakarta",
      "star_rating": 4,
      "rating_score": "8.8/10",
      "price": "Rp 990.000",
      "features": ["Fitness center", "Pool"],
      "extracted_at": "2026-03-30T10:00:00"
    }
  ]
}
```

---

### Search Hotels (Asynchronous)

**POST** `/hotels/search/async`

Start an asynchronous hotel search. Returns immediately with a job ID.

**Request Body:**
```json
{
  "location": "Bali",
  "save_results": true
}
```

**Response:** `JobStatusResponse`
```json
{
  "job_id": "660e8400-e29b-41d4-a716-446655440001",
  "job_type": "hotel_search",
  "status": "pending",
  "params": {"location": "Bali"},
  "created_at": "2026-03-30T10:00:00",
  "progress": 0
}
```

---

### Get Hotel Job Status

**GET** `/hotels/job/{job_id}`

Get the status and results of a hotel search job.

---

### Cancel Hotel Job

**DELETE** `/hotels/job/{job_id}`

Cancel a running hotel search job.

---

### List Popular Destinations

**GET** `/hotels/popular-destinations`

Get list of popular hotel destinations.

**Response:**
```json
{
  "jakarta": "Jakarta, Indonesia",
  "bali": "Bali, Indonesia",
  "bandung": "Bandung, Indonesia",
  "singapore": "Singapore"
}
```

---

## Job Management Endpoints

### List All Jobs

**GET** `/jobs`

Get a list of all scraping jobs with their current status.

**Response:** `JobListResponse`
```json
{
  "total": 5,
  "jobs": [
    {
      "job_id": "...",
      "job_type": "flight_search",
      "status": "completed",
      ...
    }
  ]
}
```

---

### Get Job Status

**GET** `/jobs/{job_id}`

Get the status of any scraping job by ID.

---

### Cancel Job

**DELETE** `/jobs/{job_id}`

Cancel any running scraping job by ID.

---

### Cleanup Old Jobs

**POST** `/jobs/cleanup?max_age_seconds=3600`

Remove completed/failed jobs older than specified age.

**Response:**
```json
{
  "message": "Cleaned up 10 old jobs",
  "deleted_count": 10
}
```

---

### Get Job Statistics

**GET** `/jobs/stats`

Get statistics about all jobs.

**Response:**
```json
{
  "total_jobs": 25,
  "by_status": {
    "pending": 2,
    "running": 1,
    "completed": 20,
    "failed": 1,
    "cancelled": 1
  },
  "by_type": {
    "flight_search": 15,
    "hotel_search": 10
  }
}
```

---

## Health & Utility Endpoints

### Health Check

**GET** `/health`

Check API health status and Selenium connection.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2026-03-30T10:00:00",
  "selenium_connected": true,
  "selenium_url": "http://localhost:4444/wd/hub"
}
```

---

### API Root

**GET** `/`

Welcome message and API information.

---

## Usage Examples

### Python (requests)

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# Synchronous flight search
response = requests.post(
    f"{BASE_URL}/flights/search",
    json={"origin": "CGK", "destination": "DPS"}
)
result = response.json()
print(f"Found {result['total_results']} flights")

# Asynchronous flight search
response = requests.post(
    f"{BASE_URL}/flights/search/async",
    json={"origin": "CGK", "destination": "DPS"}
)
job = response.json()
job_id = job['job_id']

# Poll for results
while True:
    response = requests.get(f"{BASE_URL}/flights/job/{job_id}")
    job = response.json()
    
    if job['status'] == 'completed':
        print(f"Search completed: {job['result']['total_results']} flights")
        break
    elif job['status'] == 'failed':
        print(f"Search failed: {job['error']}")
        break
    
    time.sleep(2)
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Search flights
curl -X POST http://localhost:8000/api/v1/flights/search \
  -H "Content-Type: application/json" \
  -d '{"origin":"CGK","destination":"DPS"}'

# Search hotels
curl -X POST http://localhost:8000/api/v1/hotels/search \
  -H "Content-Type: application/json" \
  -d '{"location":"Jakarta"}'

# Async search
curl -X POST http://localhost:8000/api/v1/flights/search/async \
  -H "Content-Type: application/json" \
  -d '{"origin":"CGK","destination":"DPS"}'

# Check job status
curl http://localhost:8000/api/v1/jobs/{job_id}

# List all jobs
curl http://localhost:8000/api/v1/jobs
```

### JavaScript (fetch)

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// Search flights
async function searchFlights(origin, destination) {
  const response = await fetch(`${BASE_URL}/flights/search`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({origin, destination})
  });
  return await response.json();
}

// Async search with polling
async function searchFlightsAsync(origin, destination) {
  const response = await fetch(`${BASE_URL}/flights/search/async`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({origin, destination})
  });
  const job = await response.json();
  
  // Poll for results
  while (true) {
    const statusResponse = await fetch(`${BASE_URL}/flights/job/${job.job_id}`);
    const status = await statusResponse.json();
    
    if (status.status === 'completed') {
      return status.result;
    } else if (status.status === 'failed') {
      throw new Error(status.error);
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}
```

---

## Error Handling

The API uses standard HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 202 | Accepted (async job started) |
| 204 | No Content (successful deletion) |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (job not found) |
| 429 | Too Many Requests (rate limit) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (Selenium not connected) |

**Error Response Format:**
```json
{
  "message": "Error description",
  "details": {"additional": "information"}
}
```

---

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SELENIUM_REMOTE_URL` | `http://localhost:4444/wd/hub` | Selenium Grid URL |

---

## Best Practices

1. **Use Async Endpoints**: For production use, prefer `/search/async` endpoints to avoid blocking.

2. **Poll Responsibly**: When polling for job results, use 2-5 second intervals.

3. **Clean Up Jobs**: Use `/jobs/cleanup` periodically to remove old completed jobs.

4. **Monitor Job Stats**: Use `/jobs/stats` to monitor system load.

5. **Check Health**: Always check `/health` before starting scraping operations.

---

## Troubleshooting

### Selenium Connection Error

```json
{
  "status": "degraded",
  "selenium_connected": false
}
```

**Solution:** Start Selenium Grid:
```bash
docker-compose -f docker/selenium-grid/docker-compose.yml up -d
```

### Job Fails Immediately

Check logs for detailed error messages. Common causes:
- Invalid airport codes
- Website structure changes
- Network timeouts

### Slow Performance

- Reduce `max_tickets` or `max_hotels` parameters
- Disable scrolling for faster but fewer results
- Use async endpoints with multiple workers
