"""
Tests for Traveloka hotel scraper models.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from traveloka_hotel_scraper.models import (
    Hotel,
    HotelLocation,
    HotelSearchResult,
    HotelScraperConfig,
)


class TestHotelModel:
    """Test Hotel model."""

    def test_create_hotel_minimal(self):
        """Test creating a hotel with minimal required fields."""
        hotel = Hotel(
            hotel_name="Test Hotel",
            location="Test Location",
        )
        assert hotel.hotel_name == "Test Hotel"
        assert hotel.location == "Test Location"
        assert hotel.star_rating is None
        assert hotel.price is None

    def test_create_hotel_full(self):
        """Test creating a hotel with all fields."""
        hotel = Hotel(
            hotel_name="Grand Hotel",
            location="Jakarta",
            star_rating=5,
            rating_score="9.2/10",
            review_count="1,234 reviews",
            main_image_url="https://example.com/image.jpg",
            supporting_images=["https://example.com/img1.jpg"],
            original_price="Rp 2.000.000",
            price="Rp 1.500.000",
            total_price="Total Rp 1.800.000",
            booking_info="Booked 10 times",
            hotel_type="Hotels",
            ranking="No. 1 in Jakarta",
            features=["Pool", "Spa", "Gym"],
        )
        assert hotel.hotel_name == "Grand Hotel"
        assert hotel.star_rating == 5
        assert len(hotel.features) == 3
        assert hotel.supporting_images == ["https://example.com/img1.jpg"]

    def test_hotel_default_values(self):
        """Test hotel default values."""
        hotel = Hotel(hotel_name="Test", location="Test")
        assert hotel.features == []
        assert hotel.supporting_images == []
        assert hotel.extracted_at is not None
        assert isinstance(hotel.extracted_at, datetime)

    def test_hotel_star_rating_validation(self):
        """Test star rating validation."""
        # Valid star rating
        hotel = Hotel(hotel_name="Test", location="Test", star_rating=4)
        assert hotel.star_rating == 4

        # String that can be converted to int
        hotel = Hotel(hotel_name="Test", location="Test", star_rating=5)
        assert hotel.star_rating == 5

    def test_hotel_missing_required_fields(self):
        """Test validation error for missing required fields."""
        with pytest.raises(ValidationError):
            Hotel()

        with pytest.raises(ValidationError):
            Hotel(hotel_name="Test")

        with pytest.raises(ValidationError):
            Hotel(location="Test")


class TestHotelSearchResult:
    """Test HotelSearchResult model."""

    def test_create_search_result_success(self):
        """Test creating a successful search result."""
        hotels = [
            Hotel(hotel_name="Hotel 1", location="Jakarta"),
            Hotel(hotel_name="Hotel 2", location="Jakarta"),
        ]
        result = HotelSearchResult(
            location="Jakarta",
            status="success",
            total_results=2,
            hotels=hotels,
        )
        assert result.location == "Jakarta"
        assert result.status == "success"
        assert result.total_results == 2
        assert len(result.hotels) == 2

    def test_create_search_result_error(self):
        """Test creating an error search result."""
        result = HotelSearchResult(
            location="Jakarta",
            status="error",
            total_results=0,
            error_message="Search failed",
        )
        assert result.status == "error"
        assert result.error_message == "Search failed"
        assert result.hotels == []

    def test_search_result_to_dict(self):
        """Test converting search result to dictionary."""
        result = HotelSearchResult(
            location="Jakarta",
            status="success",
            total_results=0,
        )
        data = result.to_dict()
        assert data["location"] == "Jakarta"
        assert data["status"] == "success"
        assert "hotels" in data

    def test_search_result_to_dataframe_data(self):
        """Test converting search result to DataFrame format."""
        hotels = [
            Hotel(hotel_name="Hotel 1", location="Jakarta", price="Rp 500.000"),
            Hotel(hotel_name="Hotel 2", location="Jakarta", price="Rp 600.000"),
        ]
        result = HotelSearchResult(
            location="Jakarta",
            status="success",
            total_results=2,
            hotels=hotels,
        )
        df_data = result.to_dataframe_data()
        assert len(df_data) == 2
        assert df_data[0]["hotel_name"] == "Hotel 1"
        assert df_data[1]["price"] == "Rp 600.000"


class TestHotelScraperConfig:
    """Test HotelScraperConfig model."""

    def test_create_config_defaults(self):
        """Test creating config with default values."""
        config = HotelScraperConfig()
        assert config.selenium_remote_url == "http://localhost:4444/wd/hub"
        assert config.scroll_enabled is True
        assert config.max_hotels == 100
        assert config.num_scrolls == 20
        assert config.save_csv is True
        assert config.save_json is False

    def test_create_config_custom(self):
        """Test creating config with custom values."""
        config = HotelScraperConfig(
            selenium_remote_url="http://custom:4444/wd/hub",
            max_hotels=50,
            scroll_enabled=False,
            save_csv=False,
            save_json=True,
            output_dir="/tmp",
        )
        assert config.selenium_remote_url == "http://custom:4444/wd/hub"
        assert config.max_hotels == 50
        assert config.scroll_enabled is False
        assert config.save_csv is False
        assert config.save_json is True
        assert config.output_dir == "/tmp"

    def test_config_validation(self):
        """Test config field validation."""
        # Valid integer fields
        config = HotelScraperConfig(
            element_wait_timeout=30,
            scroll_timeout=120,
        )
        assert config.element_wait_timeout == 30
        assert config.scroll_timeout == 120

        # Float field
        config = HotelScraperConfig(scroll_pause=3.5)
        assert config.scroll_pause == 3.5


class TestHotelLocation:
    """Test HotelLocation model."""

    def test_create_location(self):
        """Test creating a hotel location."""
        location = HotelLocation(address="Jl. Test No. 123", city="Jakarta")
        assert location.address == "Jl. Test No. 123"
        assert location.city == "Jakarta"

    def test_create_location_optional_city(self):
        """Test creating location without city."""
        location = HotelLocation(address="Jl. Test No. 123")
        assert location.address == "Jl. Test No. 123"
        assert location.city is None
