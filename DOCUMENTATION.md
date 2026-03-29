# Scraprrr - Complete Repository Documentation

> **⚠️ Legal Notice:** This repository is for **documentation and educational purposes only**. All scraping activities must comply with target websites' Terms of Service and robots.txt. Use responsibly and at your own risk.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Code Architecture](#code-architecture)
4. [Project Structure](#project-structure)
5. [Technology Stack](#technology-stack)
6. [Installation](#installation)
7. [Configuration](#configuration)
8. [Usage](#usage)
9. [Development](#development)
10. [Testing](#testing)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)

---

## Overview

**Scraprrr** is a modular web scraping framework designed for extracting e-commerce data (flights, hotels, and more) from travel platforms like Traveloka. It provides both a command-line interface (CLI) and a Python API, making it accessible for developers and non-technical users alike.

### What It Does

- **Flight Scraping**: Extract flight information including prices, schedules, airlines, and promotions
- **Hotel Scraping**: Collect hotel data including ratings, amenities, locations, and pricing
- **Unified Interface**: Single codebase for multiple scraper types
- **Data Export**: Save results to CSV, JSON, or ingest into databases
- **Real-time Monitoring**: Track scraper progress and status (via API)

### Key Design Principles

1. **Modularity**: Each scraper type is a self-contained module
2. **Type Safety**: Pydantic models ensure data validation
3. **Reusability**: Shared infrastructure reduces code duplication
4. **Extensibility**: Easy to add new scraper types
5. **Testability**: Comprehensive test suite with fixtures

---

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Unified CLI** | Single command interface for all scraper types |
| **Python API** | Programmatic access for integration |
| **Modular Design** | Clean separation of concerns |
| **Type-Safe Models** | Pydantic validation for all data |
| **Selenium Integration** | Browser automation via Docker |
| **Data Export** | CSV, JSON, and database ingestion |
| **Batch Processing** | Scrape multiple routes/locations |
| **Configurable** | Extensive customization options |

### Scraper Modules

#### Flight Scraper
- Origin/destination search
- Date-based queries
- Price tracking
- Airline filtering
- Baggage info extraction
- Promo detection

#### Hotel Scraper
- Location-based search
- Star rating extraction
- Guest ratings
- Amenity detection
- Price comparison
- Multi-page scrolling

---

## Code Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Scraprrr                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    CLI Layer                             │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │   main.py    │  │  commands/   │  │  parsers/    │   │    │
│  │  │  (Entry)     │  │  (Handlers)  │  │  (Args)      │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Core Layer                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │   base.py    │  │  driver.py   │  │  utils.py    │   │    │
│  │  │  (Base       │  │  (WebDriver  │  │  (Config,    │   │    │
│  │  │   Scraper)   │  │    Mgmt)     │  │   I/O)       │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│              ┌───────────────┼───────────────┐                   │
│              │               │               │                   │
│              ▼               ▼               ▼                   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │  Flight Module  │ │   Hotel Module  │ │  Future Modules │    │
│  │                 │ │                 │ │                 │    │
│  │ - models.py     │ │ - models.py     │ │ - ...           │    │
│  │ - scraper.py    │ │ - scraper.py    │ │                 │    │
│  │ - page.py       │ │ - page.py       │ │                 │    │
│  │ - extractor.py  │ │ - extractor.py  │ │                 │    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Selenium   │  │   Target     │  │   Output     │          │
│  │    Grid      │  │   Websites   │  │   Files/DB   │          │
│  │  (Docker)    │  │  (Traveloka) │  │  (CSV/JSON)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Module Pattern

Each scraper module follows a consistent pattern:

```
module_name/
├── __init__.py      # Public exports
├── models.py        # Pydantic data models
├── scraper.py       # Main scraper logic (extends BaseScraper)
├── page.py          # Page objects (Selenium interactions)
└── extractor.py     # Data extraction from DOM elements
```

### Class Hierarchy

```
BaseScraper[T] (Abstract)
    │
    ├── FlightScraper
    │     └── search(origin, destination) → FlightSearchResult
    │
    └── HotelScraper
          └── search(location) → HotelSearchResult
```

### Data Flow

```
1. CLI/API Request
         │
         ▼
2. Scraper.initialize() → WebDriver
         │
         ▼
3. Scraper.search() → Navigate to page
         │
         ▼
4. Page.search() → Input parameters, submit
         │
         ▼
5. Page.wait_for_results() → Wait for load
         │
         ▼
6. Page.scroll_to_load_more() → Load additional data
         │
         ▼
7. Extractor.extract_all() → Parse DOM elements
         │
         ▼
8. Scraper._create_items() → Validate with Pydantic
         │
         ▼
9. Scraper.save_results() → CSV/JSON/Database
         │
         ▼
10. Return Result object
```

---

## Project Structure

```
scraprrr/
│
├── 📄 README.md                  # User-facing documentation
├── 📄 PRD.md                     # Product Requirements Document
├── 📄 pyproject.toml             # Python project configuration
├── 📄 requirements.txt           # Pip dependencies
├── 📄 .gitignore                 # Git ignore rules
│
├── 📁 src/scraprrr/              # Main package source
│   ├── __init__.py               # Public API exports
│   │
│   ├── 📁 cli/                   # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py               # CLI entry point (argparse)
│   │   ├── commands/             # Command handlers
│   │   │   ├── __init__.py
│   │   │   ├── flight.py         # Flight CLI commands
│   │   │   └── hotel.py          # Hotel CLI commands
│   │   └── parsers/              # Argument parsers
│   │       ├── __init__.py
│   │       ├── flight_parser.py  # Flight argument definitions
│   │       └── hotel_parser.py   # Hotel argument definitions
│   │
│   ├── 📁 core/                  # Shared infrastructure
│   │   ├── __init__.py
│   │   ├── base.py               # BaseScraper abstract class
│   │   ├── driver.py             # WebDriver creation/management
│   │   └── utils.py              # Config, I/O utilities
│   │
│   └── 📁 modules/               # Domain-specific scrapers
│       ├── __init__.py
│       ├── flight/               # Flight scraper module
│       │   ├── __init__.py
│       │   ├── models.py         # FlightTicket, FlightSearchResult
│       │   ├── scraper.py        # FlightScraper implementation
│       │   ├── page.py           # FlightPage (Selenium page object)
│       │   └── extractor.py      # FlightExtractor (DOM parsing)
│       │
│       └── hotel/                # Hotel scraper module
│           ├── __init__.py
│           ├── models.py         # Hotel, HotelSearchResult
│           ├── scraper.py        # HotelScraper implementation
│           ├── page.py           # HotelPage (Selenium page object)
│           └── extractor.py      # HotelExtractor (DOM parsing)
│
├── 📁 tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures and config
│   ├── test_models.py            # Flight model tests
│   ├── test_scraper.py           # Scraper tests
│   ├── test_page.py              # Page object tests
│   ├── test_extractor.py         # Extractor tests
│   ├── test_utils.py             # Utility tests
│   ├── test_hotel_*.py           # Hotel module tests
│   └── ...
│
├── 📁 docker/selenium-grid/      # Selenium Docker configuration
│   └── docker-compose.yml        # Selenium standalone Chrome
│
├── 📁 agents/                    # AI agent documentation
│   └── FEATURE_AGENTS.md         # Code generation agents
│
├── 📁 backup/                    # Legacy scraper backups
│   ├── traveloka_flight_scraper/
│   └── traveloka_hotel_scraper/
│
├── 📁 playground/                # Jupyter notebooks
│   ├── flight_scraper.ipynb
│   └── hotel_scraper.ipynb
│
├── 📁 mappings/                  # Configuration files
│   └── airports.json             # Airport code mappings
│
├── 📁 results/                   # Output directory (gitignored)
│   ├── *.csv                     # Scraped flight/hotel data
│   └── *.json                    # JSON exports
│
└── 📁 .git/                      # Git repository
```

---

## Technology Stack

### Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.9+ | Primary language |
| **Package Manager** | pip | - | Dependency management |
| **Build System** | setuptools | 61.0+ | Package building |

### Libraries & Frameworks

| Library | Version | Purpose |
|---------|---------|---------|
| **Selenium** | 4.15.0+ | Browser automation |
| **Pydantic** | 2.0.0+ | Data validation |
| **Pandas** | 2.0.0+ | Data manipulation, CSV export |
| **Requests** | 2.31.0+ | HTTP requests |

### Development Tools

| Tool | Version | Purpose |
|------|---------|---------|
| **pytest** | 7.0.0+ | Testing framework |
| **pytest-cov** | 4.0.0+ | Test coverage |
| **black** | 23.0.0+ | Code formatting |
| **ruff** | 0.1.0+ | Linting |
| **mypy** | 1.0.0+ | Type checking |

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker | Selenium Grid |
| **Browser** | Chrome (via Selenium) | Web automation |
| **Selenium Grid** | selenium/standalone-chrome | Remote WebDriver |

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Docker (for Selenium Grid)
- Git (optional, for cloning)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/scraprrr.git
cd scraprrr
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Development mode (recommended)
pip install -e ".[dev]"

# Or regular installation
pip install .
```

### Step 4: Start Selenium Grid

```bash
docker-compose -f docker/selenium-grid/docker-compose.yml up -d
```

### Verify Installation

```bash
# Check package
pip show scraprrr

# Test CLI
scraprrr --help

# Test imports
python -c "from scraprrr import FlightScraper, HotelScraper; print('✓ Success')"
```

---

## Configuration

### ScraperConfig Options

All scrapers inherit from `ScraperConfig` with these options:

```python
from scraprrr import ScraperConfig

config = ScraperConfig(
    # Selenium settings
    selenium_remote_url="http://localhost:4444/wd/hub",
    page_load_timeout=30,
    element_wait_timeout=15,
    
    # Scraping settings
    scroll_enabled=True,
    scroll_timeout=60,
    scroll_pause=2.0,
    
    # Output settings
    save_csv=True,
    save_json=False,
    output_dir="./results",
)
```

### Module-Specific Config

#### FlightScraperConfig

```python
from scraprrr import FlightScraperConfig

config = FlightScraperConfig(
    max_tickets=0,  # 0 = unlimited
    **base_config_options
)
```

#### HotelScraperConfig

```python
from scraprrr import HotelScraperConfig

config = HotelScraperConfig(
    max_hotels=100,
    **base_config_options
)
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SELENIUM_URL` | `http://localhost:4444/wd/hub` | Selenium Grid endpoint |
| `SCRAPRRR_OUTPUT_DIR` | `.` | Default output directory |
| `SCRAPRRR_VERBOSE` | `False` | Enable verbose logging |

---

## Usage

### CLI Usage

#### Flight Search

```bash
# Basic search
scraprrr search flight --origin CGK --destination DPS

# With options
scraprrr search flight \
  --origin CGK \
  --destination DPS \
  --origin-name "Soekarno-Hatta" \
  --destination-name "Ngurah Rai" \
  --max-tickets 50 \
  --no-scroll \
  --save-json \
  --output-dir ./my-results
```

#### Hotel Search

```bash
# Basic search
scraprrr search hotel --location "Jakarta"

# With options
scraprrr search hotel \
  --location "Bali" \
  --max-hotels 200 \
  --num-scrolls 30 \
  --save-json
```

#### Batch Search

```bash
# Multiple flight routes
scraprrr search batch \
  --type flight \
  --routes "CGK-DPS,SUB-SIN,JKT-BKK" \
  --delay 10

# Multiple hotel locations
scraprrr search batch \
  --type hotel \
  --locations "Jakarta,Bali,Surabaya,Bandung"
```

### Python API

#### Basic Flight Scraping

```python
from scraprrr import FlightScraper, FlightScraperConfig

# Configure
config = FlightScraperConfig(
    scroll_enabled=True,
    save_csv=True,
    output_dir="./results"
)

# Scrape
with FlightScraper(config) as scraper:
    result = scraper.search(
        origin="CGK",
        destination="DPS"
    )
    
    if result.status == "success":
        print(f"Found {result.total_results} flights")
        for ticket in result.tickets[:5]:
            print(f"{ticket.airline_name}: {ticket.price}")
```

#### Basic Hotel Scraping

```python
from scraprrr import HotelScraper

with HotelScraper() as scraper:
    result = scraper.search(location="Bali")
    
    if result.status == "success":
        for hotel in result.hotels[:10]:
            print(f"{hotel.hotel_name} - {hotel.price}")
```

#### Convenience Functions

```python
from scraprrr import scrape_flights, scrape_hotels

# Quick flight search
result = scrape_flights(origin="CGK", destination="DPS")

# Quick hotel search
result = scrape_hotels(location="Jakarta")
```

#### Working with Results

```python
# Access result data
print(f"Status: {result.status}")
print(f"Total: {result.total_results}")
print(f"Error: {result.error_message}")

# Convert to dict
data = result.to_dict()

# Convert for pandas
df_data = result.to_dataframe_data()

# Save manually
scraper.save_results(result)
```

---

## Development

### Setting Up Development Environment

```bash
# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Verify installation
pytest --version
black --version
ruff --version
```

### Code Style

The project uses **black** for formatting and **ruff** for linting:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/scraprrr/
```

### Adding a New Scraper Module

1. **Create module directory:**
   ```bash
   mkdir src/scraprrr/modules/new_scraper
   ```

2. **Create module files:**
   - `__init__.py` - Exports
   - `models.py` - Pydantic models
   - `scraper.py` - Scraper class
   - `page.py` - Page objects
   - `extractor.py` - Data extractor

3. **Update parent `__init__.py`:**
   ```python
   from scraprrr.modules.new_scraper import NewScraper, scrape_new
   ```

4. **Add CLI commands** (optional)

5. **Write tests**

See `agents/FEATURE_AGENTS.md` for automated scaffolding.

---

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=scraprrr --cov-report=term-missing

# Specific test file
pytest tests/test_models.py -v

# Specific test function
pytest tests/test_models.py::test_flight_ticket_model -v

# Skip slow tests
pytest -m "not slow"
```

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_models.py        # Pydantic model tests
├── test_scraper.py       # Scraper logic tests
├── test_page.py          # Page object tests
├── test_extractor.py     # Extractor tests
├── test_utils.py         # Utility function tests
└── test_*_*.py          # Module-specific tests
```

### Example Test

```python
# tests/test_models.py
from scraprrr.modules.flight.models import FlightTicket

def test_flight_ticket_creation():
    ticket = FlightTicket(
        airline_name="Garuda Indonesia",
        departure_time="08:00",
        departure_airport="CGK",
        arrival_time="10:30",
        arrival_airport="DPS",
        duration="2h 30m",
        flight_type="Direct",
        price="Rp 1.500.000",
        baggage="20 kg"
    )
    assert ticket.airline_name == "Garuda Indonesia"
    assert ticket.price == "Rp 1.500.000"
```

---

## Deployment

### Docker Deployment

#### Selenium Grid

```bash
# Start Selenium
docker-compose -f docker/selenium-grid/docker-compose.yml up -d

# Check status
docker ps | grep selenium

# View logs
docker-compose -f docker/selenium-grid/docker-compose.yml logs selenium
```

#### Full Stack (Future)

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Services:
# - scraprrr-api (FastAPI)
# - scraprrr-worker (Celery)
# - postgres (Database)
# - redis (Broker)
# - selenium-grid (Browsers)
```

### Production Considerations

1. **Scale Selenium Grid**: Use hub-node architecture
2. **Database**: PostgreSQL for result storage
3. **Queue**: Redis + Celery for async jobs
4. **API**: FastAPI with uvicorn workers
5. **Monitoring**: Prometheus + Grafana
6. **Logging**: Structured JSON logs

See `PRD.md` for detailed deployment architecture.

---

## Troubleshooting

### Common Issues

#### Selenium Connection Failed

**Symptom:** `Could not connect to Selenium server`

**Solution:**
```bash
# Check if container is running
docker ps | grep selenium

# Restart container
docker-compose -f docker/selenium-grid/docker-compose.yml restart

# Check logs
docker-compose -f docker/selenium-grid/docker-compose.yml logs
```

#### No Results Found

**Symptom:** Empty CSV/JSON output

**Solution:**
- Enable scrolling: Remove `--no-scroll` flag
- Increase timeout: `--scroll-timeout 120`
- Check VNC: `http://localhost:7900` (password: `secret`)
- Enable verbose: `--verbose` flag

#### Chrome Crashes

**Symptom:** Browser closes unexpectedly

**Solution:**
```bash
# Increase shared memory
docker-compose -f docker/selenium-grid/docker-compose.yml up -d --scale selenium=1

# Or edit docker-compose.yml:
# shm_size: 4gb
```

#### Element Not Found

**Symptom:** `TimeoutException: Unable to locate element`

**Solution:**
- Website structure may have changed
- Update selectors in `page.py`
- Increase `element_wait_timeout`
- Check VNC for visual debugging

#### Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'scraprrr'`

**Solution:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall package
pip install -e .
```

---

## Contributing

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes**
4. **Run tests:**
   ```bash
   pytest --cov=scraprrr
   ```
5. **Format and lint:**
   ```bash
   black src/ tests/
   ruff check src/ tests/
   ```
6. **Commit with conventional commits:**
   ```bash
   git commit -m "feat: add new scraper module"
   ```
7. **Push and create PR**

### Code Review Checklist

- [ ] Tests added/updated
- [ ] Type hints added
- [ ] Docstrings complete
- [ ] Black formatted
- [ ] Ruff linting passes
- [ ] No sensitive data exposed

---

## License

MIT License - See LICENSE file for details.

---

## Support

- **Documentation:** `README.md`, `PRD.md`
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

## Changelog

### v2.0.0 (2026-03-26)
- Unified CLI for flight and hotel scraping
- Modular architecture refactor
- Pydantic v2 migration
- Improved type safety

### v1.0.0 (Previous)
- Initial flight scraper
- Basic hotel scraper
- CLI interface

---

*Last updated: March 29, 2026*
