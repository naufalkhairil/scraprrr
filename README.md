# Scraprrr

A collection of web scrapers documented and maintained in one place. This repository houses various scraping projects for Traveloka.com.

## Prerequisites

### 1. Create Virtual Environment

It's recommended to create a virtual environment before installing dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Start Docker Selenium Server

```bash
docker-compose up -d
```

## Scrapers

| Scraper | Description | Status |
|---------|-------------|--------|
| [Traveloka Flight Scraper](./src/traveloka_flight_scraper/README.md) | Scrapes flight data from Traveloka.com using Selenium | ✅ Active |
| [Traveloka Hotel Scraper](./src/traveloka_hotel_scraper/README.md) | Scrapes hotel data from Traveloka.com using Selenium | ✅ Active |

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
