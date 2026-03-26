# Scraprrr

A collection of web scrapers documented and maintained in one place. This repository houses various scraping projects for Traveloka.com.

## Prerequisites

**Start Docker Selenium Server** (from project root):

```bash
docker-compose up -d
```

## Scrapers

| Scraper | Description | Status |
|---------|-------------|--------|
| [Traveloka Flight Scraper](#traveloka-flight-scraper) | Scrapes flight data from Traveloka.com using Selenium | ✅ Active |
| [Traveloka Hotel Scraper](#traveloka-hotel-scraper) | Scrapes hotel data from Traveloka.com using Selenium | ✅ Active |

## Traveloka Flight Scraper

Scrape flight information from Traveloka.com including airline, prices, departure/arrival times, and more.

### Quick Start (Flight)

```python
from traveloka_flight_scraper import scrape_traveloka_flights

# Search flights
result = scrape_traveloka_flights("CGK", destination_code="DPS")
print(f"Found {result.total_results} flights")
```

### CLI (Flight)

```bash
# Search flights
traveloka-scraper search CGK DPS

# Batch search
traveloka-scraper search-batch --routes routes.json
```

See `src/traveloka_flight_scraper/README.md` for full documentation.

## Traveloka Hotel Scraper

Scrape hotel information from Traveloka.com including prices, ratings, amenities, and more.

### Quick Start (Hotel)

```python
from traveloka_hotel_scraper import scrape_traveloka_hotels

# Search hotels
result = scrape_traveloka_hotels("Jakarta")
print(f"Found {result.total_results} hotels")

# Access hotel data
for hotel in result.hotels[:5]:
    print(f"- {hotel.hotel_name}: {hotel.price}")
```

### CLI (Hotel)

```bash
# Search hotels in a city
traveloka-hotel-scraper search Jakarta

# Batch search multiple cities
traveloka-hotel-scraper search-batch "Jakarta,Bandung,Surabaya"

# With options
traveloka-hotel-scraper search Bali --max-hotels 50 --no-scroll
```

See `src/traveloka_hotel_scraper/README.md` for full documentation.

## Installation

```bash
pip install -e .
```

## Troubleshooting

### Selenium Connection Issues

If you can't connect to the Selenium server:

```bash
# Check if Docker container is running
docker ps | grep selenium

# Restart the container
docker-compose restart

# Check logs
docker-compose logs selenium
```

### No Results Found

- Ensure the Selenium server is running
- Check your internet connection
- Verify the location/airport codes are valid
- Try increasing the timeout values

## License

MIT License
