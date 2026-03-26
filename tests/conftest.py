"""
Pytest fixtures for Traveloka Flight Scraper tests.
"""

import pytest

from traveloka_flight_scraper.models import FlightTicket, ScraperConfig


@pytest.fixture
def sample_ticket_data():
    """Sample flight ticket data for testing."""
    return {
        "airline_name": "Garuda Indonesia",
        "airline_logo": "https://example.com/logo.png",
        "departure_time": "08:00",
        "departure_airport": "CGK",
        "arrival_time": "10:30",
        "arrival_airport": "DPS",
        "duration": "2h 30m",
        "flight_type": "Direct",
        "price": "Rp 1.500.000",
        "original_price": "Rp 2.000.000",
        "baggage": "20 kg",
        "promos": ["Member Discount"],
        "special_tag": "Bigger Discount",
        "highlight_label": "Cheapest",
    }


@pytest.fixture
def sample_flight_ticket(sample_ticket_data):
    """Sample FlightTicket instance for testing."""
    return FlightTicket(**sample_ticket_data)


@pytest.fixture
def default_scraper_config():
    """Default ScraperConfig for testing."""
    return ScraperConfig(
        selenium_remote_url="http://localhost:4444/wd/hub",
        scroll_enabled=False,
        save_csv=False,
        save_json=False,
    )
