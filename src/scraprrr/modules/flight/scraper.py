"""
Flight scraper implementation for Traveloka.com.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from selenium.webdriver.remote.webdriver import WebDriver

from scraprrr.core.base import BaseScraper
from scraprrr.core.utils import generate_output_filename, save_to_csv, save_to_json
from scraprrr.modules.flight.models import (
    AirportInfo,
    FlightSearchResult,
    FlightTicket,
    FlightScraperConfig,
)

logger = logging.getLogger(__name__)


class FlightScraper(BaseScraper[FlightSearchResult]):
    """
    Scraper for Traveloka flight data.

    Example:
        ```python
        with FlightScraper() as scraper:
            result = scraper.search(origin="CGK", destination="DPS")
            print(f"Found {result.total_results} flights")
        ```
    """

    def __init__(self, config: Optional[FlightScraperConfig] = None):
        """Initialize the FlightScraper."""
        super().__init__(config or FlightScraperConfig())
        self.config: FlightScraperConfig

    def search(
        self,
        origin: str,
        destination: str,
        origin_name: Optional[str] = None,
        destination_name: Optional[str] = None,
        save_results: bool = True,
    ) -> FlightSearchResult:
        """
        Search for flights between origin and destination.

        Args:
            origin: Origin airport IATA code.
            destination: Destination airport IATA code.
            origin_name: Origin airport name (auto-resolved if None).
            destination_name: Destination airport name (auto-resolved if None).
            save_results: Whether to save results to files.

        Returns:
            FlightSearchResult containing search status and ticket data.
        """
        logger.info(f"Starting flight search: {origin} → {destination}")

        if not self._is_initialized:
            raise RuntimeError("Scraper not initialized. Call initialize() first.")

        search_timestamp = datetime.now()

        try:
            # Import page objects here to avoid circular imports
            from scraprrr.modules.flight.page import FlightPage

            # Navigate and search
            flight_page = FlightPage(self.driver, self.config.element_wait_timeout)
            flight_page.open()

            search_success = flight_page.search(
                departure_code=origin,
                departure_name=origin_name,
                destination_code=destination,
                destination_name=destination_name,
            )

            if not search_success:
                return FlightSearchResult(
                    origin=AirportInfo(code=origin, name=origin_name or f"{origin} Airport"),
                    destination=AirportInfo(code=destination, name=destination_name or f"{destination} Airport"),
                    search_timestamp=search_timestamp,
                    status="error",
                    total_results=0,
                    error_message="Failed to perform search",
                )

            # Wait for results
            time.sleep(10)

            if not flight_page.wait_for_results():
                return FlightSearchResult(
                    origin=AirportInfo(code=origin, name=origin_name or f"{origin} Airport"),
                    destination=AirportInfo(code=destination, name=destination_name or f"{destination} Airport"),
                    search_timestamp=search_timestamp,
                    status="error",
                    total_results=0,
                    error_message="No results found within timeout",
                )

            # Scroll if enabled
            if self.config.scroll_enabled:
                flight_page.scroll_to_load_more(
                    scroll_pause=self.config.scroll_pause,
                    timeout=self.config.scroll_timeout,
                    max_tickets=self.config.max_tickets,
                )
                time.sleep(2)

            # Extract tickets
            from scraprrr.modules.flight.extractor import FlightExtractor

            extractor = FlightExtractor()
            ticket_containers = flight_page.get_ticket_containers()
            raw_tickets = extractor.extract_all(ticket_containers)

            # Create FlightTicket objects
            tickets = self._create_flight_tickets(raw_tickets)

            result = FlightSearchResult(
                origin=AirportInfo(code=origin, name=origin_name or f"{origin} Airport"),
                destination=AirportInfo(code=destination, name=destination_name or f"{destination} Airport"),
                search_timestamp=search_timestamp,
                status="success",
                total_results=len(tickets),
                tickets=tickets,
                raw_data={"raw_tickets": raw_tickets},
            )

            logger.info(f"Search completed: {len(tickets)} flights found")

            if save_results:
                self.save_results(result, origin, destination)

            return result

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return FlightSearchResult(
                origin=AirportInfo(code=origin, name=origin_name or f"{origin} Airport"),
                destination=AirportInfo(code=destination, name=destination_name or f"{destination} Airport"),
                search_timestamp=search_timestamp,
                status="error",
                total_results=0,
                error_message=str(e),
            )

    def _create_flight_tickets(self, raw_tickets: List[Dict[str, Any]]) -> List[FlightTicket]:
        """Convert raw ticket dictionaries to FlightTicket objects."""
        tickets = []
        for raw in raw_tickets:
            try:
                ticket = FlightTicket(**raw)
                tickets.append(ticket)
            except Exception as e:
                logger.warning(f"Failed to validate ticket: {e}")
        return tickets

    def save_results(
        self,
        result: FlightSearchResult,
        origin: str,
        destination: str,
    ) -> None:
        """Save search results to files."""
        timestamp = result.search_timestamp
        files_saved = []

        if self.config.save_csv and result.tickets:
            csv_path = generate_output_filename(
                prefix="trave_flight_tickets",
                extension="csv",
                output_dir=self.config.output_dir,
                timestamp=timestamp,
                origin=origin,
                destination=destination,
            )
            save_to_csv(result.to_dataframe_data(), csv_path)
            files_saved.append(("CSV", csv_path))

        if self.config.save_json:
            json_path = generate_output_filename(
                prefix="trave_flight_tickets",
                extension="json",
                output_dir=self.config.output_dir,
                timestamp=timestamp,
                origin=origin,
                destination=destination,
            )
            save_to_json(result.to_dict(), json_path)
            files_saved.append(("JSON", json_path))

        if files_saved:
            logger.info(f"Saved {len(files_saved)} file(s)")
            for file_type, file_path in files_saved:
                logger.info(f"  - {file_type}: {file_path}")


def scrape_flights(
    origin: str,
    destination: str,
    selenium_url: str = "http://localhost:4444/wd/hub",
) -> FlightSearchResult:
    """
    Convenience function to scrape flights without managing scraper lifecycle.

    Args:
        origin: Origin airport IATA code.
        destination: Destination airport IATA code.
        selenium_url: URL of Selenium Grid server.

    Returns:
        FlightSearchResult containing search results.
    """
    config = FlightScraperConfig(selenium_remote_url=selenium_url)
    with FlightScraper(config) as scraper:
        return scraper.search(origin=origin, destination=destination)
