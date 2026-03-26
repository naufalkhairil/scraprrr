"""
Traveloka Flight Scraper - A well-structured package for scraping flight data from Traveloka.com.

This package provides a modular, maintainable approach to web scraping using Selenium,
with proper separation of concerns using the Page Object Model pattern.
"""

from traveloka_flight_scraper.scraper import TravelokaScraper
from traveloka_flight_scraper.models import (
    FlightTicket,
    FlightSearchResult,
    AirportInfo,
    FlightInfo,
)
from traveloka_flight_scraper.config import (
    get_airport_name,
    get_airport_code,
    ConfigManager,
)

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = [
    "TravelokaScraper",
    "FlightTicket",
    "FlightSearchResult",
    "AirportInfo",
    "FlightInfo",
    "get_airport_name",
    "get_airport_code",
    "ConfigManager",
]
