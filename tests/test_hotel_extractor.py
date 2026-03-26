"""
Tests for Traveloka hotel scraper extractor.
"""

from unittest.mock import MagicMock

from traveloka_hotel_scraper.extractor import HotelParser


class TestHotelParser:
    """Test HotelParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = HotelParser()

    def test_safe_find_element_found(self):
        """Test _safe_find_element when element is found."""
        mock_container = MagicMock()
        mock_element = MagicMock()
        mock_container.find_element.return_value = mock_element

        result = self.parser._safe_find_element(
            mock_container, "css", "[data-testid='test']"
        )

        assert result == mock_element
        mock_container.find_element.assert_called_once()

    def test_safe_find_element_not_found(self):
        """Test _safe_find_element when element is not found."""
        from selenium.common.exceptions import NoSuchElementException

        mock_container = MagicMock()
        mock_container.find_element.side_effect = NoSuchElementException()

        result = self.parser._safe_find_element(
            mock_container, "css", "[data-testid='test']"
        )

        assert result is None

    def test_extract_review_count(self):
        """Test review count extraction."""
        mock_element = MagicMock()
        mock_element.text.strip.return_value = "(3,4K reviews)"

        result = self.parser._extract_review_count(mock_element)
        assert result == "3,4K reviews"

    def test_extract_review_count_empty(self):
        """Test review count extraction with empty text."""
        mock_element = MagicMock()
        mock_element.text.strip.return_value = ""

        result = self.parser._extract_review_count(mock_element)
        assert result is None

    def test_extract_review_count_none(self):
        """Test review count extraction with None element."""
        result = self.parser._extract_review_count(None)
        assert result is None

    def test_extract_star_rating_valid(self):
        """Test star rating extraction with valid value."""
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "4"

        result = self.parser._extract_star_rating(mock_element)
        assert result == 4

    def test_extract_star_rating_invalid(self):
        """Test star rating extraction with invalid value."""
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "invalid"

        result = self.parser._extract_star_rating(mock_element)
        assert result is None

    def test_extract_star_rating_none(self):
        """Test star rating extraction with None element."""
        result = self.parser._extract_star_rating(None)
        assert result is None

    def test_extract_supporting_images(self):
        """Test supporting images extraction."""
        mock_container = MagicMock()
        mock_img1 = MagicMock()
        mock_img1.get_attribute.return_value = "https://example.com/img1.jpg"
        mock_img2 = MagicMock()
        mock_img2.get_attribute.return_value = "https://example.com/img2.jpg"
        mock_container.find_elements.return_value = [mock_img1, mock_img2]

        result = self.parser._extract_supporting_images(mock_container)
        assert result == [
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg",
        ]

    def test_extract_supporting_images_empty(self):
        """Test supporting images extraction with no images."""
        mock_container = MagicMock()
        mock_container.find_elements.return_value = []

        result = self.parser._extract_supporting_images(mock_container)
        assert result == []

    def test_extract_features(self):
        """Test feature badges extraction."""
        mock_container = MagicMock()
        mock_badge1 = MagicMock()
        mock_badge1.text.strip.return_value = "Pool"
        mock_badge2 = MagicMock()
        mock_badge2.text.strip.return_value = "Gym"
        mock_container.find_elements.return_value = [mock_badge1, mock_badge2]

        result = self.parser._extract_features(mock_container)
        assert result == ["Pool", "Gym"]

    def test_extract_features_empty(self):
        """Test feature extraction with no features."""
        mock_container = MagicMock()
        mock_container.find_elements.return_value = []

        result = self.parser._extract_features(mock_container)
        assert result == []

    def test_parse_hotel_success(self):
        """Test parsing a hotel successfully."""
        mock_container = MagicMock()

        # Mock all required elements
        def find_element_side_effect(by, selector):
            mock_elem = MagicMock()
            if "hotelName" in selector:
                mock_elem.text.strip.return_value = "Test Hotel"
            elif "ratingScore" in selector:
                mock_elem.text.strip.return_value = "8.8/10"
            elif "hotelLocation" in selector:
                mock_elem.text.strip.return_value = "Jakarta"
            elif "hotelPrice" in selector:
                mock_elem.text.strip.return_value = "Rp 500.000"
            elif "originalPrice" in selector:
                from selenium.common.exceptions import NoSuchElementException
                raise NoSuchElementException()
            elif "starRating" in selector:
                mock_elem.get_attribute.return_value = "4"
            elif "main-image" in selector:
                mock_elem.get_attribute.return_value = "https://example.com/img.jpg"
            elif "tvat-hotelLocation" in selector and "img" not in selector:
                mock_elem.text.strip.return_value = "Jakarta"
            else:
                from selenium.common.exceptions import NoSuchElementException
                raise NoSuchElementException()
            return mock_elem

        mock_container.find_element.side_effect = find_element_side_effect
        mock_container.find_elements.return_value = []

        result = self.parser.parse(mock_container)

        assert result is not None
        assert result["hotel_name"] == "Test Hotel"
        assert result["location"] == "Jakarta"
        assert result["price"] == "Rp 500.000"
        assert result["star_rating"] == 4

    def test_parse_hotel_failure(self):
        """Test parsing fails gracefully on error."""
        mock_container = MagicMock()
        mock_container.find_element.side_effect = Exception("Unexpected error")

        result = self.parser.parse(mock_container)
        assert result is None

    def test_parse_all(self):
        """Test parsing multiple hotels."""
        mock_container1 = MagicMock()
        mock_container2 = MagicMock()

        # Mock first hotel
        def find_element_side_effect1(by, selector):
            mock_elem = MagicMock()
            if "hotelName" in selector:
                mock_elem.text.strip.return_value = "Hotel 1"
            elif "hotelLocation" in selector:
                mock_elem.text.strip.return_value = "Location 1"
            elif "hotelPrice" in selector:
                mock_elem.text.strip.return_value = "Rp 500.000"
            else:
                from selenium.common.exceptions import NoSuchElementException
                raise NoSuchElementException()
            return mock_elem

        # Mock second hotel
        def find_element_side_effect2(by, selector):
            mock_elem = MagicMock()
            if "hotelName" in selector:
                mock_elem.text.strip.return_value = "Hotel 2"
            elif "hotelLocation" in selector:
                mock_elem.text.strip.return_value = "Location 2"
            elif "hotelPrice" in selector:
                mock_elem.text.strip.return_value = "Rp 600.000"
            else:
                from selenium.common.exceptions import NoSuchElementException
                raise NoSuchElementException()
            return mock_elem

        mock_container1.find_element.side_effect = find_element_side_effect1
        mock_container2.find_element.side_effect = find_element_side_effect2
        mock_container1.find_elements.return_value = []
        mock_container2.find_elements.return_value = []

        result = self.parser.parse_all(
            [mock_container1, mock_container2],
            show_progress=False,
        )

        assert len(result) == 2
        assert result[0]["hotel_name"] == "Hotel 1"
        assert result[1]["hotel_name"] == "Hotel 2"
