"""
Backward compatibility layer for traveloka_flight_scraper.

This module re-exports from the new scraprrr package structure
to maintain compatibility with existing code.
"""

# Re-export models
from scraprrr.modules.flight.models import (
    AirportInfo,
    FlightInfo,
    FlightTicket,
    FlightSearchResult,
    FlightScraperConfig as ScraperConfig,
)

# Re-export scraper
from scraprrr.modules.flight.scraper import FlightScraper as TravelokaScraper
from scraprrr.modules.flight.scraper import scrape_flights as scrape_traveloka_flights
from scraprrr.modules.flight.scraper import scrape_flights

# Re-export config
from scraprrr.core.utils import generate_output_filename, save_to_csv, save_to_json

# Re-export CLI
from traveloka_flight_scraper.cli import main

__all__ = [
    "AirportInfo",
    "FlightInfo",
    "FlightTicket",
    "FlightSearchResult",
    "ScraperConfig",
    "TravelokaScraper",
    "scrape_traveloka_flights",
    "scrape_flights",
    "generate_output_filename",
    "save_to_csv",
    "save_to_json",
    "main",
]
