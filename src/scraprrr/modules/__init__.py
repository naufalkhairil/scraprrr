"""
Scraper modules for Scraprrr.

This package contains domain-specific scraper implementations.
"""

from scraprrr.modules.flight import (
    FlightScraper,
    FlightSearchResult,
    FlightTicket,
    scrape_flights,
)
from scraprrr.modules.hotel import (
    HotelScraper,
    HotelSearchResult,
    Hotel,
    scrape_hotels,
)

__all__ = [
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
