"""
Scraprrr - A collection of web scrapers for Traveloka.com.

This package provides scrapers for flights and hotels with a unified CLI.

Example usage:
    from scraprrr.modules import FlightScraper, HotelScraper
    from scraprrr.core import ScraperConfig

    # Flight scraping
    scraper = FlightScraper()
    result = scraper.search(origin="CGK", destination="DPS")

    # Hotel scraping
    scraper = HotelScraper()
    result = scraper.search(location="Jakarta")
"""

__version__ = "2.0.0"
__author__ = "Your Name"

# Public API - Core components
from scraprrr.core import ScraperConfig, create_driver, quit_driver

# Public API - Modules
from scraprrr.modules.flight import FlightScraper, FlightSearchResult, FlightTicket
from scraprrr.modules.hotel import HotelScraper, HotelSearchResult, Hotel

# Convenience functions
from scraprrr.modules.flight import scrape_flights
from scraprrr.modules.hotel import scrape_hotels

__all__ = [
    # Version
    "__version__",
    # Core
    "ScraperConfig",
    "create_driver",
    "quit_driver",
    # Flight
    "FlightScraper",
    "FlightSearchResult",
    "FlightTicket",
    "scrape_flights",
    # Hotel
    "HotelScraper",
    "HotelSearchResult",
    "Hotel",
    "scrape_hotels",
]
