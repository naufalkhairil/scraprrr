"""
Pytest fixtures for Scraprrr tests.
"""

import pytest

from scraprrr.modules.flight.models import FlightTicket, FlightScraperConfig
from scraprrr.modules.hotel.models import Hotel, HotelScraperConfig
from scraprrr.core.utils import ScraperConfig


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
def sample_hotel_data():
    """Sample hotel data for testing."""
    return {
        "hotel_name": "Mercure Jakarta",
        "location": "Gatot Subroto, South Jakarta",
        "star_rating": 4,
        "rating_score": "8.8/10",
        "review_count": "Very Good",
        "price": "Rp 990.000",
        "total_price": "Total Rp 1.197.900 for 1 room",
        "booking_info": "Booked 8 times",
        "hotel_type": "Hotels",
        "features": ["Express check-out", "Fitness center"],
    }


@pytest.fixture
def sample_hotel(sample_hotel_data):
    """Sample Hotel instance for testing."""
    return Hotel(**sample_hotel_data)


@pytest.fixture
def default_scraper_config():
    """Default ScraperConfig for testing."""
    return ScraperConfig(
        selenium_remote_url="http://localhost:4444/wd/hub",
        scroll_enabled=False,
        save_csv=False,
        save_json=False,
    )


@pytest.fixture
def default_flight_scraper_config():
    """Default FlightScraperConfig for testing."""
    return FlightScraperConfig(
        selenium_remote_url="http://localhost:4444/wd/hub",
        scroll_enabled=False,
        save_csv=False,
        save_json=False,
    )


@pytest.fixture
def default_hotel_scraper_config():
    """Default HotelScraperConfig for testing."""
    return HotelScraperConfig(
        selenium_remote_url="http://localhost:4444/wd/hub",
        scroll_enabled=False,
        save_csv=False,
        save_json=False,
    )
