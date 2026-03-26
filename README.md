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
