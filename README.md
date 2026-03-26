# Scraprrr

A collection of web scrapers documented and maintained in one place. This repository houses various scraping projects, starting with a Traveloka flight scraper as the initial implementation.

## Prerequisites

**Start Docker Selenium Server** (from project root):

```bash
docker-compose up -d
```

## Scrapers

| Scraper | Description | Status |
|---------|-------------|--------|
| [Traveloka Flight Scraper](#traveloka-flight-scraper) | Scrapes flight data from Traveloka.com using Selenium | ✅ Active |


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

## License

MIT License
