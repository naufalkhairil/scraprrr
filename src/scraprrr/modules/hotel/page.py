"""
Page Object for Traveloka hotel search.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class HotelPage:
    """Page Object for Traveloka hotel search."""

    URL = "https://www.traveloka.com/en-id/hotel"

    _SEARCH_INPUT = "input[placeholder*='city' i], input[placeholder*='hotel' i]"
    _SUGGESTION_ITEM_NAME = "[data-testid='autocomplete-item-name']"
    _SEARCH_BUTTON = "[data-testid='hotel-search-button']"
    _HOTEL_SECTION = "[data-testid='hotel-results-section']"
    _HOTEL_CONTAINER = "[data-testid^='hotel-card']"
    _SCROLL_CONTAINER = ".css-1dbjc4n.r-14lw9ot.r-1pi2tsx"
    _LOADING_INDICATOR = "//*[contains(text(), 'Loading') or contains(text(), 'Searching')]"

    def __init__(self, driver: WebDriver, timeout: int = 15):
        self.driver = driver
        self.timeout = timeout

    def open(self) -> "HotelPage":
        """Navigate to Traveloka hotel page."""
        logger.info(f"Navigating to: {self.URL}")
        self.driver.get(self.URL)
        return self

    def search(self, location: str) -> bool:
        """Search for hotels in a location."""
        try:
            search_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._SEARCH_INPUT))
            )
            search_input.clear()
            search_input.send_keys(location)
            logger.debug(f"Entered location: {location}")
            time.sleep(2)

            # Select first suggestion
            try:
                suggestion = WebDriverWait(self.driver, self.timeout).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, self._SUGGESTION_ITEM_NAME)
                    )
                )
                suggestion.click()
                logger.debug("Selected autocomplete suggestion")
                time.sleep(1)
            except TimeoutException:
                pass

            search_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._SEARCH_BUTTON))
            )
            search_button.click()

            return True

        except Exception as e:
            logger.error(f"Hotel search failed: {e}")
            return False

    def wait_for_hotels(self, timeout: Optional[int] = None) -> bool:
        """Wait for hotel results to load."""
        timeout = timeout or self.timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._HOTEL_SECTION))
            )
            return True
        except TimeoutException:
            containers = self.get_hotel_containers()
            return len(containers) > 0

    def get_hotel_containers(self) -> List[WebElement]:
        """Get all hotel container elements."""
        return self.driver.find_elements(By.CSS_SELECTOR, self._HOTEL_CONTAINER)

    def get_all_hotels(
        self,
        scroll: bool = True,
        scroll_timeout: int = 60,
        num_scrolls: int = 20,
        num_hotels: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get all hotels by scrolling."""
        from scraprrr.modules.hotel.extractor import HotelExtractor

        extractor = HotelExtractor()
        last_count = 0
        no_change_count = 0

        start_time = time.time()
        scroll_container = self._get_scroll_container()

        while True:
            if time.time() - start_time > scroll_timeout:
                break

            if scroll and scroll_container:
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;",
                    scroll_container,
                )
                time.sleep(2)

            containers = self.get_hotel_containers()
            current_count = len(containers)

            if num_hotels > 0 and current_count >= num_hotels:
                break

            if current_count == last_count:
                no_change_count += 1
                if no_change_count >= 3:
                    break
            else:
                no_change_count = 0

            last_count = current_count

        containers = self.get_hotel_containers()
        if num_hotels > 0:
            containers = containers[:num_hotels]

        return extractor.extract_all(containers)

    def _get_scroll_container(self) -> Optional[WebElement]:
        """Get the scrollable container element."""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, self._SCROLL_CONTAINER)
        except Exception:
            return None
