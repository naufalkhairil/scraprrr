"""
Main scraper orchestration for Traveloka hotel data.

This module provides the TravelokaHotelScraper class that coordinates all components
(driver, pages, extractor) to perform complete hotel searches and data extraction.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from selenium.webdriver.remote.webdriver import WebDriver

from traveloka_hotel_scraper.driver import create_driver, quit_driver
from traveloka_hotel_scraper.models import Hotel, HotelSearchResult, HotelScraperConfig
from traveloka_hotel_scraper.page import TravelokaHotelPage
from traveloka_hotel_scraper.utils import generate_output_filename, save_to_csv, save_to_json

logger = logging.getLogger(__name__)


class TravelokaHotelScraper:
    """
    Main scraper class for Traveloka hotel data.

    This class orchestrates the complete scraping workflow:
    1. Initialize WebDriver
    2. Navigate to Traveloka hotel page
    3. Set search location
    4. Execute search
    5. Extract hotel data
    6. Save results

    Example:
        ```python
        scraper = TravelokaHotelScraper()
        result = scraper.search_hotels("Jakarta")
        print(f"Found {result.total_results} hotels")
        scraper.close()
        ```
    """

    def __init__(self, config: Optional[HotelScraperConfig] = None):
        """
        Initialize the TravelokaHotelScraper.

        Args:
            config: Optional scraper configuration. Uses defaults if not provided.
        """
        logger.info("Initializing TravelokaHotelScraper...")
        self.config = config or HotelScraperConfig()
        self.driver: Optional[WebDriver] = None
        self._is_initialized = False
        logger.debug(
            f"Scraper config: scroll_enabled={self.config.scroll_enabled}, "
            f"save_csv={self.config.save_csv}, max_hotels={self.config.max_hotels}"
        )

    def initialize(self) -> "TravelokaHotelScraper":
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

    def __enter__(self) -> "TravelokaHotelScraper":
        """Context manager entry."""
        logger.debug("Entering context manager")
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        logger.debug("Exiting context manager")
        self.close()

    def search_hotels(
        self,
        location: str,
        save_results: bool = True,
    ) -> HotelSearchResult:
        """
        Search for hotels in a specific location.

        Args:
            location: City, hotel, or place name to search.
            save_results: Whether to save results to files.

        Returns:
            HotelSearchResult containing search status and hotel data.

        Raises:
            RuntimeError: If scraper is not initialized.
        """
        logger.info(f"Starting hotel search in: {location}")

        if not self._is_initialized:
            logger.error("Scraper not initialized")
            raise RuntimeError("Scraper not initialized. Call initialize() first.")

        search_timestamp = datetime.now()

        try:
            # Navigate to hotel page
            logger.info("Navigating to Traveloka hotel page...")
            hotel_page = TravelokaHotelPage(self.driver, self.config.element_wait_timeout)
            hotel_page.open()

            # Perform search
            logger.info("Performing hotel search...")
            search_success = hotel_page.search_hotel(location)

            if not search_success:
                logger.error("Hotel search failed")
                return HotelSearchResult(
                    location=location,
                    search_timestamp=search_timestamp,
                    status="error",
                    total_results=0,
                    error_message="Failed to perform search",
                )

            # Wait for results page to load
            logger.info("Waiting for results page to load...")
            time.sleep(5)  # Initial wait for page load

            if not hotel_page.wait_for_hotels(timeout=self.config.element_wait_timeout):
                logger.error("Hotel results section not found")
                return HotelSearchResult(
                    location=location,
                    search_timestamp=search_timestamp,
                    status="error",
                    total_results=0,
                    error_message="No results found within timeout",
                )

            # Scroll to load more hotels if enabled
            if self.config.scroll_enabled:
                logger.info("Scrolling to load more hotels...")
                raw_hotels = hotel_page.get_all_hotels(
                    scroll=True,
                    scroll_timeout=self.config.scroll_timeout,
                    num_scrolls=self.config.num_scrolls,
                    num_hotels=self.config.max_hotels,
                )
            else:
                logger.debug("Scrolling disabled, getting visible hotels only")
                hotel_containers = hotel_page.get_hotel_containers()
                from traveloka_hotel_scraper.extractor import HotelParser

                parser = HotelParser()
                raw_hotels = parser.parse_all(hotel_containers)

            # Validate and create Hotel objects
            logger.info(f"Validating {len(raw_hotels)} extracted hotels...")
            hotels = self._create_hotels(raw_hotels)
            logger.info(f"Successfully validated {len(hotels)} hotels")

            # Create search result
            result = HotelSearchResult(
                location=location,
                search_timestamp=search_timestamp,
                status="success",
                total_results=len(hotels),
                hotels=hotels,
                raw_data={"raw_hotels": raw_hotels},
            )

            logger.info(f"Search completed successfully: {len(hotels)} hotels found")

            # Save results if requested
            if save_results:
                logger.info("Saving results to files...")
                self._save_results(result, location)
            else:
                logger.debug("Save results disabled")

            return result

        except Exception as e:
            logger.error(f"Search failed with error: {e}")
            return HotelSearchResult(
                location=location,
                search_timestamp=search_timestamp,
                status="error",
                total_results=0,
                error_message=str(e),
            )

    def _create_hotels(
        self, raw_hotels: List[Dict[str, Any]]
    ) -> List[Hotel]:
        """
        Convert raw hotel dictionaries to Hotel objects.

        Args:
            raw_hotels: List of raw hotel dictionaries.

        Returns:
            List of validated Hotel objects.
        """
        logger.debug(f"Validating {len(raw_hotels)} raw hotels...")
        hotels = []
        for i, raw in enumerate(raw_hotels, 1):
            try:
                # Skip if hotel_name is missing
                if not raw.get("hotel_name"):
                    logger.warning(f"Hotel {i} missing hotel_name, skipping")
                    continue

                hotel = Hotel(**raw)
                hotels.append(hotel)
                logger.debug(f"Hotel {i}/{len(raw_hotels)} validated")
            except Exception as e:
                logger.warning(f"Failed to validate hotel {i}: {e}")
                continue

        logger.debug(f"Validated {len(hotels)}/{len(raw_hotels)} hotels")
        return hotels

    def _save_results(
        self,
        result: HotelSearchResult,
        location: str,
    ) -> None:
        """
        Save search results to files.

        Args:
            result: HotelSearchResult to save.
            location: Search location for filename.
        """
        timestamp = result.search_timestamp
        files_saved = []

        if self.config.save_csv and result.hotels:
            logger.info("Saving results to CSV...")
            csv_path = generate_output_filename(
                prefix="trave_hotel_results",
                extension="csv",
                output_dir=self.config.output_dir,
                timestamp=timestamp,
                location=location,
            )
            hotel_data = result.to_dataframe_data()
            save_to_csv(hotel_data, csv_path)
            import os

            file_size = os.path.getsize(csv_path) / 1024  # KB
            logger.info(f"Results saved to CSV: {csv_path} ({file_size:.1f} KB)")
            files_saved.append(("CSV", csv_path))

        if self.config.save_json:
            logger.info("Saving results to JSON...")
            json_path = generate_output_filename(
                prefix="trave_hotel_results",
                extension="json",
                output_dir=self.config.output_dir,
                timestamp=timestamp,
                location=location,
            )
            save_to_json(result.to_dict(), json_path)
            import os

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

    def search_multiple_locations(
        self,
        locations: List[str],
        delay_between_searches: float = 5.0,
    ) -> List[HotelSearchResult]:
        """
        Search multiple locations sequentially.

        Args:
            locations: List of location names to search.
            delay_between_searches: Delay in seconds between searches.

        Returns:
            List of HotelSearchResult for each location.
        """
        logger.info(f"Starting batch search for {len(locations)} locations")
        results = []

        for i, location in enumerate(locations):
            logger.info(f"\n{'='*50}")
            logger.info(f"Searching location {i + 1}/{len(locations)}: {location}")
            logger.info(f"{'='*50}")

            result = self.search_hotels(
                location=location,
                save_results=True,
            )

            results.append(result)
            logger.info(f"Location {i + 1}/{len(locations)} complete: {result.total_results} hotels found")

            if i < len(locations) - 1:
                logger.info(f"Waiting {delay_between_searches}s before next search...")
                time.sleep(delay_between_searches)

        success_count = sum(1 for r in results if r.status == "success")
        total_hotels = sum(r.total_results for r in results)
        logger.info(f"{'='*50}")
        logger.info(f"Batch search complete: {success_count}/{len(locations)} locations successful, {total_hotels} total hotels")
        logger.info(f"{'='*50}")

        return results


def scrape_traveloka_hotels(
    location: str,
    selenium_url: str = "http://localhost:4444/wd/hub",
) -> HotelSearchResult:
    """
    Convenience function to scrape hotels without managing scraper lifecycle.

    Args:
        location: City, hotel, or place name to search.
        selenium_url: URL of Selenium Grid server.

    Returns:
        HotelSearchResult containing search results.

    Example:
        ```python
        result = scrape_traveloka_hotels("Jakarta")
        if result.status == "success":
            print(f"Found {result.total_results} hotels")
        ```
    """
    logger.info(f"Convenience scrape: {location}")
    config = HotelScraperConfig(selenium_remote_url=selenium_url)

    with TravelokaHotelScraper(config) as scraper:
        return scraper.search_hotels(location)


def scrape_multiple_locations(
    locations: Optional[List[str]] = None,
    selenium_url: str = "http://localhost:4444/wd/hub",
) -> List[HotelSearchResult]:
    """
    Convenience function to scrape multiple locations.

    Args:
        locations: List of location names. If None, uses default Indonesia locations.
        selenium_url: URL of Selenium Grid server.

    Returns:
        List of HotelSearchResult for each location.
    """
    if locations is None:
        # Default locations
        locations = ["Jakarta", "Bandung", "Surabaya", "Bali", "Yogyakarta"]
        logger.info(f"Using default locations: {len(locations)} locations")

    logger.info(f"Convenience batch scrape: {len(locations)} locations")
    config = HotelScraperConfig(selenium_remote_url=selenium_url)

    with TravelokaHotelScraper(config) as scraper:
        return scraper.search_multiple_locations(locations)
