# Traveloka Flight Scraper

A well-structured Python package for scraping flight data from Traveloka.com using Selenium.

## Features

- **Modular Architecture**: Clean separation of concerns using Page Object Model pattern
- **Type-Safe Data Models**: Pydantic models for validated data structures
- **CLI Interface**: Command-line tool for easy usage
- **Configurable**: Extensive configuration options for scraping behavior
- **Test Coverage**: Comprehensive unit tests for all components

## Installation

### Prerequisites

1. **Start Docker Selenium Server** (from project root):

```bash
docker-compose up -d
```

2. **Install Python Dependencies**:

```bash
# From project root
pip install -r requirements.txt

# Or install as a package (recommended for development)
pip install -e ".[dev]"
```

3. **Verify Installation**:

```bash
traveloka-scraper --help
```

## Usage

### Command-Line Interface

#### Search Single Route

```bash
# Basic search
traveloka-scraper search --origin CGK --destination DPS

# With custom output directory
traveloka-scraper search -o CGK -d SIN --output-dir ./results

# Without scrolling (faster, fewer results)
traveloka-scraper search -o CGK -d DPS --no-scroll

# Enable JSON output in addition to CSV
traveloka-scraper search -o CGK -d DPS --json
```

```bash
# Basic search (without installing/compiling)
PYTHONPATH=./src python -m traveloka_flight_scraper.cli search --origin CGK --destination DPS
```

#### Search Multiple Routes

```bash
# Search predefined Indonesia-Singapore routes
traveloka-scraper search-multiple
```

### Python API

#### Basic Usage

```python
from traveloka_flight_scraper import TravelokaScraper

# Using context manager (recommended)
with TravelokaScraper() as scraper:
    result = scraper.search_flights(
        origin_code="CGK",
        origin_name="Soekarno Hatta International Airport",
        destination_code="DPS",
        destination_name="Ngurah Rai International Airport",
    )

if result.status == "success":
    print(f"Found {result.total_results} flights")
    for ticket in result.tickets:
        print(f"{ticket.airline_name}: {ticket.price}")
```

#### Using Convenience Function

```python
from traveloka_flight_scraper.scraper import scrape_traveloka_flights

result = scrape_traveloka_flights(
    origin_code="CGK",
    destination_code="DPS",
    selenium_url="http://localhost:4444/wd/hb",
)

if result.status == "success":
    # Convert to pandas DataFrame
    import pandas as pd
    df = pd.DataFrame(result.to_dataframe_data())
    print(df.head())
```

#### Custom Configuration

```python
from traveloka_flight_scraper import TravelokaScraper
from traveloka_flight_scraper.models import ScraperConfig

config = ScraperConfig(
    selenium_remote_url="http://localhost:4444/wd/hub",
    scroll_enabled=True,
    scroll_timeout=60,
    num_scrolls=5,
    save_csv=True,
    save_json=True,
    output_dir="./results",
)

scraper = TravelokaScraper(config)
scraper.initialize()

try:
    result = scraper.search_flights("CGK", destination_code="SIN")
finally:
    scraper.close()
```

#### Search Multiple Routes

```python
from traveloka_flight_scraper.scraper import scrape_multiple_routes

routes = [
    {"origin_code": "CGK", "destination_code": "SIN"},
    {"origin_code": "DPS", "destination_code": "SIN"},
    {"origin_code": "SUB", "destination_code": "SIN"},
]

results = scrape_multiple_routes(routes=routes)

for result in results:
    print(f"{result.origin.code} → {result.destination.code}: {result.total_results} flights")
```

## Data Models

### FlightTicket

```python
{
    "airline_name": "Garuda Indonesia",
    "airline_logo": "https://...",
    "departure_time": "08:00",
    "departure_airport": "CGK",
    "arrival_time": "10:30",
    "arrival_airport": "DPS",
    "duration": "2h 30m",
    "flight_type": "Direct",
    "price": "Rp 1.500.000",
    "original_price": "Rp 2.000.000",
    "baggage": "20 kg",
    "promos": ["Member Discount"],
    "special_tag": "Bigger Discount",
    "highlight_label": "Cheapest",
    "extracted_at": "2026-03-26T10:00:00"
}
```

### FlightSearchResult

```python
{
    "origin": {"code": "CGK", "name": "Soekarno Hatta International Airport"},
    "destination": {"code": "DPS", "name": "Ngurah Rai International Airport"},
    "search_timestamp": "2026-03-26T10:00:00",
    "status": "success",
    "total_results": 50,
    "tickets": [...],
    "error_message": None
}
```

## Known Airports

Airport mappings are stored in `mappings/airports.json` at the project root.

### Default Airports

> List airports below is not align with Traveloka naming

| Code | Name |
|------|------|
| CGK | Soekarno Hatta International Airport (Jakarta) |
| DPS | Ngurah Rai International Airport (Bali) |
| SIN | Changi International Airport (Singapore) |
| SUB | Juanda International Airport (Surabaya) |
| KNO | Kualanamu International Airport (Medan) |
| BTH | Hang Nadim International Airport (Batam) |
| JKT | Soekarno Hatta International Airport (Jakarta) |
| UPG | Sultan Hasanuddin International Airport |
| BPN | Sultan Aji Muhammad Sulaiman Airport |
| PLM | Sultan Mahmud Badaruddin II Airport |
| PDG | Minangkabau International Airport |
| PKU | Sultan Syarif Kasim II International Airport |
| BDO | Husein Sastranegara International Airport |
| SOC | Adisumarmo International Airport |
| JOG | Yogyakarta International Airport |
| SRG | Ahmad Yani International Airport |
| MLG | Abdul Rachman Saleh Airport |
| LOP | Lombok International Airport |
| AMQ | Pattimura Airport |
| MDC | Sam Ratulangi International Airport |
| MNL | Ninoy Aquino International Airport |
| BKK | Suvarnabhumi Airport |
| KUL | Kuala Lumpur International Airport |

### Adding Custom Airports

Edit `mappings/airports.json` to add new airports:

```json
{
    "CGK": "Soekarno Hatta International Airport",
    "YOUR_CODE": "Your Airport Name"
}
```

### Programmatic Airport Management

```python
from traveloka_flight_scraper import get_airport_name, get_airport_code, ConfigManager

# Get airport name by code
name = get_airport_name("CGK")
print(name)  # Soekarno Hatta International Airport

# Get airport code by name (partial match)
code = get_airport_code("Changi")
print(code)  # SIN

# Add airport at runtime (doesn't save to file)
cm = ConfigManager()
cm.add_airport("XXX", "My Custom Airport")
print(cm.get_airport_name("XXX"))  # My Custom Airport

# List all airports
airports = cm.list_airports()
for code, name in airports.items():
    print(f"{code}: {name}")
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=traveloka_flight_scraper

# Run specific test file
pytest tests/test_models.py -v
```

## Development

### Building the Package

```bash
# Build wheel and sdist
python -m build

# Install locally
pip install -e .
```

## Troubleshooting

### No Results Found

Traveloka may have anti-bot protection. Try:

1. **Open VNC Viewer**: Visit `http://localhost:7900` (password: `secret`) to watch the browser
2. **Increase Delays**: Add longer waits between actions
3. **Manual Verification**: Check if the search works manually in the browser

### CSV Output Empty

Ensure scrolling is enabled to load more tickets:

```python
config = ScraperConfig(scroll_enabled=True, num_scrolls=10)
```

## License

MIT License
