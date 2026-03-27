"""
Page Object for Traveloka flight search.
"""

import logging
import time
from typing import List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class FlightPage:
    """Page Object for Traveloka flight search."""

    URL = "https://www.traveloka.com/en-id"

    _GUEST_BROWSE_BUTTON = "//*[contains(text(), 'Browse as a guest')]"
    _DEPARTURE_CONTAINER = "[data-testid='airport-autocomplete-container-departure']"
    _DESTINATION_CONTAINER = "[data-testid='airport-autocomplete-container-destination']"
    _SEARCH_BUTTON = "[data-testid='desktop-default-search-button']"
    _ORIGIN_INPUT = "input[placeholder='Origin']"
    _DESTINATION_INPUT = "input[placeholder='Destination']"
    _FLIGHT_LIST_SECTION = "[data-testid='view_flight_section_list']"
    _TICKET_CONTAINER = "[data-testid^='flight-inventory-card-container']"
    _SCROLL_CONTAINER = ".css-1dbjc4n.r-14lw9ot.r-1pi2tsx.r-1rnoaur"
    _LOADING_INDICATOR = "//*[starts-with(normalize-space(text()), 'Searching') or starts-with(normalize-space(text()), 'Loading')]"

    def __init__(self, driver: WebDriver, timeout: int = 15):
        self.driver = driver
        self.timeout = timeout

    def open(self) -> "FlightPage":
        """Navigate to Traveloka homepage."""
        logger.info(f"Navigating to: {self.URL}")
        self.driver.get(self.URL)
        logger.debug("Homepage loaded")
        return self

    def dismiss_guest_popup(self) -> bool:
        """Dismiss guest browse popup if present."""
        logger.debug("Looking for guest popup...")
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, self._GUEST_BROWSE_BUTTON))
            )
            element.click()
            logger.debug("Guest popup dismissed successfully")
            return True
        except TimeoutException:
            logger.debug("Guest popup not found, skipping")
            return False

    def _select_airport(self, airport_code: str, airport_name: str) -> bool:
        """Select airport from dropdown."""

        # Priority 1: Try data-testid pattern (most reliable)
        data_testid = f"item_nimbus-autocomplete-airport-{airport_code.lower()}"
        try:
            elem = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"[data-testid='{data_testid}']"))
            )
            elem.click()
            logger.debug(f"Airport selected using data-testid: {data_testid}")
            return True
        except TimeoutException:
            logger.debug(f"data-testid match failed, trying full name: {data_testid}")

        # Priority 2: Try full name match
        try:
            elem = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{airport_name}')]"))
            )
            elem.click()
            logger.debug(f"Airport selected using full name: {airport_name}")
            return True
        except TimeoutException:
            logger.debug(f"Full name match failed, trying split search: {airport_name}")
        
        logger.warning(f"Airport not found using data-testid or full name: {airport_code}")
        return False

    def search(
        self,
        departure_code: str,
        departure_name: str,
        destination_code: str,
        destination_name: str,
    ) -> bool:
        """Perform flight search."""
        self.dismiss_guest_popup()
        time.sleep(2)

        try:
            # Set departure
            logger.debug("Clicking departure container...")
            departure_elem = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._DEPARTURE_CONTAINER))
            )
            departure_elem.click()
            time.sleep(2)

            logger.debug(f"Entering airport code: {departure_code}")
            origin_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._ORIGIN_INPUT))
            )
            origin_input.send_keys(departure_code)
            time.sleep(2)

            if not self._select_airport(departure_code, departure_name):
                logger.error(f"Failed to select departure airport: {departure_code}")
                return False
            
            logger.info(f"Departure airport set: {departure_code}")

            # Set destination
            logger.debug("Clicking destination container...")
            destination_elem = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._DESTINATION_CONTAINER))
            )
            destination_elem.click()
            time.sleep(2)

            logger.debug(f"Entering airport code: {destination_code}")
            dest_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._DESTINATION_INPUT))
            )
            dest_input.send_keys(destination_code)
            time.sleep(2)

            if not self._select_airport(destination_code, destination_name):
                logger.error(f"Failed to select destination airport: {destination_code}")
                return False

            logger.info(f"Destination airport set: {destination_code}")

            # Click search
            logger.debug("Initiating flight search...")
            search_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._SEARCH_BUTTON))
            )
            search_button.click()
            logger.info("Flight search initiated successfully")
            return True

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return False

    def wait_for_results(self) -> bool:
        """Wait for flight results to load."""
        try:
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._FLIGHT_LIST_SECTION))
            )
            return True
        except TimeoutException:
            ticket_containers = self.get_ticket_containers()
            return len(ticket_containers) > 0

    def get_ticket_containers(self) -> List[WebElement]:
        """Get all flight ticket container elements."""
        containers = self.driver.find_elements(By.CSS_SELECTOR, self._TICKET_CONTAINER)
        logger.debug(f"Found {len(containers)} ticket containers")
        return containers

    def scroll_to_load_more(
        self,
        scroll_pause: float = 2.0,
        timeout: int = 60,
        max_tickets: int = 0,
    ) -> int:
        """Scroll to load more tickets."""
        import time

        logger.info(f"Starting scroll to load tickets (timeout={timeout}s, max_tickets={max_tickets})")
        
        last_count = 0
        no_change_count = 0
        max_no_change = 3
        scroll_iteration = 0

        start_time = time.time()
        scroll_container = self._get_scroll_container()
        
        logger.debug(f"Scroll container found: {scroll_container is not None}")
        if scroll_container:
            logger.debug(f"Scroll container tag: {scroll_container.tag_name}")

        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                logger.debug(f"Scroll timeout reached after {elapsed:.1f}s")
                break

            scroll_iteration += 1
            logger.debug(f"=== Scroll iteration {scroll_iteration} ===")

            # Scroll down
            if scroll_container:
                logger.debug("Executing scroll on scroll container element")
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;",
                    scroll_container,
                )
                logger.debug("Scrolled scroll container to bottom")
            else:
                logger.debug("No scroll container found, scrolling window")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                logger.debug("Scrolled window to bottom")

            # Wait for new content to load
            logger.debug(f"Waiting {scroll_pause}s for new content to load...")
            time.sleep(scroll_pause)
            logger.debug(f"Wait complete")

            # Count tickets
            current_count = len(self.get_ticket_containers())
            logger.debug(f"Current ticket count: {current_count} (previous: {last_count})")

            # Check if max_tickets threshold reached
            if max_tickets > 0 and current_count >= max_tickets:
                logger.info(f"Reached max tickets threshold ({current_count} >= {max_tickets})")
                break

            # Check if no new tickets loaded
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

        final_count = len(self.get_ticket_containers())
        logger.info(f"Scroll complete. Total tickets loaded: {final_count}")
        return final_count

    def _get_scroll_container(self) -> Optional[WebElement]:
        """Get the scrollable container element."""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, self._SCROLL_CONTAINER)
        except Exception:
            return None
