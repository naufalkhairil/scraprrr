# Scraprrr

> **⚠️ Note:** This repository is for **documentation and learning purposes only**. Built with assistance from Qwen Code AI. All scraping activities should comply with Traveloka.com's Terms of Service and robots.txt. Use responsibly and at your own risk.

A collection of web scrapers for Traveloka.com, providing unified CLI, Python API, and REST API for scraping flight and hotel data.

## Features

- **REST API**: FastAPI backend with synchronous and asynchronous endpoints
- **Unified CLI**: Single command for both flight and hotel scraping
- **Modular Architecture**: Clean separation between CLI, core, and scraper modules
- **Type-Safe**: Pydantic models for validated data structures
- **Backward Compatible**: Legacy package names still work
- **Job Management**: Background task support with job tracking and cancellation

## Project Structure

```
scraprrr/
├── src/scraprrr/                 # Main package
│   ├── __init__.py               # Public API exports
│   │
│   ├── api/                      # REST API (FastAPI)
│   │   ├── __init__.py
│   │   ├── app.py                # FastAPI application
│   │   ├── cli.py                # API server CLI
│   │   ├── core/                 # API core components
│   │   │   ├── config.py         # API configuration
│   │   │   ├── job_manager.py    # Background job manager
│   │   │   └── exceptions.py     # Custom exceptions
│   │   ├── routes/               # API routes
│   │   │   ├── __init__.py
│   │   │   ├── flights.py        # Flight endpoints
│   │   │   ├── hotels.py         # Hotel endpoints
│   │   │   └── jobs.py           # Job management endpoints
│   │   └── schemas/              # Pydantic schemas
│   │       └── __init__.py       # Request/Response schemas
│   │
│   ├── cli/                      # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py               # CLI entry point
│   │   ├── commands/             # Command handlers
│   │   │   ├── __init__.py
│   │   │   ├── flight.py         # Flight CLI commands
│   │   │   └── hotel.py          # Hotel CLI commands
│   │   └── parsers/              # Argument parsers
│   │       ├── __init__.py
│   │       ├── flight_parser.py
│   │       └── hotel_parser.py
│   │
│   ├── core/                     # Shared infrastructure
│   │   ├── __init__.py
│   │   ├── base.py               # Base scraper class
│   │   ├── driver.py             # WebDriver management
│   │   └── utils.py              # Common utilities
│   │
│   └── modules/                  # Domain-specific scrapers
│       ├── __init__.py
│       ├── flight/               # Flight scraper module
│       │   ├── __init__.py
│       │   ├── models.py         # FlightTicket, FlightSearchResult
│       │   ├── scraper.py        # FlightScraper class
│       │   ├── page.py           # Flight page objects
│       │   └── extractor.py      # Flight data extractor
│       │
│       └── hotel/                # Hotel scraper module
│           ├── __init__.py
│           ├── models.py         # Hotel, HotelSearchResult
│           ├── scraper.py        # HotelScraper class
│           ├── page.py           # Hotel page objects
│           └── extractor.py      # Hotel data extractor
│
├── tests/                        # Test suite
├── docker/
│   ├── selenium-grid/            # Docker Compose for Selenium
│   └── api/                      # Docker files for API
├── examples/                     # Example usage scripts
├── mappings/                     # Configuration (airports.json)
├── results/                      # Output directory for scraped data
└── playground/                   # Jupyter notebooks
```

## Prerequisites

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install package in development mode (recommended)
pip install -e ".[dev]"

# Or regular installation
pip install .
```

## Installation Options

> **⚠️ Important:** This package is **not published to PyPI**. You must install from the local repository or a Git URL. Running `pip install scraprrr` will fail or install a different package.

### Install from Local Directory (Recommended)

```bash
# Navigate to the repository root
cd /path/to/scraprrr

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install in editable/development mode (recommended)
pip install -e ".[dev]"

# Or regular installation
pip install .
```

### Install from Git Repository

```bash
# Install directly from GitHub
pip install git+https://github.com/yourusername/scraprrr.git

# Install with dev dependencies
pip install "git+https://github.com/yourusername/scraprrr.git#egg=scraprrr[dev]"

# Install from specific branch
pip install git+https://github.com/yourusername/scraprrr.git@refactor/unified-cli
```

### Verify Installation

```bash
# Check package is installed
pip show scraprrr

# Test CLI (must have venv activated)
traveloka --help

