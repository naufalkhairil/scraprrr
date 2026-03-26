"""
Traveloka Hotel Scraper - A Python package for scraping hotel data from Traveloka.com.

This package provides tools to search and extract hotel information from Traveloka,
including hotel names, prices, ratings, locations, and amenities.

Example usage:
    ```python
    from traveloka_hotel_scraper import TravelokaHotelScraper, HotelScraperConfig

    # Create scraper with custom config
    config = HotelScraperConfig(max_hotels=50, save_csv=True)
    scraper = TravelokaHotelScraper(config)

    # Search for hotels
    with scraper:
        result = scraper.search_hotels("Jakarta")
        print(f"Found {result.total_results} hotels")

    # Or use convenience function
    from traveloka_hotel_scraper import scrape_traveloka_hotels
    result = scrape_traveloka_hotels("Bali")
    ```

CLI usage:
    # Search hotels in Jakarta
    traveloka-hotel-scraper search Jakarta

    # Batch search multiple locations
    traveloka-hotel-scraper search-batch "Jakarta,Bandung,Surabaya"
"""

from traveloka_hotel_scraper.driver import create_driver, quit_driver
from traveloka_hotel_scraper.models import (
    Hotel,
    HotelLocation,
    HotelSearchResult,
    HotelScraperConfig,
)
from traveloka_hotel_scraper.scraper import (
    TravelokaHotelScraper,
    scrape_multiple_locations,
    scrape_traveloka_hotels,
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    # Version
    "__version__",
    # Models
    "Hotel",
    "HotelLocation",
    "HotelSearchResult",
    "HotelScraperConfig",
    # Scraper
    "TravelokaHotelScraper",
    "scrape_traveloka_hotels",
    "scrape_multiple_locations",
    # Driver
    "create_driver",
    "quit_driver",
]
