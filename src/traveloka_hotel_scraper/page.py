"""
Page Object Model for Traveloka hotel website interactions.

This module provides classes that encapsulate the structure and interactions
of specific pages on Traveloka.com hotel search, following the Page Object Model pattern.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from traveloka_hotel_scraper.extractor import HotelParser

logger = logging.getLogger(__name__)


class TravelokaHotelPage:
    """Page Object for Traveloka hotel search page."""

    URL = "https://www.traveloka.com/en-id/hotel"

    # Locators
    _SEARCH_INPUT = "input[placeholder='City, hotel, place to go']"
    _AUTOCOMPLETE_ITEM_NAME = "[data-testid='autocomplete-item-name']"
    _SEARCH_SUBMIT_BUTTON = "[data-testid='search-submit-button']"
    _HOTEL_SEARCH_LIST_ITEM = "[data-testid='tvat-searchListItem']"

    def __init__(self, driver: WebDriver, timeout: int = 15):
        """
        Initialize the HotelPage.

        Args:
            driver: Selenium WebDriver instance.
            timeout: Default timeout for element waits in seconds.
        """
        self.driver = driver
        self.timeout = timeout
        self.parser = HotelParser()

    def open(self) -> "TravelokaHotelPage":
        """
        Navigate to the Traveloka hotel page.

        Returns:
            Self for method chaining.
        """
        logger.info(f"Navigating to Traveloka hotel page: {self.URL}")
        self.driver.get(self.URL)
        logger.debug("Hotel page loaded")
        return self

    def search_hotel(
        self,
        location: str,
    ) -> bool:
        """
        Search for hotels by location.

        Args:
            location: City, hotel, or place name to search.

        Returns:
            True if search was initiated successfully, False otherwise.
        """
        logger.info(f"Searching hotels in: {location}")
        try:
            # Enter location in search bar
            search_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self._SEARCH_INPUT)
                )
            )
            search_input.click()
            search_input.send_keys(location)
            logger.debug(f"Entered location: {location}")

            # Wait for autocomplete suggestions
            time.sleep(2)

            # Click on first autocomplete suggestion
            autocomplete_item = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, self._AUTOCOMPLETE_ITEM_NAME)
                )
            )
            autocomplete_item.click()
            logger.debug("Selected autocomplete suggestion")

            # Wait for selection to register
            time.sleep(2)

            # Click search button
            submit_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, self._SEARCH_SUBMIT_BUTTON)
                )
            )
            submit_button.click()
            logger.info(f"Hotel search initiated for: {location}")
            return True

        except (TimeoutException, Exception) as e:
            logger.error(f"Failed to search hotels: {e}")
            return False

    def wait_for_hotels(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for hotel results to load.

        Args:
            timeout: Override timeout in seconds. Uses self.timeout if None.

        Returns:
            True if hotels are loaded, False if timeout.
        """
        effective_timeout = timeout if timeout else self.timeout
        logger.debug(f"Waiting for hotel results (timeout: {effective_timeout}s)...")
        try:
            WebDriverWait(self.driver, effective_timeout).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self._HOTEL_SEARCH_LIST_ITEM)
                )
            )
            logger.info("Hotel results loaded")
            return True
        except TimeoutException:
            logger.warning("Hotel results not found within timeout")
            return False

    def get_hotel_containers(self) -> List:
        """
        Get all hotel container elements.

        Returns:
            List of WebElement hotel containers.
        """
        containers = self.driver.find_elements(
            By.CSS_SELECTOR, self._HOTEL_SEARCH_LIST_ITEM
        )
        logger.debug(f"Found {len(containers)} hotel containers")
        return containers

    def scroll_to_load_more(
        self,
        scroll_pause: float = 2.0,
        num_scrolls: int = 20,
        num_hotels: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Scroll through the hotel list and parse results incrementally.

        Parses current hotels before each scroll to avoid losing data when elements
        are recycled during infinite scroll.

        Args:
            scroll_pause: Time to wait between scrolls in seconds.
            num_scrolls: Number of times to scroll (default: 20).
            num_hotels: Target number of hotels to collect (default: 100).

        Returns:
            List of parsed hotel information dictionaries.
        """
        all_hotels: List[Dict[str, Any]] = []
        seen_hotel_keys: set = set()
        last_count = 0
        no_change_count = 0
        max_no_change = 3  # Stop if no new hotels loaded after this many scrolls

        # Parse initial hotels before any scrolling
        logger.info("Parsing initial hotels...")
        initial_containers = self.get_hotel_containers()
        initial_hotels = self.parser.parse_all(initial_containers, show_progress=False)

        for hotel in initial_hotels:
            hotel_key = hotel.get("hotel_name")
            if hotel_key and hotel_key not in seen_hotel_keys:
                seen_hotel_keys.add(hotel_key)
                all_hotels.append(hotel)

        logger.info(f"Initial load: {len(initial_hotels)} hotels parsed, {len(all_hotels)} unique")
        print(f"Initial load: {len(all_hotels)} hotels")

        for i in range(num_scrolls):
            # Check if threshold reached
            if len(all_hotels) > num_hotels:
                logger.info(f"Threshold {num_hotels} number of hotels reached")
                break

            # Scroll to bottom of the window
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new content to load
            time.sleep(scroll_pause)

            # Wait for network to be idle (helps with lazy-loaded content)
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
                pass  # Continue even if network wait fails

            # Count current hotels
            current_count = len(self.get_hotel_containers())

            # Check if no new hotels loaded
            if current_count == last_count:
                no_change_count += 1
                if no_change_count >= max_no_change:
                    logger.info(f"No new hotels loaded after {no_change_count} attempts")
                    break
            else:
                no_change_count = 0
                logger.info(f"Scroll {i+1}/{num_scrolls}: {current_count} hotels visible")
                print(f"Scroll {i+1}/{num_scrolls}: {current_count} hotels visible")

                # Parse current visible hotels
                current_containers = self.get_hotel_containers()
                current_hotels = self.parser.parse_all(current_containers, show_progress=False)

                # Add only new unique hotels
                new_count = 0
                for hotel in current_hotels:
                    hotel_key = hotel.get("hotel_name")
                    if hotel_key and hotel_key not in seen_hotel_keys:
                        seen_hotel_keys.add(hotel_key)
                        all_hotels.append(hotel)
                        new_count += 1

                if new_count > 0:
                    logger.info(f"Added {new_count} new hotels, total: {len(all_hotels)}")
                    print(f"Added {new_count} new hotels, total: {len(all_hotels)}")

            last_count = current_count

        logger.info(f"Scrolling complete. Total unique hotels parsed: {len(all_hotels)}")
        return all_hotels

    def get_all_hotels(
        self,
        scroll: bool = True,
        scroll_timeout: int = 60,
        num_scrolls: int = 20,
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
            num_scrolls: Number of times to scroll.
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
                    num_scrolls=num_scrolls,
                    num_hotels=num_hotels,
                )
                return hotels

            # If no scrolling, just parse current visible hotels
            hotel_containers = self.get_hotel_containers()
            logger.info(f"Found {len(hotel_containers)} hotel containers")

            # Parse hotels
            hotels = self.parser.parse_all(hotel_containers)
            return hotels

        except Exception as e:
            logger.error(f"Error getting hotels: {e}")
            return []
