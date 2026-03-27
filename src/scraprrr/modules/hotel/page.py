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
    _SEARCH_BUTTON = "[data-testid='search-submit-button']"
    _HOTEL_SEARCH_LIST_ITEM = "[data-testid='tvat-searchListItem']"

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
            logger.info(f"Hotel search initiated for: {location}")
            return True

        except Exception as e:
            logger.error(f"Hotel search failed: {e}")
            return False

    def wait_for_hotels(self, timeout: Optional[int] = None) -> bool:
        """Wait for hotel results to load."""
        timeout = timeout or self.timeout
        logger.debug(f"Waiting for hotel results (timeout: {timeout}s)...")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._HOTEL_SEARCH_LIST_ITEM))
            )
            logger.debug("Hotel results loaded")
            return True
        except TimeoutException:
            logger.warning("Hotel results not found within timeout")
            containers = self.get_hotel_containers()
            return len(containers) > 0

    def get_hotel_containers(self) -> List[WebElement]:
        """Get all hotel container elements."""
        containers = self.driver.find_elements(By.CSS_SELECTOR, self._HOTEL_SEARCH_LIST_ITEM)
        logger.debug(f"Found {len(containers)} hotel containers")
        return containers

    def scroll_to_load_more(
        self,
        scroll_pause: float = 2.0,
        num_hotels: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Scroll through the hotel list to load more hotels, then parse all at once.

        First collects all hotel containers by scrolling, then parses them
        after the threshold is reached to avoid repeated parsing during scroll.

        Args:
            scroll_pause: Time to wait between scrolls in seconds.
            num_hotels: Target number of hotels to collect (default: 100).

        Returns:
            List of parsed hotel information dictionaries.
        """
        from scraprrr.modules.hotel.extractor import HotelExtractor

        logger.info(f"Starting scroll to load hotels (target: {num_hotels})")

        # Hotel store variables - outside while loop for threshold check
        all_containers: List[WebElement] = []
        last_count = 0
        no_change_count = 0
        max_no_change = 3  # Stop if no new hotels loaded after this many scrolls
        scroll_iteration = 0

        # Phase 1: Scroll to collect containers
        logger.info("Phase 1: Scrolling to load hotel containers...")

        while True:
            scroll_iteration += 1
            logger.debug(f"=== Scroll iteration {scroll_iteration} ===")

            # Get current containers
            current_containers = self.get_hotel_containers()
            current_count = len(current_containers)
            logger.debug(f"Current hotel count: {current_count} (previous: {last_count})")

            # Update container list
            all_containers = current_containers

            # Check if threshold reached
            if current_count >= num_hotels:
                logger.info(f"Threshold {num_hotels} hotels reached ({current_count} containers loaded)")
                print(f"Scroll {scroll_iteration}: {current_count} hotels loaded (threshold reached)")
                break

            # Scroll to bottom of the window
            logger.debug("Executing scroll: window.scrollTo(0, document.body.scrollHeight)")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.debug("Scroll executed successfully")

            # Wait for new content to load
            logger.debug(f"Waiting {scroll_pause}s for new content to load...")
            time.sleep(scroll_pause)
            logger.debug("Wait complete")

            # Wait for network to be idle (helps with lazy-loaded content)
            logger.debug("Waiting for network idle...")
            try:
                self.driver.execute_script("""
                    return new Promise((resolve) => {
                        let pending = 0;
                        const origFetch = window.fetch;
                        window.fetch = function(...args) {
                            pending++;
                            return origFetch.apply(this, args).finally(() => {
                                pending--;
                                if (pending === 0) resolve();
                            });
                        };
                        if (pending === 0) resolve();
                        setTimeout(() => resolve(), 1000);
                    });
                """)
                logger.debug("Network idle wait complete")
            except Exception as e:
                logger.debug(f"Network idle wait skipped: {e}")

            # Check if no new hotels loaded
            new_current_count = len(self.get_hotel_containers())
            if new_current_count == current_count:
                no_change_count += 1
                logger.debug(f"No new hotels loaded (attempt {no_change_count}/{max_no_change})")
                if no_change_count >= max_no_change:
                    logger.info(f"No new hotels loaded after {no_change_count} attempts, stopping scroll")
                    print(f"Stopping scroll: No new hotels after {no_change_count} attempts")
                    break
            else:
                no_change_count = 0
                logger.info(f"Scroll {scroll_iteration}: {new_current_count} hotels loaded")
                print(f"Scroll {scroll_iteration}: {new_current_count} hotels loaded")

            last_count = new_current_count

        logger.info(f"Scrolling complete. Total containers collected: {len(all_containers)}")

        # Phase 2: Parse all containers at once
        logger.info(f"Phase 2: Parsing {len(all_containers)} hotel containers...")
        print(f"Parsing {len(all_containers)} hotels...")

        extractor = HotelExtractor()
        all_hotels: List[Dict[str, Any]] = []
        seen_hotel_keys: set = set()

        # Parse with progress bar
        total = len(all_containers)
        for i, container in enumerate(all_containers, 1):
            hotel_info = extractor.extract(container)
            if hotel_info:
                hotel_key = hotel_info.get("hotel_name")
                if hotel_key and hotel_key not in seen_hotel_keys:
                    seen_hotel_keys.add(hotel_key)
                    all_hotels.append(hotel_info)

            # Progress bar
            percent = (i / total) * 100
            bar_length = 40
            filled_length = int(bar_length * i // total)
            bar = "█" * filled_length + "-" * (bar_length - filled_length)
            print(f"\rParsing hotels: |{bar}| {i}/{total} ({percent:.1f}%) - {len(all_hotels)} unique", end="", flush=True)

        print()  # New line after progress bar
        logger.info(f"Parsing complete. Total unique hotels: {len(all_hotels)}")
        print(f"Complete: {len(all_hotels)} unique hotels parsed")

        return all_hotels

    def get_all_hotels(
        self,
        scroll: bool = True,
        scroll_timeout: int = 60,
        num_hotels: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get all hotels from the search results page with scroll and parse in one flow.

        This function follows the pattern:
        1. Wait for hotels to load
        2. Scroll to load more hotels (if enabled) - parses incrementally during scroll
        3. Returns all parsed hotels

        Args:
            scroll: Whether to scroll to load more hotels.
            scroll_timeout: Maximum time in seconds to scroll.
            num_hotels: Target number of hotels to collect.

        Returns:
            List of hotel information dictionaries.
        """
        try:
            # Wait for hotel cards to load
            WebDriverWait(self.driver, scroll_timeout).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self._HOTEL_SEARCH_LIST_ITEM)
                )
            )

            # Scroll to load more hotels if enabled
            if scroll:
                logger.info("Scrolling to load all hotels...")
                hotels = self.scroll_to_load_more(
                    num_hotels=num_hotels,
                )
                return hotels

            # If no scrolling, just parse current visible hotels
            hotel_containers = self.get_hotel_containers()
            logger.info(f"Found {len(hotel_containers)} hotel containers")

            # Parse hotels
            from scraprrr.modules.hotel.extractor import HotelExtractor
            extractor = HotelExtractor()
            hotels = extractor.extract_all(hotel_containers)
            return hotels

        except Exception as e:
            logger.error(f"Error getting hotels: {e}")
            return []