# Test import in Python
python -c "from scraprrr import FlightScraper, HotelScraper; print('✓ Installation successful')"
```

### Uninstall

```bash
pip uninstall scraprrr
```

### Notes

- **Package name**: `scraprrr`
- **Python version**: Requires Python 3.9+
- **Dev dependencies**: pytest, pytest-cov, black, ruff, mypy
- Always activate your virtual environment before using the CLI
- The `traveloka` command is only available after running `pip install -e .` or `pip install .`

### 3. Start Docker Selenium Server

```bash
docker-compose -f docker/selenium-grid/docker-compose.yml up -d
```

## CLI Usage

### Running the CLI

You can run the CLI in three ways:

```bash
# Option 1: Using PYTHONPATH (recommended for development)
PYTHONPATH=./src python -m scraprrr.cli.main search flight --origin CGK --destination DPS

# Option 2: Using installed package command
scraprrr search flight --origin CGK --destination DPS
```

### Unified CLI Commands

```bash
# Search flights
scraprrr search flight --origin CGK --destination DPS

# Search hotels
scraprrr search hotel --location Jakarta

# Batch search flights
scraprrr search batch --type flight --routes CGK-DPS,SUB-SIN

# Batch search hotels
scraprrr search batch --type hotel --locations Jakarta,Bali,Surabaya

# Search with custom settings
scraprrr search flight --origin CGK --destination SIN --no-scroll --json

# Enable verbose logging
scraprrr search flight --origin CGK --destination DPS --verbose
```

### CLI Options

#### Flight Search

| Option | Description |
|--------|-------------|
| `--origin, -o` | Origin airport IATA code (required) |
| `--destination, -d` | Destination airport IATA code (required) |
| `--origin-name` | Origin airport name (optional, auto-resolved) |
| `--destination-name` | Destination airport name (optional, auto-resolved) |
| `--max-tickets` | Maximum tickets threshold (default: 0 = unlimited) |
| `--selenium-url` | Selenium Grid URL (default: http://localhost:4444/wd/hub) |
| `--output-dir` | Output directory (default: current directory) |
| `--no-scroll` | Disable scrolling (faster, fewer results) |
| `--no-csv` | Disable CSV output |
| `--save-json` | Enable JSON output |
| `--delay` | Delay between batch searches (default: 5.0s) |

#### Hotel Search

| Option | Description |
|--------|-------------|
| `location` | City, hotel, or place name (required) |
| `--max-hotels` | Maximum hotels to collect (default: 100) |
| `--num-scrolls` | Maximum scrolls (default: 20) |
| `--selenium-url` | Selenium Grid URL (default: http://localhost:4444/wd/hub) |
| `--output-dir` | Output directory (default: current directory) |
| `--no-scroll` | Disable scrolling (faster, fewer results) |
| `--no-csv` | Disable CSV output |
| `--save-json` | Enable JSON output |

## Python API

### Flight Scraping

```python
from scraprrr import FlightScraper, scrape_flights

# Using convenience function
result = scrape_flights(origin="CGK", destination="DPS")
print(f"Found {result.total_results} flights")

# Using scraper class
with FlightScraper() as scraper:
    result = scraper.search(origin="CGK", destination="DPS")
    
    if result.status == "success":
        for ticket in result.tickets[:5]:
            print(f"{ticket.airline_name}: {ticket.price}")
```

### Hotel Scraping

```python
from scraprrr import HotelScraper, scrape_hotels

# Using convenience function
result = scrape_hotels(location="Jakarta")
print(f"Found {result.total_results} hotels")

# Using scraper class
with HotelScraper() as scraper:
    result = scraper.search(location="Bali")
    
    if result.status == "success":
        for hotel in result.hotels[:5]:
            print(f"{hotel.hotel_name}: {hotel.price}")
```

### Custom Configuration

```python
from scraprrr import FlightScraper, ScraperConfig

config = ScraperConfig(
    selenium_remote_url="http://localhost:4444/wd/hub",
    scroll_enabled=True,
    scroll_timeout=60,
    save_csv=True,
    save_json=False,
    output_dir="./results",
)

scraper = FlightScraper(config)
result = scraper.search(origin="CGK", destination="DPS")
```

## Data Models

### FlightTicket

```python
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
    "promos": ["Member Discount"],
    "extracted_at": "2026-03-26T10:00:00"
}
```

### Hotel

```python
{
    "hotel_name": "Mercure Jakarta",
    "location": "Gatot Subroto, South Jakarta",
    "star_rating": 4,
    "rating_score": "8.8/10",
    "price": "Rp 990.000",
    "features": ["Fitness center", "Pool"],
    "extracted_at": "2026-03-26T10:00:00"
}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scraprrr --cov-report=term-missing

