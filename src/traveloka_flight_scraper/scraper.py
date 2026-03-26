"""
Main scraper orchestration for Traveloka flight data.

This module provides the TravelokaScraper class that coordinates all components
(driver, pages, extractor) to perform complete flight searches and data extraction.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from selenium.webdriver.remote.webdriver import WebDriver

from traveloka_flight_scraper.config import get_airport_name
from traveloka_flight_scraper.driver import create_driver, quit_driver
from traveloka_flight_scraper.extractor import TicketExtractor
from traveloka_flight_scraper.models import (
    AirportInfo,
    FlightSearchResult,
    FlightTicket,
    ScraperConfig,
)
from traveloka_flight_scraper.page import TravelokaHomePage, TravelokaResultsPage
from traveloka_flight_scraper.utils import (
    generate_output_filename,
    save_to_csv,
    save_to_json,
)

logger = logging.getLogger(__name__)


class TravelokaScraper:
    """
    Main scraper class for Traveloka flight data.

    This class orchestrates the complete scraping workflow:
    1. Initialize WebDriver
    2. Navigate to Traveloka homepage
    3. Set search parameters (origin, destination)
    4. Execute search
    5. Extract flight ticket data
    6. Save results

    Example:
        ```python
        scraper = TravelokaScraper()
        result = scraper.search_flights("CGK", "Soekarno Hatta", "DPS", "Ngurah Rai")
        print(f"Found {result.total_results} flights")
        scraper.close()
        ```
    """

    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the TravelokaScraper.

        Args:
            config: Optional scraper configuration. Uses defaults if not provided.
        """
        logger.info("Initializing TravelokaScraper...")
        self.config = config or ScraperConfig()
        self.driver: Optional[WebDriver] = None
        self.extractor = TicketExtractor()
        self._is_initialized = False
        logger.debug(f"Scraper config: scroll_enabled={self.config.scroll_enabled}, save_csv={self.config.save_csv}")

    def initialize(self) -> "TravelokaScraper":
        """
        Initialize the WebDriver connection.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If driver initialization fails.
        """
        if self._is_initialized:
            logger.debug("Scraper already initialized")
            return self

        logger.info("Initializing WebDriver connection...")
        try:
            self.driver = create_driver(self.config.selenium_remote_url)
            self._is_initialized = True
            logger.info("WebDriver initialized successfully")
            return self
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise RuntimeError(f"Failed to initialize WebDriver: {e}") from e

    def close(self) -> None:
        """Close the WebDriver connection."""
        if self.driver:
            logger.info("Closing WebDriver connection...")
            quit_driver(self.driver)
            self.driver = None
            self._is_initialized = False
            logger.info("WebDriver connection closed")

    def __enter__(self) -> "TravelokaScraper":
        """Context manager entry."""
        logger.debug("Entering context manager")
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        logger.debug("Exiting context manager")
        self.close()

    def search_flights(
        self,
        origin_code: str,
        origin_name: Optional[str] = None,
        destination_code: str = "",
        destination_name: Optional[str] = None,
        save_results: bool = True,
    ) -> FlightSearchResult:
        """
        Search for flights between origin and destination.

        Args:
            origin_code: Origin airport IATA code (e.g., 'CGK').
            origin_name: Origin airport name. If None, looks up from KNOWN_AIRPORTS.
            destination_code: Destination airport IATA code.
            destination_name: Destination airport name. If None, looks up from KNOWN_AIRPORTS.
            save_results: Whether to save results to files.

        Returns:
            FlightSearchResult containing search status and ticket data.

        Raises:
            RuntimeError: If scraper is not initialized.
        """
        logger.info(f"Starting flight search: {origin_code} → {destination_code}")

        if not self._is_initialized:
            logger.error("Scraper not initialized")
            raise RuntimeError("Scraper not initialized. Call initialize() first.")

        # Resolve airport names using config file
        origin_name = origin_name or get_airport_name(origin_code, f"{origin_code} Airport")
        destination_name = destination_name or get_airport_name(destination_code, f"{destination_code} Airport")
        logger.info(f"Search route: {origin_name} ({origin_code}) → {destination_name} ({destination_code})")

        search_timestamp = datetime.now()

        try:
            # Navigate to homepage and perform search
            logger.info("Navigating to Traveloka homepage...")
            home_page = TravelokaHomePage(self.driver, self.config.element_wait_timeout)
            home_page.open()

            logger.info("Performing flight search...")
            search_success = home_page.search(
                departure_code=origin_code,
                departure_name=origin_name,
                destination_code=destination_code,
                destination_name=destination_name,
            )

            if not search_success:
                logger.error("Flight search failed")
                return FlightSearchResult(
                    origin=AirportInfo(code=origin_code, name=origin_name),
                    destination=AirportInfo(
                        code=destination_code, name=destination_name
                    ),
                    search_timestamp=search_timestamp,
                    status="error",
                    total_results=0,
                    error_message="Failed to perform search",
                )

            # Wait for results page to load
            logger.info("Waiting for results page to load...")
            time.sleep(10)  # Initial wait for page load

            results_page = TravelokaResultsPage(
                self.driver, self.config.element_wait_timeout
            )

            # Wait for loading indicator to disappear before fetching tickets
            logger.info("Waiting for loading indicator to disappear...")
            if not results_page.wait_for_loading_indicator_to_disappear(
                timeout=self.config.scroll_timeout
            ):
                logger.warning("Proceeding without waiting for loading indicator")

            if not results_page.wait_for_results():
                logger.error("Flight results section not found")
                return FlightSearchResult(
                    origin=AirportInfo(code=origin_code, name=origin_name),
                    destination=AirportInfo(
                        code=destination_code, name=destination_name
                    ),
                    search_timestamp=search_timestamp,
                    status="error",
                    total_results=0,
                    error_message="No results found within timeout",
                )

            # Scroll to load more tickets if enabled
            if self.config.scroll_enabled:
                logger.info("Scrolling to load more tickets...")
                results_page.scroll_to_load_more(
                    scroll_pause=self.config.scroll_pause,
                    timeout=self.config.scroll_timeout,
                    max_tickets=self.config.max_tickets,
                )
                time.sleep(2)  # Final wait for lazy-loaded content
            else:
                logger.debug("Scrolling disabled, skipping")

            # Extract ticket data
            logger.info("Extracting ticket data...")
            ticket_containers = results_page.get_ticket_containers()
            raw_tickets = self.extractor.extract_all(ticket_containers, show_progress=True)

            # Validate and create FlightTicket objects
            logger.info(f"Validating {len(raw_tickets)} extracted tickets...")
            tickets = self._create_flight_tickets(raw_tickets)
            logger.info(f"Successfully validated {len(tickets)} tickets")

            # Create search result
            result = FlightSearchResult(
                origin=AirportInfo(code=origin_code, name=origin_name),
                destination=AirportInfo(code=destination_code, name=destination_name),
                search_timestamp=search_timestamp,
                status="success",
                total_results=len(tickets),
                tickets=tickets,
                raw_data={"raw_tickets": raw_tickets},
            )

            logger.info(f"Search completed successfully: {len(tickets)} flights found")

            # Save results if requested
            if save_results:
                logger.info("Saving results to files...")
                self._save_results(result, origin_code, destination_code)
            else:
                logger.debug("Save results disabled")

            return result

        except Exception as e:
            logger.error(f"Search failed with error: {e}")
            return FlightSearchResult(
                origin=AirportInfo(code=origin_code, name=origin_name),
                destination=AirportInfo(code=destination_code, name=destination_name),
                search_timestamp=search_timestamp,
                status="error",
                total_results=0,
                error_message=str(e),
            )

    def _create_flight_tickets(
        self, raw_tickets: List[Dict[str, Any]]
    ) -> List[FlightTicket]:
        """
        Convert raw ticket dictionaries to FlightTicket objects.

        Args:
            raw_tickets: List of raw ticket dictionaries.

        Returns:
            List of validated FlightTicket objects.
        """
        logger.debug(f"Validating {len(raw_tickets)} raw tickets...")
        tickets = []
        for i, raw in enumerate(raw_tickets, 1):
            try:
                ticket = FlightTicket(**raw)
                tickets.append(ticket)
                logger.debug(f"Ticket {i}/{len(raw_tickets)} validated")
            except Exception as e:
                logger.warning(f"Failed to validate ticket {i}: {e}")
                continue
        
        logger.debug(f"Validated {len(tickets)}/{len(raw_tickets)} tickets")
        return tickets

    def _save_results(
        self,
        result: FlightSearchResult,
        origin_code: str,
        destination_code: str,
    ) -> None:
        """
        Save search results to files.

        Args:
            result: FlightSearchResult to save.
            origin_code: Origin airport code for filename.
            destination_code: Destination airport code for filename.
        """
        import os
        timestamp = result.search_timestamp
        files_saved = []

        if self.config.save_csv and result.tickets:
            logger.info("Saving results to CSV...")
            csv_path = generate_output_filename(
                prefix="trave_flight_tickets",
                extension="csv",
                output_dir=self.config.output_dir,
                timestamp=timestamp,
                origin=origin_code,
                destination=destination_code,
            )
            ticket_data = result.to_dataframe_data()
            save_to_csv(ticket_data, csv_path)
            file_size = os.path.getsize(csv_path) / 1024  # KB
            logger.info(f"Results saved to CSV: {csv_path} ({file_size:.1f} KB)")
            files_saved.append(("CSV", csv_path))

        if self.config.save_json:
            logger.info("Saving results to JSON...")
            json_path = generate_output_filename(
                prefix="trave_flight_tickets",
                extension="json",
                output_dir=self.config.output_dir,
                timestamp=timestamp,
                origin=origin_code,
                destination=destination_code,
            )
            save_to_json(result.to_dict(), json_path)
            file_size = os.path.getsize(json_path) / 1024  # KB
            logger.info(f"Results saved to JSON: {json_path} ({file_size:.1f} KB)")
            files_saved.append(("JSON", json_path))

        # Log summary of saved files
        if files_saved:
            logger.info(f"Save complete: {len(files_saved)} file(s) saved")
            for file_type, file_path in files_saved:
                logger.info(f"  - {file_type}: {file_path}")
        else:
            logger.debug("No files saved (save options disabled)")

    def search_multiple_routes(
        self,
        routes: List[Dict[str, str]],
        delay_between_searches: float = 5.0,
    ) -> List[FlightSearchResult]:
        """
        Search multiple routes sequentially.

        Args:
            routes: List of route dictionaries with keys:
                    - origin_code: Origin airport code
                    - origin_name: Origin airport name (optional)
                    - destination_code: Destination airport code
                    - destination_name: Destination airport name (optional)
            delay_between_searches: Delay in seconds between searches.

        Returns:
            List of FlightSearchResult for each route.
        """
        logger.info(f"Starting batch search for {len(routes)} routes")
        results = []

        for i, route in enumerate(routes):
            logger.info(f"\n{'='*50}")
            logger.info(f"Searching route {i + 1}/{len(routes)}: {route['origin_code']} → {route['destination_code']}")
            logger.info(f"{'='*50}")

            result = self.search_flights(
                origin_code=route["origin_code"],
                origin_name=route.get("origin_name"),
                destination_code=route["destination_code"],
                destination_name=route.get("destination_name"),
                save_results=True,
            )

            results.append(result)
            logger.info(f"Route {i + 1}/{len(routes)} complete: {result.total_results} flights found")

            if i < len(routes) - 1:
                logger.info(f"Waiting {delay_between_searches}s before next search...")
                time.sleep(delay_between_searches)

        success_count = sum(1 for r in results if r.status == "success")
        total_tickets = sum(r.total_results for r in results)
        logger.info(f"{'='*50}")
        logger.info(f"Batch search complete: {success_count}/{len(routes)} routes successful, {total_tickets} total flights")
        logger.info(f"{'='*50}")

        return results

    def get_all_tickets(
        self,
        timeout: int = 15,
        scroll: bool = True,
        scroll_timeout: int = 60,
        num_scrolls: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Get all flight tickets from the current search results page.

        This is a lower-level method that returns raw ticket data.
        For a complete search workflow, use search_flights() instead.

        Args:
            timeout: Maximum time to wait for tickets to load initially.
            scroll: Whether to scroll to load more tickets.
            scroll_timeout: Maximum time in seconds to scroll for more tickets.
            num_scrolls: Number of times to scroll.

        Returns:
            List of ticket information dictionaries.
        """
        logger.info("Getting all tickets from current page...")
        
        if not self.driver:
            logger.error("Driver not initialized")
            raise RuntimeError("Driver not initialized")

        results_page = TravelokaResultsPage(self.driver, timeout)

        if not results_page.wait_for_results():
            logger.warning("No tickets found within timeout period")
            return []

        if scroll:
            logger.info("Scrolling to load more tickets...")
            results_page.scroll_to_load_more(
                scroll_pause=2.0,
                num_scrolls=num_scrolls,
                timeout=scroll_timeout,
            )
            time.sleep(2)

        ticket_containers = results_page.get_ticket_containers()
        tickets = self.extractor.extract_all(ticket_containers)
        logger.info(f"Extracted {len(tickets)} tickets from page")
        return tickets


def scrape_traveloka_flights(
    origin_code: str,
    origin_name: Optional[str] = None,
    destination_code: str = "",
    destination_name: Optional[str] = None,
    selenium_url: str = "http://localhost:4444/wd/hub",
) -> FlightSearchResult:
    """
    Convenience function to scrape flights without managing scraper lifecycle.

    Args:
        origin_code: Origin airport IATA code.
        origin_name: Origin airport name (optional, auto-resolved if not provided).
        destination_code: Destination airport IATA code.
        destination_name: Destination airport name (optional, auto-resolved).
        selenium_url: URL of Selenium Grid server.

    Returns:
        FlightSearchResult containing search results.

    Example:
        ```python
        result = scrape_traveloka_flights("CGK", destination_code="DPS")
        if result.status == "success":
            print(f"Found {result.total_results} flights")
        ```
    """
    logger.info(f"Convenience scrape: {origin_code} → {destination_code}")
    config = ScraperConfig(selenium_remote_url=selenium_url)

    with TravelokaScraper(config) as scraper:
        return scraper.search_flights(
            origin_code=origin_code,
            origin_name=origin_name,
            destination_code=destination_code,
            destination_name=destination_name,
        )


def scrape_multiple_routes(
    routes: Optional[List[Dict[str, str]]] = None,
    selenium_url: str = "http://localhost:4444/wd/hub",
) -> List[FlightSearchResult]:
    """
    Convenience function to scrape multiple routes.

    Args:
        routes: List of route dictionaries. If None, uses default Indonesia-Singapore routes.
        selenium_url: URL of Selenium Grid server.

    Returns:
        List of FlightSearchResult for each route.
    """
    if routes is None:
        # Default routes
        routes = [
            {"origin_code": "JKT", "destination_code": "SIN"},
            {"origin_code": "DPS", "destination_code": "SIN"},
            {"origin_code": "SUB", "destination_code": "SIN"},
            {"origin_code": "KNO", "destination_code": "SIN"},
            {"origin_code": "BTH", "destination_code": "SIN"},
        ]
        logger.info(f"Using default routes: {len(routes)} routes")

    logger.info(f"Convenience batch scrape: {len(routes)} routes")
    config = ScraperConfig(selenium_remote_url=selenium_url)

    with TravelokaScraper(config) as scraper:
        return scraper.search_multiple_routes(routes)
