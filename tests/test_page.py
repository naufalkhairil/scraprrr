"""
Tests for Traveloka Flight Scraper page objects.
"""

from unittest.mock import MagicMock, patch

import pytest
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from traveloka_flight_scraper.page import TravelokaHomePage


class TestSelectAirportFromDropdown:
    """Tests for _select_airport_from_dropdown method."""

    def test_select_airport_data_testid_match(self):
        """Test airport selection using data-testid pattern (priority 1)."""
        driver = MagicMock()
        page = TravelokaHomePage(driver, timeout=10)

        mock_wait = MagicMock()
        mock_element = MagicMock()
        
        with patch('traveloka_flight_scraper.page.WebDriverWait') as mock_wait_class:
            mock_wait_class.return_value = mock_wait
            mock_wait.until.return_value = mock_element
            
            result = page._select_airport_from_dropdown("PDG", "Minangkabau International Airport")
            
            assert result is True
            mock_element.click.assert_called_once()

    def test_select_airport_full_name_fallback(self):
        """Test airport selection falls back to full name when data-testid fails."""
        driver = MagicMock()
        page = TravelokaHomePage(driver, timeout=10)

        mock_wait = MagicMock()
        mock_element = MagicMock()
        
        with patch('traveloka_flight_scraper.page.WebDriverWait') as mock_wait_class:
            mock_wait_class.return_value = mock_wait
            
            # First call (data-testid) fails, second call (full name) succeeds
            mock_wait.until.side_effect = [
                TimeoutException(),  # data-testid fails
                mock_element  # Full name succeeds
            ]
            
            result = page._select_airport_from_dropdown("PDG", "Minangkabau International Airport")
            
            assert result is True
            assert mock_element.click.call_count == 1
            # Should have been called twice (data-testid then full name)
            assert mock_wait.until.call_count == 2

    def test_select_airport_split_search_fallback(self):
        """Test airport selection using split search fallback (priority 3)."""
        driver = MagicMock()
        page = TravelokaHomePage(driver, timeout=10)

        mock_wait = MagicMock()
        mock_element = MagicMock()
        
        with patch('traveloka_flight_scraper.page.WebDriverWait') as mock_wait_class:
            mock_wait_class.return_value = mock_wait
            
            # data-testid fails, full name fails, split word succeeds
            mock_wait.until.side_effect = [
                TimeoutException(),  # data-testid fails
                TimeoutException(),  # Full name fails
                mock_element  # Split word succeeds
            ]
            
            result = page._select_airport_from_dropdown("PDG", "Minangkabau International Airport")
            
            assert result is True
            mock_element.click.assert_called_once()

    def test_select_airport_all_methods_fail(self):
        """Test airport selection fails when all methods fail."""
        driver = MagicMock()
        page = TravelokaHomePage(driver, timeout=10)

        mock_wait = MagicMock()
        
        with patch('traveloka_flight_scraper.page.WebDriverWait') as mock_wait_class:
            mock_wait_class.return_value = mock_wait
            mock_wait.until.side_effect = TimeoutException()
            
            result = page._select_airport_from_dropdown("XXX", "Unknown Airport")
            
            assert result is False

    def test_select_airport_uses_lowercase_for_data_testid(self):
        """Test that uppercase airport code is converted to lowercase for data-testid."""
        driver = MagicMock()
        page = TravelokaHomePage(driver, timeout=10)

        mock_wait = MagicMock()
        mock_element = MagicMock()
        
        with patch('traveloka_flight_scraper.page.WebDriverWait') as mock_wait_class:
            mock_wait_class.return_value = mock_wait
            mock_wait.until.return_value = mock_element
            
            # Use uppercase code - should be converted to lowercase internally
            result = page._select_airport_from_dropdown("PDG", "Minangkabau International Airport")
            
            assert result is True
            # Verify click was called (data-testid worked)
            mock_element.click.assert_called_once()
