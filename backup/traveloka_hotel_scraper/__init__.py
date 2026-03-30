"""
Backward compatibility layer for traveloka_hotel_scraper.

This module re-exports from the new scraprrr package structure
to maintain compatibility with existing code.
"""

# Re-export models
from scraprrr.modules.hotel.models import (
    Hotel,
    HotelSearchResult,
    HotelScraperConfig,
)

# Re-export scraper
from scraprrr.modules.hotel.scraper import HotelScraper as TravelokaHotelScraper
from scraprrr.modules.hotel.scraper import scrape_hotels as scrape_traveloka_hotels
from scraprrr.modules.hotel.scraper import scrape_hotels

# Re-export config
from scraprrr.core.utils import generate_output_filename, save_to_csv, save_to_json

# Re-export CLI
from traveloka_hotel_scraper.cli import main

__all__ = [
    "Hotel",
    "HotelSearchResult",
    "HotelScraperConfig",
    "TravelokaHotelScraper",
    "scrape_traveloka_hotels",
    "scrape_hotels",
    "generate_output_filename",
    "save_to_csv",
    "save_to_json",
    "main",
]
