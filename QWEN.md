# Scraprrr - Project Context

## Project Overview

**Scraprrr** is a collection of web scrapers for Traveloka.com, a travel booking platform. The project contains two main scraping modules:

1. **Traveloka Flight Scraper** - Scrapes flight data (prices, schedules, airlines, baggage info)
2. **Traveloka Hotel Scraper** - Scrapes hotel data (ratings, prices, amenities, images)

Both scrapers use **Selenium WebDriver** with a Docker-based Selenium Grid for browser automation, and follow the **Page Object Model (POM)** design pattern for maintainable test automation.

### Architecture

```
scraprrr/
├── src/
│   ├── traveloka_flight_scraper/    # Flight scraper package
│   │   ├── scraper.py               # Main orchestration class
│   │   ├── page.py                  # Page Objects (Home, Results)
│   │   ├── extractor.py             # Data extraction logic
│   │   ├── driver.py                # WebDriver creation/management
│   │   ├── models.py                # Pydantic data models
│   │   ├── config.py                # Configuration (airport mappings)
│   │   ├── cli.py                   # Command-line interface
│   │   └── utils.py                 # Helper functions
│   └── traveloka_hotel_scraper/     # Hotel scraper package (same structure)
├── tests/                           # Pytest test suite
├── mappings/                        # Configuration files (airports.json)
├── docker/selenium-grid/            # Docker Compose for Selenium
├── results/                         # Output directory for scraped data
└── playground/                      # Jupyter notebooks for experimentation
```

### Key Technologies

| Technology | Purpose |
|------------|---------|
| Python 3.9+ | Core language |
| Selenium 4.15+ | Browser automation |
| Pydantic 2.0+ | Data validation and models |
| Pandas 2.0+ | Data manipulation/export |
| Docker | Selenium Grid server |
| Pytest | Testing framework |

### Design Patterns

- **Page Object Model (POM)**: Separate page classes (`TravelokaHomePage`, `TravelokaResultsPage`) encapsulate UI interactions
- **Data Models**: Pydantic models (`FlightTicket`, `FlightSearchResult`, `Hotel`, etc.) ensure type-safe data structures
- **Factory Pattern**: `create_driver()` function for WebDriver instantiation
- **Context Manager**: Scrapers support `with` statement for proper resource cleanup

## Building and Running

### Prerequisites

1. **Python 3.9+**
2. **Docker** (for Selenium Grid)

### Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"  # For development mode with dev tools

# 3. Start Selenium Grid
docker-compose -f docker/selenium-grid/docker-compose.yml up -d
```

### Running the Scrapers

#### Flight Scraper

```bash
# CLI - Search single route
traveloka-scraper search --origin CGK --destination DPS

# CLI - Search multiple predefined routes
traveloka-scraper search-multiple

# CLI - Without scrolling (faster, fewer results)
traveloka-scraper search --origin CGK --destination DPS --no-scroll

# Python API
from traveloka_flight_scraper import scrape_traveloka_flights
result = scrape_traveloka_flights("CGK", destination_code="DPS")
```

#### Hotel Scraper

```bash
# CLI - Search hotels
traveloka-hotel-scraper search "Jakarta"

# CLI - Batch search
traveloka-hotel-scraper search-batch "Jakarta,Bandung,Surabaya"

# Python API
from traveloka_hotel_scraper import scrape_traveloka_hotels
result = scrape_traveloka_hotels("Bali")
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=traveloka_flight_scraper --cov-report=term-missing

# Run specific test file
pytest tests/test_models.py -v

# Run hotel scraper tests
pytest tests/test_hotel_*.py -v
```

### Development Commands

```bash
# Code formatting
black src/ tests/

# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Build package
python -m build
```

## Configuration

### ScraperConfig (Flight)

```python
from traveloka_flight_scraper.models import ScraperConfig

config = ScraperConfig(
    selenium_remote_url="http://localhost:4444/wd/hub",
    scroll_enabled=True,
    scroll_timeout=60,
    max_tickets=0,  # 0 = unlimited
    save_csv=True,
    save_json=False,
    output_dir=".",
)
```

### HotelScraperConfig

```python
from traveloka_hotel_scraper.models import HotelScraperConfig

config = HotelScraperConfig(
    selenium_remote_url="http://localhost:4444/wd/hub",
    scroll_enabled=True,
    max_hotels=100,
    save_csv=True,
    save_json=False,
)
```

### Airport Mappings

Airport codes are stored in `mappings/airports.json`. Add custom airports:

```json
{
    "CGK": "Soekarno Hatta International Airport",
    "XXX": "Your Custom Airport"
}
```

## Development Conventions

### Code Style

- **Line length**: 100 characters (Black + Ruff configured)
- **Type hints**: Encouraged but not enforced (`disallow_untyped_defs = false`)
- **Imports**: Sorted automatically by Ruff (isort)
- **Formatting**: Black handles all formatting

### Testing Practices

- **Test files**: `test_*.py` in `tests/` directory
- **Fixtures**: Defined in `conftest.py`
- **Naming**: `Test*` classes, `test_*` functions
- **Coverage**: Target comprehensive coverage for models, extractors, utils

### Project Structure

- Each scraper is a standalone Python package under `src/`
- Shared utilities may be duplicated between scrapers (flight/hotel have separate codebases)
- Configuration files (airport mappings) at project root in `mappings/`

### CLI Conventions

- Entry points defined in `pyproject.toml`:
  - `traveloka-scraper` - Flight scraper CLI
  - `traveloka-hotel-scraper` - Hotel scraper CLI
- Use `argparse` with subcommands for different operations
- Verbose logging with `-v` flag

## Key Files Reference

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project configuration, dependencies, tool settings |
| `requirements.txt` | Pip dependencies |
| `docker/selenium-grid/docker-compose.yml` | Selenium Grid Docker setup |
| `mappings/airports.json` | Airport code-to-name mappings |
| `src/*/scraper.py` | Main scraper orchestration |
| `src/*/page.py` | Page Object classes |
| `src/*/models.py` | Pydantic data models |
| `src/*/cli.py` | CLI entry points |
| `tests/conftest.py` | Pytest fixtures |

## Troubleshooting

### Selenium Connection Issues

```bash
# Check container status
docker ps | grep selenium

# Restart container
docker-compose -f docker/selenium-grid/docker-compose.yml restart

# View logs
docker-compose -f docker/selenium-grid/docker-compose.yml logs selenium
```

### No Results Found

- Verify Selenium Grid is running: `http://localhost:4444`
- Use VNC viewer to watch browser: `http://localhost:7900` (password: `secret`)
- Increase timeouts in config
- Enable verbose logging: `-v` flag

### Common Issues

| Issue | Solution |
|-------|----------|
| Empty CSV output | Enable scrolling: `--no-scroll` flag off |
| Timeout errors | Increase `scroll_timeout` or `element_wait_timeout` |
| Element not found | Website structure may have changed; update selectors in `page.py` |
