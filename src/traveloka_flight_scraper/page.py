"""
Page Object Model for Traveloka website interactions.

This module provides classes that encapsulate the structure and interactions
of specific pages on Traveloka.com, following the Page Object Model pattern.
"""

import logging
import time
from typing import Optional

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class TravelokaHomePage:
    """Page Object for Traveloka homepage."""

    URL = "https://www.traveloka.com/en-id"

    # Locators
    _GUEST_BROWSE_BUTTON = "//*[contains(text(), 'Browse as a guest')]"
    _DEPARTURE_CONTAINER = "[data-testid='airport-autocomplete-container-departure']"
    _DESTINATION_CONTAINER = "[data-testid='airport-autocomplete-container-destination']"
    _SEARCH_BUTTON = "[data-testid='desktop-default-search-button']"
    _ORIGIN_INPUT = "input[placeholder='Origin']"
    _DESTINATION_INPUT = "input[placeholder='Destination']"

    def __init__(self, driver: WebDriver, timeout: int = 10):
        """
        Initialize the HomePage.

        Args:
            driver: Selenium WebDriver instance.
            timeout: Default timeout for element waits in seconds.
        """
        self.driver = driver
        self.timeout = timeout

    def open(self) -> "TravelokaHomePage":
        """
        Navigate to the Traveloka homepage.

        Returns:
            Self for method chaining.
        """
        logger.info(f"Navigating to Traveloka homepage: {self.URL}")
        self.driver.get(self.URL)
        logger.debug("Homepage loaded")
        return self

    def dismiss_guest_popup(self) -> bool:
        """
        Click the 'Browse as a guest' button if the popup appears.

        Returns:
            True if the popup was dismissed, False if not found.
        """
        logger.debug("Looking for guest popup...")
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, self._GUEST_BROWSE_BUTTON))
            )
            element.click()
            logger.info("Guest popup dismissed successfully")
            return True
        except TimeoutException:
            logger.debug("Guest popup not found, skipping")
            return False

    def _select_airport_from_dropdown(self, airport_code: str, airport_name: str) -> bool:
        """
        Select an airport from the dropdown using data-testid, full name, or split search.

        Search priority:
        1. data-testid pattern (most reliable): item_nimbus-autocomplete-airport-<CODE>
        2. Full airport name match
        3. Split search (individual words)

        Args:
            airport_code: IATA airport code (e.g., 'PDG').
            airport_name: Full airport name (e.g., "Minangkabau International Airport").
            timeout: Wait timeout in seconds.

        Returns:
            True if airport was selected, False otherwise.
        """
        # Priority 1: Try data-testid pattern (most reliable)
        data_testid = f"item_nimbus-autocomplete-airport-{airport_code.lower()}"
        try:
            airport_element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f"[data-testid='{data_testid}']")
                )
            )
            airport_element.click()
            logger.debug(f"Airport selected using data-testid: {data_testid}")
            return True
        except (TimeoutException, NoSuchElementException):
            logger.debug(f"data-testid match failed, trying full name: {data_testid}")

        # Priority 2: Try full name match
        try:
            airport_element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//*[contains(text(), '{airport_name}')]")
                )
            )
            airport_element.click()
            logger.debug(f"Airport selected using full name: {airport_name}")
            return True
        except (TimeoutException, NoSuchElementException):
            logger.debug(f"Full name match failed, trying split search: {airport_name}")

        # Priority 3: Split search - try each word in the airport name
        words = airport_name.split()
        for word in words:
            if len(word) < 3:  # Skip very short words
                continue
            
            try:
                airport_element = WebDriverWait(self.driver, self.timeout).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//*[contains(text(), '{word}')]")
                    )
                )
                airport_element.click()
                logger.debug(f"Airport selected using split search word: '{word}'")
                return True
            except (TimeoutException, NoSuchElementException):
                logger.debug(f"Split search word '{word}' not found, trying next...")
                continue

        logger.warning(f"Airport not found using data-testid, full name, or split search: {airport_code}")
        return False

    def set_departure(self, airport_code: str, airport_name: str) -> bool:
        """
        Set the departure airport.

        Args:
            airport_code: IATA code of the airport (e.g., 'CGK').
            airport_name: Full name of the airport for selection.

        Returns:
            True if successful, False otherwise.
        """
        logger.info(f"Setting departure airport: {airport_code} - {airport_name}")
        try:
            # Click departure container
            logger.debug("Clicking departure container...")
            departure_element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._DEPARTURE_CONTAINER))
            )
            departure_element.click()

            time.sleep(2)

            # Enter airport code
            logger.debug(f"Entering airport code: {airport_code}")
            origin_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._ORIGIN_INPUT))
            )
            origin_input.send_keys(airport_code)

            time.sleep(2)

            # Select the airport from dropdown (with data-testid priority)
            if self._select_airport_from_dropdown(airport_code, airport_name):
                logger.info(f"Departure airport set: {airport_code}")
                return True
            else:
                logger.error(f"Failed to select departure airport: {airport_name}")
                return False
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Failed to set departure airport: {e}")
            return False

    def set_destination(self, airport_code: str, airport_name: str) -> bool:
        """
        Set the destination airport.

        Args:
            airport_code: IATA code of the airport (e.g., 'DPS').
            airport_name: Full name of the airport for selection.

        Returns:
            True if successful, False otherwise.
        """
        logger.info(f"Setting destination airport: {airport_code} - {airport_name}")
        try:
            # Click destination container
            logger.debug("Clicking destination container...")
            destination_element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._DESTINATION_CONTAINER))
            )
            destination_element.click()

            time.sleep(2)

            # Enter airport code
            logger.debug(f"Entering airport code: {airport_code}")
            destination_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._DESTINATION_INPUT))
            )
            destination_input.send_keys(airport_code)

            time.sleep(2)

            # Select the airport from dropdown (with data-testid priority)
            if self._select_airport_from_dropdown(airport_code, airport_name):
                logger.info(f"Destination airport set: {airport_code}")
                return True
            else:
                logger.error(f"Failed to select destination airport: {airport_name}")
                return False
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Failed to set destination airport: {e}")
            return False

    def search_flights(self) -> bool:
        """
        Click the search button to search for flights.

        Returns:
            True if successful, False otherwise.
        """
        logger.info("Initiating flight search...")
        try:
            search_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._SEARCH_BUTTON))
            )
            search_button.click()
            logger.info("Flight search initiated successfully")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Failed to initiate flight search: {e}")
            return False

    def search(
        self,
        departure_code: str,
        departure_name: str,
        destination_code: str,
        destination_name: str,
    ) -> bool:
        """
        Perform a complete flight search.

        Args:
            departure_code: Departure airport IATA code.
            departure_name: Departure airport full name.
            destination_code: Destination airport IATA code.
            destination_name: Destination airport full name.

        Returns:
            True if search was initiated successfully, False otherwise.
        """
        logger.info(f"Starting flight search: {departure_code} → {destination_code}")
        self.dismiss_guest_popup()
        if not self.set_departure(departure_code, departure_name):
            logger.error("Failed to set departure airport")
            return False
        if not self.set_destination(destination_code, destination_name):
            logger.error("Failed to set destination airport")
            return False
        if not self.search_flights():
            logger.error("Failed to initiate search")
            return False
        logger.info(f"Flight search initiated: {departure_code} → {destination_code}")
        return True


