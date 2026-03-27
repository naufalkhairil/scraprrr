"""
Flight data extractor for Traveloka search results.
"""

import logging
from typing import Any, Dict, List, Optional

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

logger = logging.getLogger(__name__)


class FlightExtractor:
    """Extractor for flight ticket information from Traveloka search results."""

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
        """Extract ticket information from a flight card container."""
        try:
            ticket_info: Dict[str, Any] = {}

            airline_img = ticket_container.find_element(By.CSS_SELECTOR, self._AIRLINE_LOGO_IMG)
            ticket_info["airline_logo"] = airline_img.get_attribute("src")

            airline_name_elem = ticket_container.find_element(By.CSS_SELECTOR, self._AIRLINE_NAME_DIV)
            ticket_info["airline_name"] = airline_name_elem.text.strip()

            baggage_elem = ticket_container.find_element(By.CSS_SELECTOR, self._BAGGAGE_SVG)
            ticket_info["baggage"] = baggage_elem.text.strip()

            departure_container = ticket_container.find_element(By.CSS_SELECTOR, self._DEPARTURE_CONTAINER)
            departure_elems = departure_container.find_elements(By.CSS_SELECTOR, "div[dir='auto']")
            if len(departure_elems) >= 2:
                ticket_info["departure_time"] = departure_elems[0].text.strip()
                ticket_info["departure_airport"] = departure_elems[1].text.strip()

            arrival_container = ticket_container.find_element(By.CSS_SELECTOR, self._ARRIVAL_CONTAINER)
            arrival_elems = arrival_container.find_elements(By.CSS_SELECTOR, "div[dir='auto']")
            if len(arrival_elems) >= 2:
                ticket_info["arrival_time"] = arrival_elems[0].text.strip()
                ticket_info["arrival_airport"] = arrival_elems[1].text.strip()

            duration_elem = ticket_container.find_element(By.CSS_SELECTOR, self._DURATION_DIV)
            ticket_info["duration"] = duration_elem.text.strip()

            flight_type_elem = ticket_container.find_element(By.CSS_SELECTOR, self._FLIGHT_TYPE_DIV)
            ticket_info["flight_type"] = flight_type_elem.text.strip()

            price_elem = ticket_container.find_element(By.CSS_SELECTOR, self._PRICE_LABEL)
            ticket_info["price"] = price_elem.text.strip()

            ticket_info["original_price"] = self._extract_original_price(ticket_container)
            ticket_info["promos"] = self._extract_promos(ticket_container)
            ticket_info["special_tag"] = self._extract_special_tag(ticket_container)
            ticket_info["highlight_label"] = self._extract_highlight_label(ticket_container)

            return ticket_info

        except (NoSuchElementException, IndexError) as e:
            logger.error(f"Error extracting ticket: {e}")
            return None

    def _extract_original_price(self, container: WebElement) -> Optional[str]:
        try:
            elem = container.find_element(By.CSS_SELECTOR, self._ORIGINAL_PRICE_DIV)
            return elem.text.strip()
        except NoSuchElementException:
            return None

    def _extract_promos(self, container: WebElement) -> List[str]:
        try:
            promo_container = container.find_element(By.CSS_SELECTOR, self._PROMO_CONTAINER)
            promo_elems = promo_container.find_elements(By.CSS_SELECTOR, self._PROMO_PILL)
            return [promo.text.strip() for promo in promo_elems if promo.text.strip()]
        except NoSuchElementException:
            return []

    def _extract_special_tag(self, container: WebElement) -> Optional[str]:
        try:
            elem = container.find_element(By.CSS_SELECTOR, self._SPECIAL_TAG_SVG)
            return elem.text.strip()
        except NoSuchElementException:
            return None

    def _extract_highlight_label(self, container: WebElement) -> Optional[str]:
        try:
            elem = container.find_element(By.CSS_SELECTOR, self._HIGHLIGHT_LABEL)
            return elem.text.strip()
        except NoSuchElementException:
            return None

    def extract_all(self, ticket_containers: List[WebElement]) -> List[Dict[str, Any]]:
        """Extract information from multiple ticket containers."""
        tickets = []
        for container in ticket_containers:
            ticket_info = self.extract(container)
            if ticket_info:
                tickets.append(ticket_info)
        return tickets
