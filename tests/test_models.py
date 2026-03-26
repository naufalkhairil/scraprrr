"""
Tests for Traveloka Flight Scraper models.
"""

from datetime import datetime

import pytest

from traveloka_flight_scraper.models import (
    AirportInfo,
    FlightInfo,
    FlightSearchResult,
    FlightTicket,
    ScraperConfig,
)


class TestAirportInfo:
    """Tests for AirportInfo model."""

    def test_create_airport_info(self):
        """Test creating an AirportInfo instance."""
        airport = AirportInfo(code="CGK", name="Soekarno Hatta International Airport")
        assert airport.code == "CGK"
        assert airport.name == "Soekarno Hatta International Airport"

    def test_airport_info_validation(self):
        """Test that AirportInfo requires both fields."""
        with pytest.raises(Exception):
            AirportInfo(code="CGK")


class TestFlightTicket:
    """Tests for FlightTicket model."""

    def test_create_flight_ticket(self, sample_flight_ticket):
        """Test creating a FlightTicket instance."""
        assert sample_flight_ticket.airline_name == "Garuda Indonesia"
        assert sample_flight_ticket.departure_airport == "CGK"
        assert sample_flight_ticket.arrival_airport == "DPS"
        assert sample_flight_ticket.price == "Rp 1.500.000"
        assert sample_flight_ticket.promos == ["Member Discount"]

    def test_flight_ticket_optional_fields(self, sample_ticket_data):
        """Test FlightTicket with optional fields."""
        # Remove optional fields
        del sample_ticket_data["original_price"]
        del sample_ticket_data["special_tag"]
        del sample_ticket_data["highlight_label"]
        del sample_ticket_data["promos"]

        ticket = FlightTicket(**sample_ticket_data)
        assert ticket.original_price is None
        assert ticket.special_tag is None
        assert ticket.highlight_label is None
        assert ticket.promos == []

    def test_flight_ticket_default_timestamp(self, sample_ticket_data):
        """Test that FlightTicket has a default timestamp."""
        before = datetime.now()
        ticket = FlightTicket(**sample_ticket_data)
        after = datetime.now()

        assert before <= ticket.extracted_at <= after

    def test_flight_ticket_invalid_data(self, sample_ticket_data):
        """Test FlightTicket validation with invalid data."""
        # Remove required field
        del sample_ticket_data["price"]

        with pytest.raises(Exception):
            FlightTicket(**sample_ticket_data)


class TestFlightSearchResult:
    """Tests for FlightSearchResult model."""

    def test_create_search_result(self, sample_flight_ticket):
        """Test creating a FlightSearchResult instance."""
        result = FlightSearchResult(
            origin=AirportInfo(code="CGK", name="Soekarno Hatta"),
            destination=AirportInfo(code="DPS", name="Ngurah Rai"),
            status="success",
            total_results=1,
            tickets=[sample_flight_ticket],
        )

        assert result.status == "success"
        assert result.total_results == 1
        assert result.origin.code == "CGK"
        assert result.destination.code == "DPS"

    def test_search_result_to_dict(self, sample_flight_ticket):
        """Test converting search result to dictionary."""
        result = FlightSearchResult(
            origin=AirportInfo(code="CGK", name="Soekarno Hatta"),
            destination=AirportInfo(code="DPS", name="Ngurah Rai"),
            status="success",
            total_results=1,
            tickets=[sample_flight_ticket],
        )

        data = result.to_dict()
        assert data["status"] == "success"
        assert data["total_results"] == 1
        assert "tickets" in data

    def test_search_result_to_dataframe_data(self, sample_flight_ticket):
        """Test converting search result to DataFrame-compatible data."""
        result = FlightSearchResult(
            origin=AirportInfo(code="CGK", name="Soekarno Hatta"),
            destination=AirportInfo(code="DPS", name="Ngurah Rai"),
            status="success",
            total_results=1,
            tickets=[sample_flight_ticket],
        )

        data = result.to_dataframe_data()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["airline_name"] == "Garuda Indonesia"

    def test_search_result_error_status(self):
        """Test search result with error status."""
        result = FlightSearchResult(
            origin=AirportInfo(code="CGK", name="Soekarno Hatta"),
            destination=AirportInfo(code="DPS", name="Ngurah Rai"),
            status="error",
            total_results=0,
            error_message="Failed to load results",
        )

        assert result.status == "error"
        assert result.error_message == "Failed to load results"


class TestScraperConfig:
    """Tests for ScraperConfig model."""

    def test_default_config(self):
        """Test default ScraperConfig values."""
        config = ScraperConfig()

        assert config.selenium_remote_url == "http://localhost:4444/wd/hub"
        assert config.scroll_enabled is True
        assert config.save_csv is True
        assert config.save_json is False
        assert config.output_dir == "."

    def test_custom_config(self):
        """Test ScraperConfig with custom values."""
        config = ScraperConfig(
            selenium_remote_url="http://custom:4444/wd/hub",
            scroll_enabled=False,
            save_csv=False,
            save_json=True,
            output_dir="/tmp/results",
        )

        assert config.selenium_remote_url == "http://custom:4444/wd/hub"
        assert config.scroll_enabled is False
        assert config.save_json is True
        assert config.output_dir == "/tmp/results"
