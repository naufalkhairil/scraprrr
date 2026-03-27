"""
Flight ticket data extraction from Traveloka search results.

This module provides functionality to extract structured flight ticket information
from Selenium WebElement containers representing flight cards.
"""

import logging
import sys
from typing import Any, Dict, List, Optional

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class ProgressBar:
    """Simple text-based progress bar for ticket extraction."""

    def __init__(self, total: int, prefix: str = "Progress", length: int = 40):
        """
        Initialize the progress bar.

        Args:
            total: Total number of items.
            prefix: Prefix text for the progress bar.
            length: Length of the progress bar in characters.
        """
        self.total = total
        self.prefix = prefix
        self.length = length
        self.current = 0

    def update(self, current: int) -> None:
        """
        Update the progress bar.

        Args:
            current: Current item number.
        """
        self.current = current
        percent = (current / self.total) * 100 if self.total > 0 else 0
        filled_length = int(self.length * current // self.total) if self.total > 0 else 0
        bar = "█" * filled_length + "-" * (self.length - filled_length)
        sys.stdout.write(f"\r{self.prefix}: |{bar}| {current}/{self.total} ({percent:.1f}%)")
        if current >= self.total:
            sys.stdout.write("\n")
        sys.stdout.flush()

    def finish(self) -> None:
        """Complete the progress bar."""
        self.update(self.total)


class TicketExtractor:
    """Extractor for flight ticket information from Traveloka search results."""

    # CSS Selectors for ticket information
    _AIRLINE_LOGO_IMG = "img[src*='imagekit']"
    _AIRLINE_NAME_DIV = "div[dir='auto'].css-cens5h"
    _BAGGAGE_SVG = "svg[data-id='IcFacilitiesBaggageEmpty'] + div"
    _DEPARTURE_CONTAINER = "div.r-1habvwh.r-eqz5dr.r-9aw3ui.r-knv0ih"
    _ARRIVAL_CONTAINER = "div.r-obd0qt.r-eqz5dr.r-9aw3ui.r-knv0ih:not(.r-ggk5by)"
    _DURATION_DIV = "div.r-1awozwy.r-eqz5dr.r-knv0ih.r-bnwqim div[dir='auto']"
    _FLIGHT_TYPE_DIV = "div.r-1awozwy.r-6koalj.r-18u37iz.r-kc8jnq div[dir='auto']"
    _PRICE_LABEL = "[data-testid='label_fl_inventory_price']"
    _ORIGINAL_PRICE_DIV = "div.r-142tt33[dir='auto']"
    _PROMO_CONTAINER = "[data-testid='view-flight-card-bundle-promo-labels-container']"
    _PROMO_PILL = "[data-testid^='flight-promo-label-pill']"
    _SPECIAL_TAG_SVG = "svg[data-id='IcSystemTagFill12'] + div"
    _HIGHLIGHT_LABEL = "div[data-testid='fpr_inventory_card_neonContainerized'] div[dir='auto']"

    def extract(self, ticket_container: WebElement) -> Optional[Dict[str, Any]]:
        """
        Extract ticket information from a flight card container element.

        Args:
            ticket_container: Selenium WebElement containing the flight card.

        Returns:
            Dictionary with ticket information or None if extraction fails.
        """
        try:
            logger.debug("Starting ticket extraction...")
            ticket_info: Dict[str, Any] = {}

            # Extract airline logo and name
            airline_img = ticket_container.find_element(
                By.CSS_SELECTOR, self._AIRLINE_LOGO_IMG
            )
            ticket_info["airline_logo"] = airline_img.get_attribute("src")

            airline_name_elem = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._AIRLINE_NAME_DIV,
            )
            ticket_info["airline_name"] = airline_name_elem.text.strip()
            logger.debug(f"Airline: {ticket_info['airline_name']}")

            # Extract baggage allowance
            baggage_elem = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._BAGGAGE_SVG,
            )
            ticket_info["baggage"] = baggage_elem.text.strip()

            # Extract departure time and airport
            departure_container = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._DEPARTURE_CONTAINER,
            )
            departure_elems = departure_container.find_elements(
                By.CSS_SELECTOR,
                "div[dir='auto']",
            )
            if len(departure_elems) >= 2:
                ticket_info["departure_time"] = departure_elems[0].text.strip()
                ticket_info["departure_airport"] = departure_elems[1].text.strip()

            # Extract arrival time and airport
            arrival_container = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._ARRIVAL_CONTAINER,
            )
            arrival_elems = arrival_container.find_elements(
                By.CSS_SELECTOR,
                "div[dir='auto']",
            )
            if len(arrival_elems) >= 2:
                ticket_info["arrival_time"] = arrival_elems[0].text.strip()
                ticket_info["arrival_airport"] = arrival_elems[1].text.strip()

            # Extract duration
            duration_elem = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._DURATION_DIV,
            )
            ticket_info["duration"] = duration_elem.text.strip()

            # Extract flight type (Direct/Transit)
            flight_type_elem = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._FLIGHT_TYPE_DIV,
            )
            ticket_info["flight_type"] = flight_type_elem.text.strip()

            # Extract price
            price_elem = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._PRICE_LABEL,
            )
            ticket_info["price"] = price_elem.text.strip()

            # Extract original price if exists
            ticket_info["original_price"] = self._extract_original_price(
                ticket_container
            )

            # Extract promo labels
            ticket_info["promos"] = self._extract_promos(ticket_container)

            # Extract special tags
            ticket_info["special_tag"] = self._extract_special_tag(ticket_container)

            # Extract highlight label
            ticket_info["highlight_label"] = self._extract_highlight_label(
                ticket_container
            )

            logger.debug(f"Ticket extracted: {ticket_info['airline_name']} - {ticket_info['price']}")
            return ticket_info

        except (NoSuchElementException, IndexError) as e:
            logger.error(f"Error extracting ticket info: {e}")
            return None

    def _extract_original_price(
        self, ticket_container: WebElement
    ) -> Optional[str]:
        """Extract original (strikethrough) price if available."""
        try:
            original_price_elem = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._ORIGINAL_PRICE_DIV,
            )
            return original_price_elem.text.strip()
        except NoSuchElementException:
            return None

    def _extract_promos(self, ticket_container: WebElement) -> List[str]:
        """Extract promo labels from ticket."""
        try:
            promo_container = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._PROMO_CONTAINER,
            )
            promo_elems = promo_container.find_elements(
                By.CSS_SELECTOR,
                self._PROMO_PILL,
            )
            return [
                promo.text.strip()
                for promo in promo_elems
                if promo.text.strip()
            ]
        except NoSuchElementException:
            return []

    def _extract_special_tag(
        self, ticket_container: WebElement
    ) -> Optional[str]:
        """Extract special tag (e.g., 'Bigger Discount') if available."""
        try:
            special_tag_elem = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._SPECIAL_TAG_SVG,
            )
            return special_tag_elem.text.strip()
        except NoSuchElementException:
            return None

    def _extract_highlight_label(
        self, ticket_container: WebElement
    ) -> Optional[str]:
        """Extract 'Cheapest' or 'Best flight' label if available."""
        try:
            highlight_elem = ticket_container.find_element(
                By.CSS_SELECTOR,
                self._HIGHLIGHT_LABEL,
            )
            return highlight_elem.text.strip()
        except NoSuchElementException:
            return None

    def extract_all(
        self, ticket_containers: List[WebElement], show_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract information from multiple ticket containers.

        Args:
            ticket_containers: List of WebElement ticket containers.
            show_progress: Whether to show progress bar.

        Returns:
            List of dictionaries with ticket information.
        """
        total = len(ticket_containers)
        logger.info(f"Extracting data from {total} ticket containers...")
        
        if show_progress and total > 0:
            progress_bar = ProgressBar(total, prefix="Extracting tickets")
        
        tickets = []
        for i, container in enumerate(ticket_containers, 1):
            ticket_info = self.extract(container)
            if ticket_info:
                tickets.append(ticket_info)
            
            if show_progress and total > 0:
                progress_bar.update(i)
        
        logger.info(f"Successfully extracted {len(tickets)}/{total} tickets")
        return tickets
