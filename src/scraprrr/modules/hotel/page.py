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
        Scroll through the hotel list and parse results incrementally.

        Parses hotels after each scroll to avoid losing data when elements
        are recycled during infinite scroll.

        Args:
            scroll_pause: Time to wait between scrolls in seconds.
            num_hotels: Target number of hotels to collect (default: 100).

        Returns:
            List of parsed hotel information dictionaries.
        """
        from scraprrr.modules.hotel.extractor import HotelExtractor

        logger.info(f"Starting scroll to load hotels (target: {num_hotels})")

        all_hotels: List[Dict[str, Any]] = []
        seen_hotel_keys: set = set()
        last_count = 0
        no_change_count = 0
        max_no_change = 3
        scroll_iteration = 0

        extractor = HotelExtractor()

        # Parse initial hotels before scrolling
        logger.info("Parsing initial hotels...")
        initial_containers = self.get_hotel_containers()
        total_initial = len(initial_containers)
        print(f"Parsing initial hotels...")

        for i, container in enumerate(initial_containers, 1):
            hotel_info = extractor.extract(container)
            if hotel_info:
                hotel_key = hotel_info.get("hotel_name")
                if hotel_key and hotel_key not in seen_hotel_keys:
                    seen_hotel_keys.add(hotel_key)
                    all_hotels.append(hotel_info)

            # Progress bar for initial parsing
            percent = (i / total_initial) * 100
            bar_length = 30
            filled = int(bar_length * i // total_initial)
            bar = "█" * filled + "─" * (bar_length - filled)
            print(f"\r  |{bar}| {i}/{total_initial} ({percent:.0f}%) - {len(all_hotels)} unique", end="", flush=True)

        print()
        logger.info(f"Initial load: {len(all_hotels)} unique hotels")
        print(f"Initial: {len(all_hotels)} hotels\n")

        # Scroll and parse incrementally
        while True:
            scroll_iteration += 1
            logger.debug(f"=== Scroll iteration {scroll_iteration} ===")

            # Check if threshold reached
            if len(all_hotels) >= num_hotels:
                logger.info(f"Threshold {num_hotels} hotels reached ({len(all_hotels)} collected)")
                print(f"✓ Threshold reached: {len(all_hotels)} hotels collected")
                break

            # Scroll to bottom
            logger.debug("Scrolling to bottom...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new content
            time.sleep(scroll_pause)

            # Wait for network idle
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
            except Exception:
                pass

            # Count current hotels
            current_count = len(self.get_hotel_containers())
            logger.debug(f"Current hotels: {current_count} (previous: {last_count})")

            # Check if no new hotels
            if current_count == last_count:
                no_change_count += 1
                logger.debug(f"No change ({no_change_count}/{max_no_change})")
                if no_change_count >= max_no_change:
                    logger.info(f"Stopping: No new hotels after {no_change_count} attempts")
                    print(f"✗ Stopping: No new hotels after {no_change_count} attempts")
                    break
            else:
                no_change_count = 0
                logger.info(f"Scroll {scroll_iteration}: {current_count} hotels visible")
                print(f"Scroll {scroll_iteration}: {current_count} hotels visible")

                # Parse current hotels with progress bar
                current_containers = self.get_hotel_containers()
                total_current = len(current_containers)
                new_count = 0

                print(f"  Parsing hotels...")
                for i, container in enumerate(current_containers, 1):
                    hotel_info = extractor.extract(container)
                    if hotel_info:
                        hotel_key = hotel_info.get("hotel_name")
                        if hotel_key and hotel_key not in seen_hotel_keys:
                            seen_hotel_keys.add(hotel_key)
                            all_hotels.append(hotel_info)
                            new_count += 1

                    # Progress bar for current scroll parsing
                    percent = (i / total_current) * 100
                    bar_length = 30
                    filled = int(bar_length * i // total_current)
                    bar = "█" * filled + "─" * (bar_length - filled)
                    print(f"\r  |{bar}| {i}/{total_current} ({percent:.0f}%) - {len(all_hotels)} unique", end="", flush=True)

                print()

                if new_count > 0:
                    logger.info(f"Added {new_count} new hotels, total: {len(all_hotels)}")
                    print(f"  +{new_count} new hotels (total: {len(all_hotels)})\n")
                else:
                    print(f"  No new unique hotels\n")

            last_count = current_count

        logger.info(f"Scroll complete. Total unique hotels: {len(all_hotels)}")
        print(f"\n✓ Complete: {len(all_hotels)} unique hotels collected")

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
