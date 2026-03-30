"""
Hotel scraper module for Scraprrr.

This module provides hotel scraping functionality for Traveloka.com.
"""

from scraprrr.modules.hotel.models import (
    Hotel,
    HotelSearchResult,
    HotelScraperConfig,
)
from scraprrr.modules.hotel.scraper import HotelScraper, scrape_hotels

__all__ = [
    "Hotel",
    "HotelSearchResult",
    "HotelScraperConfig",
    "HotelScraper",
    "scrape_hotels",
]
