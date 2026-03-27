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
        return self

    def dismiss_guest_popup(self) -> bool:
        """Dismiss guest browse popup if present."""
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, self._GUEST_BROWSE_BUTTON))
            )
            element.click()
            return True
        except TimeoutException:
            return False

    def _select_airport(self, airport_code: str, airport_name: str) -> bool:
        """Select airport from dropdown."""
        data_testid = f"item_nimbus-autocomplete-airport-{airport_code.lower()}"
        try:
            elem = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"[data-testid='{data_testid}']"))
            )
            elem.click()
            return True
        except TimeoutException:
            pass

        try:
            elem = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{airport_name}')]"))
            )
            elem.click()
            return True
        except TimeoutException:
            pass

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

        try:
            # Set departure
            departure_elem = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._DEPARTURE_CONTAINER))
            )
            departure_elem.click()
            time.sleep(2)

            origin_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._ORIGIN_INPUT))
            )
            origin_input.send_keys(departure_code)
            time.sleep(2)

            if not self._select_airport(departure_code, departure_name):
                return False

            # Set destination
            destination_elem = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._DESTINATION_CONTAINER))
            )
            destination_elem.click()
            time.sleep(2)

            dest_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self._DESTINATION_INPUT))
            )
            dest_input.send_keys(destination_code)
            time.sleep(2)

            if not self._select_airport(destination_code, destination_name):
                return False

            # Click search
            search_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._SEARCH_BUTTON))
            )
            search_button.click()

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
        return self.driver.find_elements(By.CSS_SELECTOR, self._TICKET_CONTAINER)

    def scroll_to_load_more(
        self,
        scroll_pause: float = 2.0,
        timeout: int = 60,
        max_tickets: int = 0,
    ) -> int:
        """Scroll to load more tickets."""
        import time

        last_count = 0
        no_change_count = 0
        max_no_change = 3

        start_time = time.time()
        scroll_container = self._get_scroll_container()

        while True:
            if time.time() - start_time > timeout:
                break

            if scroll_container:
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight;",
                    scroll_container,
                )
            else:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(scroll_pause)

            current_count = len(self.get_ticket_containers())

            if max_tickets > 0 and current_count >= max_tickets:
                break

            if current_count == last_count:
                no_change_count += 1
                if no_change_count >= max_no_change:
                    break
            else:
                no_change_count = 0

            last_count = current_count

        return len(self.get_ticket_containers())

    def _get_scroll_container(self) -> Optional[WebElement]:
        """Get the scrollable container element."""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, self._SCROLL_CONTAINER)
        except Exception:
            return None