# Run specific test file
pytest tests/test_flight_*.py -v
```

## Troubleshooting

### Selenium Connection Issues

```bash
# Check if Docker container is running
docker ps | grep selenium

# Restart the container
docker-compose -f docker/selenium-grid/docker-compose.yml restart

# Check logs
docker-compose -f docker/selenium-grid/docker-compose.yml logs selenium
```

### No Results Found

- Ensure the Selenium server is running: `http://localhost:4444`
- Use VNC viewer to watch browser: `http://localhost:7900` (password: `secret`)
- Increase timeouts in configuration
- Enable verbose logging: `--verbose` flag

### Common Issues

| Issue | Solution |
|-------|----------|
| Empty CSV output | Enable scrolling: remove `--no-scroll` flag |
| Timeout errors | Increase `scroll_timeout` in config |
| Element not found | Website structure may have changed; update selectors |

## REST API

Scraprrr provides a FastAPI-based REST API for programmatic access to flight and hotel scraping.

### Quick Start

```bash
# Start Selenium Grid
docker-compose -f docker/selenium-grid/docker-compose.yml up -d

# Start the API server
scraprrr-serve

# Or with Docker Compose
docker-compose -f docker/api/docker-compose.yml up -d
```

### API Endpoints

- **Base URL**: `http://localhost:8000/api/v1`
- **Interactive Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

#### Flight Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/flights/search` | Search flights (synchronous) |
| POST | `/flights/search/async` | Search flights (asynchronous) |
| GET | `/flights/job/{job_id}` | Get job status |
| DELETE | `/flights/job/{job_id}` | Cancel job |
| GET | `/flights/airports` | List airports |

#### Hotel Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/hotels/search` | Search hotels (synchronous) |
| POST | `/hotels/search/async` | Search hotels (asynchronous) |
| GET | `/hotels/job/{job_id}` | Get job status |
| DELETE | `/hotels/job/{job_id}` | Cancel job |
| GET | `/hotels/popular-destinations` | List destinations |

#### Job Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jobs` | List all jobs |
| GET | `/jobs/{job_id}` | Get job status |
| DELETE | `/jobs/{job_id}` | Cancel job |
| POST | `/jobs/cleanup` | Cleanup old jobs |
| GET | `/jobs/stats` | Get job statistics |

### Example Usage

```python
import requests

# Search flights synchronously
response = requests.post(
    "http://localhost:8000/api/v1/flights/search",
    json={"origin": "CGK", "destination": "DPS"}
)
flights = response.json()
print(f"Found {flights['total_results']} flights")

# Search hotels asynchronously
response = requests.post(
    "http://localhost:8000/api/v1/hotels/search/async",
    json={"location": "Jakarta"}
)
job = response.json()
job_id = job["job_id"]

# Poll for results
import time
while True:
    response = requests.get(f"http://localhost:8000/api/v1/hotels/job/{job_id}")
    job = response.json()
    if job["status"] == "completed":
        print(f"Found {job['result']['total_results']} hotels")
        break
    time.sleep(2)
```

### Full Documentation

See [API.md](API.md) for complete API documentation, examples, and best practices.

## Web Interface (Frontend)

Scraprrr includes a modern React-based web interface for easy interaction with the scraper.

### Quick Start

```bash
# Option 1: Development mode
cd frontend
npm install
npm run dev
# Open http://localhost:3000

# Option 2: Docker (all-in-one)
docker-compose -f docker-compose.fullstack.yml up -d
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Selenium VNC: http://localhost:7900
```

### Features

- ✈️ **Flight Search** - Search by origin/destination airports
- 🏨 **Hotel Search** - Search by location with quick-select destinations
- 📺 **Live VNC View** - Watch scraping in real-time via embedded Selenium viewer
- 📊 **Job Monitoring** - Track progress, view history, cancel jobs
- 📱 **Responsive** - Works on desktop and mobile

### Screenshots

The web interface provides:
1. **Search Forms** - Easy-to-use flight and hotel search forms
2. **Job Monitor** - Real-time progress tracking with VNC integration
3. **Results View** - Tabular display of scraped data
4. **Job History** - List and manage all scraping jobs

For more details, see [frontend/README.md](frontend/README.md).

## License

MIT License
