"""
Tests for Traveloka Flight Scraper extractor.
"""

from unittest.mock import MagicMock

from traveloka_flight_scraper.extractor import TicketExtractor


class TestTicketExtractor:
    """Tests for TicketExtractor class."""

    def test_extract_basic_info(self):
        """Test extracting basic ticket information."""
        # Create mock ticket container
        container = MagicMock()

        # Setup mock return values for find_element calls
        airline_img = MagicMock()
        airline_img.get_attribute.return_value = "https://example.com/logo.png"

        airline_name = MagicMock()
        airline_name.text = "Garuda Indonesia"

        baggage = MagicMock()
        baggage.text = "20 kg"

        departure_container = MagicMock()
        dep_elem1 = MagicMock()
        dep_elem1.text = "08:00"
        dep_elem2 = MagicMock()
        dep_elem2.text = "CGK"
        departure_container.find_elements.return_value = [dep_elem1, dep_elem2]

        arrival_container = MagicMock()
        arr_elem1 = MagicMock()
        arr_elem1.text = "10:30"
        arr_elem2 = MagicMock()
        arr_elem2.text = "DPS"
        arrival_container.find_elements.return_value = [arr_elem1, arr_elem2]

        duration = MagicMock()
        duration.text = "2h 30m"

        flight_type = MagicMock()
        flight_type.text = "Direct"

        price = MagicMock()
        price.text = "Rp 1.500.000"

        # Configure container to return mocks in sequence
        # Need to include optional fields that raise NoSuchElementException
        from selenium.common.exceptions import NoSuchElementException

        container.find_element.side_effect = [
            airline_img,  # airline_logo
            airline_name,  # airline_name
            baggage,  # baggage
            departure_container,  # departure info
            arrival_container,  # arrival info
            duration,  # duration
            flight_type,  # flight_type
            price,  # price
            NoSuchElementException(),  # original_price
            NoSuchElementException(),  # promo_container
            NoSuchElementException(),  # special_tag
            NoSuchElementException(),  # highlight_label
        ]

        extractor = TicketExtractor()
        result = extractor.extract(container)

        assert result is not None
        assert result["airline_logo"] == "https://example.com/logo.png"
        assert result["airline_name"] == "Garuda Indonesia"
        assert result["baggage"] == "20 kg"
        assert result["departure_time"] == "08:00"
        assert result["departure_airport"] == "CGK"
        assert result["arrival_time"] == "10:30"
        assert result["arrival_airport"] == "DPS"
        assert result["duration"] == "2h 30m"
        assert result["flight_type"] == "Direct"
        assert result["price"] == "Rp 1.500.000"

    def test_extract_with_optional_fields(self):
        """Test extracting ticket with optional fields."""
        container = MagicMock()

        # Setup all required elements
        airline_img = MagicMock()
        airline_img.get_attribute.return_value = "https://example.com/logo.png"
        airline_name = MagicMock()
        airline_name.text = "AirAsia"
        baggage = MagicMock()
        baggage.text = "0 kg"

        departure_container = MagicMock()
        departure_container.find_elements.return_value = [
            MagicMock(text="12:00"),
            MagicMock(text="SIN"),
        ]

        arrival_container = MagicMock()
        arrival_container.find_elements.return_value = [
            MagicMock(text="14:00"),
            MagicMock(text="CGK"),
        ]

        duration = MagicMock()
        duration.text = "2h"
        flight_type = MagicMock()
        flight_type.text = "Direct"
        price = MagicMock()
        price.text = "$150.00"

        # Original price element exists
        original_price = MagicMock()
        original_price.text = "$200.00"

        # Promo container with promos
        promo_container = MagicMock()
        promo1 = MagicMock()
        promo1.text = "Member Discount"
        promo2 = MagicMock()
        promo2.text = ""
        promo_container.find_elements.return_value = [promo1, promo2]

        # Special tag
        special_tag = MagicMock()
        special_tag.text = "Bigger Discount"

        # Highlight label
        highlight = MagicMock()
        highlight.text = "Cheapest"

        container.find_element.side_effect = [
            airline_img,
            airline_name,
            baggage,
            departure_container,
            arrival_container,
            duration,
            flight_type,
            price,
            original_price,  # _extract_original_price
            promo_container,  # _extract_promos
            special_tag,  # _extract_special_tag
            highlight,  # _extract_highlight_label
        ]

        extractor = TicketExtractor()
        result = extractor.extract(container)

        assert result is not None
        assert result["original_price"] == "$200.00"
        assert result["promos"] == ["Member Discount"]
        assert result["special_tag"] == "Bigger Discount"
        assert result["highlight_label"] == "Cheapest"

    def test_extract_missing_optional_fields(self):
        """Test extracting ticket when optional fields are missing."""
        from selenium.common.exceptions import NoSuchElementException

        container = MagicMock()

        # Setup required elements
        airline_img = MagicMock()
        airline_img.get_attribute.return_value = "https://example.com/logo.png"
        airline_name = MagicMock()
        airline_name.text = "Lion Air"
        baggage = MagicMock()
        baggage.text = "20 kg"

        departure_container = MagicMock()
        departure_container.find_elements.return_value = [
            MagicMock(text="06:00"),
            MagicMock(text="CGK"),
        ]

        arrival_container = MagicMock()
        arrival_container.find_elements.return_value = [
            MagicMock(text="08:00"),
            MagicMock(text="DPS"),
        ]

        duration = MagicMock()
        duration.text = "2h"
        flight_type = MagicMock()
        flight_type.text = "Direct"
        price = MagicMock()
        price.text = "Rp 800.000"

        # Optional elements raise NoSuchElementException
        container.find_element.side_effect = [
            airline_img,
            airline_name,
            baggage,
            departure_container,
            arrival_container,
            duration,
            flight_type,
            price,
            NoSuchElementException(),  # original_price
            NoSuchElementException(),  # promo_container
            NoSuchElementException(),  # special_tag
            NoSuchElementException(),  # highlight_label
        ]

        extractor = TicketExtractor()
        result = extractor.extract(container)

        assert result is not None
        assert result["original_price"] is None
        assert result["promos"] == []
        assert result["special_tag"] is None
        assert result["highlight_label"] is None

    def test_extract_all(self):
        """Test extracting multiple tickets."""
        extractor = TicketExtractor()

        # Mock extract method
        container1 = MagicMock()
        container2 = MagicMock()

        extractor.extract = MagicMock(
            side_effect=[
                {"airline_name": "Garuda", "price": "Rp 1.000.000"},
                {"airline_name": "AirAsia", "price": "Rp 800.000"},
            ]
        )

        results = extractor.extract_all([container1, container2])

        assert len(results) == 2
        assert results[0]["airline_name"] == "Garuda"
        assert results[1]["airline_name"] == "AirAsia"

    def test_extract_failure_returns_none(self):
        """Test that extraction failure returns None."""
        from selenium.common.exceptions import NoSuchElementException

        container = MagicMock()
        container.find_element.side_effect = NoSuchElementException()

        extractor = TicketExtractor()
        result = extractor.extract(container)

        assert result is None