class TravelokaResultsPage:
    """Page Object for Traveloka flight results page."""

    # Locators
    _FLIGHT_LIST_SECTION = "[data-testid='view_flight_section_list']"
    _TICKET_CONTAINER = "[data-testid^='flight-inventory-card-container']"
    _SCROLL_CONTAINER = ".css-1dbjc4n.r-14lw9ot.r-1pi2tsx.r-1rnoaur"
    # Loading indicator - matches elements starting with loading-related text
    # Examples: "Searching for flights... 93%", "Loading...", "Searching..."
    _LOADING_INDICATOR = "//*[starts-with(normalize-space(text()), 'Searching') or starts-with(normalize-space(text()), 'Loading')]"

    def __init__(self, driver: WebDriver, timeout: int = 15):
        """
        Initialize the ResultsPage.

        Args:
            driver: Selenium WebDriver instance.
            timeout: Default timeout for element waits in seconds.
        """
        self.driver = driver
        self.timeout = timeout

    def wait_for_loading_indicator_to_disappear(self, timeout: int = 60) -> bool:
        """
        Wait until the loading indicator is gone.

        Waits for any element containing loading-related text to disappear.
        Catches various states like:
        - "Searching for flights... 93%"
        - "Searching for flights..."
        - "Loading..."

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            True if loading indicator disappeared, False if timeout.
        """
        logger.debug(f"Waiting for loading indicator to disappear (timeout: {timeout}s)...")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(
                    (By.XPATH, self._LOADING_INDICATOR)
                )
            )
            logger.info("Loading indicator disappeared")
            return True
        except TimeoutException:
            logger.warning("Loading indicator did not disappear within timeout")
            return False

    def wait_for_results(self) -> bool:
        """
        Wait for flight results to load.

        First tries to wait for _FLIGHT_LIST_SECTION. If not found,
        continues by checking if any _TICKET_CONTAINER elements are present.
        This allows scraping to continue even when the expected results
        section structure is not present.

        Returns:
            True if results are loaded (either section or tickets), False if nothing found.
        """
        logger.debug(f"Waiting for flight results (timeout: {self.timeout}s)...")
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self._FLIGHT_LIST_SECTION)
                )
            )
            logger.info("Flight results section loaded")
            return True
        except TimeoutException:
            logger.warning("Flight results section not found, checking for ticket containers...")
            # Fallback: check if any ticket containers are present
            ticket_containers = self.get_ticket_containers()
            if ticket_containers:
                logger.info(f"Found {len(ticket_containers)} ticket containers without flight list section")
                return True
            else:
                logger.warning("No ticket containers found either")
                return False

    def get_ticket_containers(self):
        """
        Get all flight ticket container elements.

        Returns:
            List of WebElement ticket containers.
        """
        containers = self.driver.find_elements(
            By.CSS_SELECTOR,
            self._TICKET_CONTAINER,
        )
        logger.debug(f"Found {len(containers)} ticket containers")
        return containers

    def get_scroll_container(self):
        """
        Get the scrollable container element for flight results.

        Returns:
            WebElement scroll container or None if not found.
        """
        try:
            container = self.driver.find_element(By.CSS_SELECTOR, self._SCROLL_CONTAINER)
            logger.debug("Scroll container found")
            return container
        except NoSuchElementException:
            logger.debug("Scroll container not found")
            return None

    def scroll_to_load_more(
        self,
        scroll_pause: float = 2.0,
        timeout: int = 60,
        max_tickets: int = 0,
    ) -> int:
        """
        Scroll through the page to load more flight tickets.

        Scrolls continuously until no more tickets load, timeout is reached,
        or max_tickets threshold is exceeded.

        Args:
            scroll_pause: Time to wait between scrolls in seconds.
            timeout: Maximum time in seconds to scroll.
            max_tickets: Maximum tickets threshold (0 for unlimited). 
                        Stops scrolling if ticket count exceeds this value.

        Returns:
            Number of tickets loaded.
        """
        logger.info(f"Starting scroll to load more tickets (timeout={timeout}s, max_tickets threshold={max_tickets})")
        last_count = 0
        no_change_count = 0
        max_no_change = 3

        start_time = time.time()
        scroll_container = self.get_scroll_container()
        scroll_iteration = 0

        while True:
            # Check timeout
            if time.time() - start_time > timeout:
                logger.warning(f"Scroll timeout reached after {timeout} seconds")
                break

            scroll_iteration += 1

            if scroll_container:
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;",
                    scroll_container,
                )
            else:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )

            time.sleep(scroll_pause)

            # Wait for network idle (optional)
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

            current_count = len(self.get_ticket_containers())

            # Check if we've exceeded the max_tickets threshold
            if max_tickets > 0 and current_count >= max_tickets:
                logger.info(f"Reached max tickets threshold ({current_count} >= {max_tickets}), stopping scroll")
                break

            if current_count == last_count:
                no_change_count += 1
                logger.debug(f"No new tickets loaded (attempt {no_change_count}/{max_no_change})")
                if no_change_count >= max_no_change:
                    logger.info(f"No new tickets after {no_change_count} attempts, stopping scroll")
                    break
            else:
                no_change_count = 0
                logger.info(f"Scroll {scroll_iteration}: Loaded {current_count} tickets")

            last_count = current_count

        total = len(self.get_ticket_containers())
        logger.info(f"Scroll complete. Total tickets loaded: {total}")
        return total
