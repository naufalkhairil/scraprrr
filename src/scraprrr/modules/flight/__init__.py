"""
Flight scraper module for Scraprrr.

This module provides flight scraping functionality for Traveloka.com.
"""

from scraprrr.modules.flight.models import (
    AirportInfo,
    FlightInfo,
    FlightTicket,
    FlightSearchResult,
    FlightScraperConfig,
)
from scraprrr.modules.flight.scraper import FlightScraper, scrape_flights

__all__ = [
    "AirportInfo",
    "FlightInfo",
    "FlightTicket",
    "FlightSearchResult",
    "FlightScraperConfig",
    "FlightScraper",
    "scrape_flights",
]
