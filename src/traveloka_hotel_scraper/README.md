# Traveloka Hotel Scraper

A Python package for scraping hotel data from Traveloka.com using Selenium.

## Features

- Search hotels by location (city, hotel name, or place)
- Extract comprehensive hotel information:
  - Hotel name and location
  - Star rating and guest reviews
  - Pricing (original, discounted, total with taxes)
  - Images (main and supporting)
  - Amenities and features
  - Booking activity indicators
- Infinite scroll support to load more results
- Export to CSV and JSON formats
- Batch search multiple locations
- Command-line interface

## Installation

Install as part of the scraprrr package:

```bash
pip install -e .
```

## Quick Start

### Python API

```python
from traveloka_hotel_scraper import scrape_traveloka_hotels

# Simple search
result = scrape_traveloka_hotels("Jakarta")
print(f"Found {result.total_results} hotels")

# Access hotel data
for hotel in result.hotels[:5]:
    print(f"- {hotel.hotel_name}: {hotel.price}")
```

### Using Scraper Class

```python
from traveloka_hotel_scraper import TravelokaHotelScraper, HotelScraperConfig

# Configure scraper
config = HotelScraperConfig(
    max_hotels=50,          # Collect up to 50 hotels
    scroll_enabled=True,    # Enable infinite scroll
    save_csv=True,          # Save results to CSV
    save_json=False,        # Don't save JSON
)

# Create and run scraper
with TravelokaHotelScraper(config) as scraper:
    result = scraper.search_hotels("Bali")
    
    if result.status == "success":
        print(f"Successfully scraped {result.total_results} hotels")
```

### Batch Search

```python
from traveloka_hotel_scraper import scrape_multiple_locations

# Search multiple locations
locations = ["Jakarta", "Bandung", "Surabaya", "Bali"]
results = scrape_multiple_locations(locations)

for result in results:
    print(f"{result.location}: {result.total_results} hotels")
```

## CLI Usage

### Search Hotels

```bash
# Basic search
traveloka-hotel-scraper search Jakarta

# With options
traveloka-hotel-scraper search Bali --max-hotels 50 --no-scroll

# Custom output directory
traveloka-hotel-scraper search Yogyakarta --output-dir ./results
```

### Batch Search

```bash
# Comma-separated locations
traveloka-hotel-scraper search-batch "Jakarta,Bandung,Surabaya"

# From file (one location per line)
traveloka-hotel-scraper search-batch --locations-file cities.txt

# With delay between searches
traveloka-hotel-scraper search-batch "Jakarta,Bali" --delay 10
```

### CLI Options

```
Global Options:
  -v, --verbose         Enable verbose logging
  --selenium-url        Selenium Grid server URL

Search Command:
  location              City, hotel, or place to search
  --max-hotels          Maximum hotels to collect (default: 100)
  --num-scrolls         Maximum scrolls (default: 20)
  --no-scroll           Disable scrolling
  --no-save-csv         Disable CSV output
  --save-json           Enable JSON output
  --output-dir          Output directory

Batch Search Command:
  locations             Comma-separated locations
  --locations-file      File with locations
  --delay               Delay between searches (seconds)
```

## Data Model

### Hotel

| Field | Type | Description |
|-------|------|-------------|
| hotel_name | str | Name of the hotel |
| location | str | Hotel location/area |
| star_rating | int | Star rating (1-5) |
| rating_score | str | Guest rating (e.g., "8.8/10") |
| review_count | str | Review count (e.g., "3,4K reviews") |
| main_image_url | str | Main image URL |
| supporting_images | list | Additional image URLs |
| original_price | str | Price before discount |
| price | str | Current price |
| total_price | str | Total with taxes |
| booking_info | str | Booking activity |
| hotel_type | str | Accommodation type |
| ranking | str | Ranking badge |
| features | list | Amenities/features |

## Configuration

### HotelScraperConfig

```python
config = HotelScraperConfig(
    # Selenium settings
    selenium_remote_url="http://localhost:4444/wd/hub",
    element_wait_timeout=15,
    
    # Scraping settings
    scroll_enabled=True,
    scroll_timeout=60,
    scroll_pause=2.0,
    max_hotels=100,
    num_scrolls=20,
    
    # Output settings
    save_csv=True,
    save_json=False,
    output_dir=".",
)
```

## Prerequisites

### Selenium Grid

Start Docker Selenium server:

```bash
docker-compose up -d
```

Or use your own Selenium Grid server.

## Output Files

### CSV Output

Hotels are saved to CSV with columns matching the Hotel model fields:

```csv
hotel_name,location,star_rating,rating_score,price,...
Mercure Jakarta,Gatot Subroto,4,8.8/10,Rp 990.000,...
```

### JSON Output

Full search result including metadata:

```json
{
  "location": "Jakarta",
  "search_timestamp": "2026-03-26T10:00:00",
  "status": "success",
  "total_results": 121,
  "hotels": [...]
}
```

## Error Handling

The scraper handles errors gracefully:

- Network timeouts
- Element not found
- Parsing failures
- Selenium connection issues

Failed searches return a `HotelSearchResult` with `status="error"` and an error message.

## Logging

Enable verbose logging for debugging:

```bash
traveloka-hotel-scraper search Jakarta -v
```

Or in Python:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Limitations

- Requires Selenium Grid (Docker) to be running
- Rate limiting may apply - use delays for batch searches
- Website structure changes may break selectors
- Infinite scroll may not load all hotels

## License

MIT License
