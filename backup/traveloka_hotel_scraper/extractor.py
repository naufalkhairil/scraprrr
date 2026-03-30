"""
Hotel data extraction from Traveloka search results.

This module provides functionality to extract structured hotel information
from Selenium WebElement containers representing hotel cards.
"""

import logging
from typing import Any, Dict, List, Optional

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class HotelParser:
    """Parser for hotel information from Traveloka search results."""

    # CSS Selectors for hotel information
    _HOTEL_NAME = "[data-testid='tvat-hotelName']"
    _RATING_SCORE = "[data-testid='tvat-ratingScore']"
    _REVIEW_COUNT = "div[data-testid='tvat-ratingScore'] + div"
    _STAR_RATING = "[data-id='tvat-starRating']"
    _LOCATION = "[data-testid='tvat-hotelLocation']"
    _MAIN_IMAGE = "[data-testid='list-view-card-main-image']"
    _ORIGINAL_PRICE = "[data-testid='tvat-originalPrice']"
    _HOTEL_PRICE = "[data-testid='tvat-hotelPrice']"
    _TOTAL_PRICE = "[data-testid='charged-rooms-label']"
    _BOOKING_INFO = "[data-testid='fomo-text']"
    _HOTEL_TYPE_BADGE = "div[data-testid='tvat-hotelLocation'] img + div"
    _RANKING_BADGE = "div[dir='auto'][style*='background-image']"
    _FEATURE_BADGES = "[data-testid='hotel-feature-badge-0']"
    _SUPPORTING_IMAGES = "[data-testid='list-view-card-supporting-image']"

    def parse(self, hotel_container: WebElement) -> Optional[Dict[str, Any]]:
        """
        Parse hotel information from a hotel card container element.

        Args:
            hotel_container: Selenium WebElement containing the hotel card.

        Returns:
            Dictionary with hotel information or None if parsing fails.
        """
        try:
            logger.debug("Starting hotel parsing...")
            hotel_info: Dict[str, Any] = {}

            # Extract hotel name
            hotel_name_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._HOTEL_NAME
            )
            hotel_info["hotel_name"] = (
                hotel_name_elem.text.strip() if hotel_name_elem else None
            )
            logger.debug(f"Hotel: {hotel_info.get('hotel_name')}")

            # Extract rating score
            rating_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._RATING_SCORE
            )
            hotel_info["rating_score"] = (
                rating_elem.text.strip() if rating_elem else None
            )

            # Extract review count
            review_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._REVIEW_COUNT
            )
            hotel_info["review_count"] = (
                self._extract_review_count(review_elem) if review_elem else None
            )

            # Extract star rating
            star_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._STAR_RATING
            )
            hotel_info["star_rating"] = (
                self._extract_star_rating(star_elem) if star_elem else None
            )

            # Extract location
            location_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._LOCATION
            )
            hotel_info["location"] = (
                location_elem.text.strip() if location_elem else None
            )

            # Extract main image URL
            main_image_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._MAIN_IMAGE
            )
            hotel_info["main_image_url"] = (
                main_image_elem.get_attribute("src") if main_image_elem else None
            )

            # Extract supporting images URLs
            hotel_info["supporting_images"] = self._extract_supporting_images(
                hotel_container
            )

            # Extract original price
            original_price_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._ORIGINAL_PRICE
            )
            hotel_info["original_price"] = (
                original_price_elem.text.strip() if original_price_elem else None
            )

            # Extract current price
            price_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._HOTEL_PRICE
            )
            hotel_info["price"] = price_elem.text.strip() if price_elem else None

            # Extract total price (with taxes)
            total_price_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._TOTAL_PRICE
            )
            hotel_info["total_price"] = (
                total_price_elem.text.strip() if total_price_elem else None
            )

            # Extract booking info (e.g., "Booked 8 times")
            booking_info_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._BOOKING_INFO
            )
            hotel_info["booking_info"] = (
                booking_info_elem.text.strip() if booking_info_elem else None
            )

            # Extract hotel type (e.g., "Hotels")
            hotel_type_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._HOTEL_TYPE_BADGE
            )
            hotel_info["hotel_type"] = (
                hotel_type_elem.text.strip() if hotel_type_elem else None
            )

            # Extract ranking badge (e.g., "No. 5 in Hotel with City View")
            ranking_elem = self._safe_find_element(
                hotel_container, By.CSS_SELECTOR, self._RANKING_BADGE
            )
            hotel_info["ranking"] = ranking_elem.text.strip() if ranking_elem else None

            # Extract feature badges (e.g., "Express check-out")
            hotel_info["features"] = self._extract_features(hotel_container)

            logger.debug(
                f"Parsed hotel: {hotel_info.get('hotel_name')} - {hotel_info.get('price')}"
            )
            return hotel_info

        except Exception as e:
            logger.error(f"Error parsing hotel info: {e}")
            return None

    def _safe_find_element(
        self, container: WebElement, by: By, selector: str
    ) -> Optional[WebElement]:
        """Safely find an element, returning None if not found."""
        try:
            return container.find_element(by, selector)
        except NoSuchElementException:
            return None

    def _extract_review_count(self, element: WebElement) -> Optional[str]:
        """Extract review count from element text (e.g., '(3,4K reviews)')."""
        if element:
            text = element.text.strip()
            return text.strip("()") if text else None
        return None

    def _extract_star_rating(self, element: WebElement) -> Optional[int]:
        """Extract star rating from data-rating attribute."""
        if element:
            rating = element.get_attribute("data-rating")
            try:
                return int(rating) if rating else None
            except ValueError:
                return None
        return None

    def _extract_supporting_images(
        self, hotel_container: WebElement
    ) -> List[str]:
        """Extract URLs of supporting images."""
        try:
            image_elems = hotel_container.find_elements(
                By.CSS_SELECTOR, self._SUPPORTING_IMAGES
            )
            return [
                img.get_attribute("src")
                for img in image_elems
                if img.get_attribute("src")
            ]
        except Exception as e:
            logger.debug(f"Error extracting supporting images: {e}")
            return []

    def _extract_features(self, hotel_container: WebElement) -> List[str]:
        """Extract hotel feature badges."""
        try:
            # Find all feature badge elements
            badge_elems = hotel_container.find_elements(
                By.CSS_SELECTOR, "[data-testid^='hotel-feature-badge-']"
            )
            features = []
            for badge in badge_elems:
                text = badge.text.strip()
                if text:
                    features.append(text)
            return features
        except Exception as e:
            logger.debug(f"Error extracting features: {e}")
            return []

    def parse_all(
        self, hotel_containers: List[WebElement], show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Parse information from multiple hotel containers.

        Args:
            hotel_containers: List of WebElement hotel containers.
            show_progress: Whether to show progress information.

        Returns:
            List of dictionaries with hotel information.
        """
        total = len(hotel_containers)
        logger.info(f"Parsing data from {total} hotel containers...")

        hotels = []
        for i, container in enumerate(hotel_containers, 1):
            hotel_info = self.parse(container)
            if hotel_info:
                hotels.append(hotel_info)

            if show_progress and total > 0:
                percent = (i / total) * 100 if total > 0 else 0
                print(
                    f"\rParsing hotels: {i}/{total} ({percent:.1f}%)",
                    end="",
                    flush=True,
                )

        if show_progress and total > 0:
            print()  # New line after completion

        logger.info(f"Successfully parsed {len(hotels)}/{total} hotels")
        return hotels
