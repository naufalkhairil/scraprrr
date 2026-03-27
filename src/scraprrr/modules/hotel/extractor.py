"""
Hotel data extractor for Traveloka search results.
"""

import logging
from typing import Any, Dict, List, Optional

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class HotelExtractor:
    """Parser for hotel information from Traveloka search results."""

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

    def extract(self, hotel_container: WebElement) -> Optional[Dict[str, Any]]:
        """Parse hotel information from a hotel card container."""
        try:
            hotel_info: Dict[str, Any] = {}

            hotel_name_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._HOTEL_NAME)
            hotel_info["hotel_name"] = hotel_name_elem.text.strip() if hotel_name_elem else None

            rating_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._RATING_SCORE)
            hotel_info["rating_score"] = rating_elem.text.strip() if rating_elem else None

            review_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._REVIEW_COUNT)
            hotel_info["review_count"] = self._extract_review_count(review_elem) if review_elem else None

            star_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._STAR_RATING)
            hotel_info["star_rating"] = self._extract_star_rating(star_elem) if star_elem else None

            location_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._LOCATION)
            hotel_info["location"] = location_elem.text.strip() if location_elem else None

            main_image_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._MAIN_IMAGE)
            hotel_info["main_image_url"] = main_image_elem.get_attribute("src") if main_image_elem else None

            hotel_info["supporting_images"] = self._extract_supporting_images(hotel_container)

            original_price_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._ORIGINAL_PRICE)
            hotel_info["original_price"] = original_price_elem.text.strip() if original_price_elem else None

            price_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._HOTEL_PRICE)
            hotel_info["price"] = price_elem.text.strip() if price_elem else None

            total_price_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._TOTAL_PRICE)
            hotel_info["total_price"] = total_price_elem.text.strip() if total_price_elem else None

            booking_info_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._BOOKING_INFO)
            hotel_info["booking_info"] = booking_info_elem.text.strip() if booking_info_elem else None

            hotel_type_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._HOTEL_TYPE_BADGE)
            hotel_info["hotel_type"] = hotel_type_elem.text.strip() if hotel_type_elem else None

            ranking_elem = self._safe_find(hotel_container, By.CSS_SELECTOR, self._RANKING_BADGE)
            hotel_info["ranking"] = ranking_elem.text.strip() if ranking_elem else None

            hotel_info["features"] = self._extract_features(hotel_container)

            return hotel_info

        except Exception as e:
            logger.error(f"Error parsing hotel: {e}")
            return None

    def _safe_find(self, container: WebElement, by: By, selector: str) -> Optional[WebElement]:
        """Safely find an element, returning None if not found."""
        try:
            return container.find_element(by, selector)
        except NoSuchElementException:
            return None

    def _extract_review_count(self, element: WebElement) -> Optional[str]:
        """Extract review count from element text."""
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

    def _extract_supporting_images(self, hotel_container: WebElement) -> List[str]:
        """Extract URLs of supporting images."""
        try:
            image_elems = hotel_container.find_elements(By.CSS_SELECTOR, self._SUPPORTING_IMAGES)
            return [img.get_attribute("src") for img in image_elems if img.get_attribute("src")]
        except Exception:
            return []

    def _extract_features(self, hotel_container: WebElement) -> List[str]:
        """Extract hotel feature badges."""
        try:
            badge_elems = hotel_container.find_elements(By.CSS_SELECTOR, "[data-testid^='hotel-feature-badge-']")
            return [badge.text.strip() for badge in badge_elems if badge.text.strip()]
        except Exception:
            return []

    def extract_all(self, hotel_containers: List[WebElement]) -> List[Dict[str, Any]]:
        """Parse information from multiple hotel containers."""
        hotels = []
        for container in hotel_containers:
            hotel_info = self.extract(container)
            if hotel_info:
                hotels.append(hotel_info)
        return hotels
