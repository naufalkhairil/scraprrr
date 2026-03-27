"""
Hotel scraper implementation for Traveloka.com.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from scraprrr.core.base import BaseScraper
from scraprrr.core.utils import generate_output_filename, save_to_csv, save_to_json
from scraprrr.modules.hotel.models import (
    Hotel,
    HotelSearchResult,
    HotelScraperConfig,
)

logger = logging.getLogger(__name__)


class HotelScraper(BaseScraper[HotelSearchResult]):
    """
    Scraper for Traveloka hotel data.

    Example:
        ```python
        with HotelScraper() as scraper:
            result = scraper.search(location="Jakarta")
            print(f"Found {result.total_results} hotels")
        ```
    """

    def __init__(self, config: Optional[HotelScraperConfig] = None):
        """Initialize the HotelScraper."""
        super().__init__(config or HotelScraperConfig())
        self.config: HotelScraperConfig

    def search(
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
        """
        logger.info(f"Starting hotel search in: {location}")

        if not self._is_initialized:
            raise RuntimeError("Scraper not initialized. Call initialize() first.")

        search_timestamp = datetime.now()

        try:
            from scraprrr.modules.hotel.page import HotelPage

            hotel_page = HotelPage(self.driver, self.config.element_wait_timeout)
            hotel_page.open()

            search_success = hotel_page.search(location)

            if not search_success:
                return HotelSearchResult(
                    location=location,
                    search_timestamp=search_timestamp,
                    status="error",
                    total_results=0,
                    error_message="Failed to perform search",
                )

            time.sleep(5)

            if not hotel_page.wait_for_hotels(timeout=self.config.element_wait_timeout):
                return HotelSearchResult(
                    location=location,
                    search_timestamp=search_timestamp,
                    status="error",
                    total_results=0,
                    error_message="No results found within timeout",
                )

            if self.config.scroll_enabled:
                raw_hotels = hotel_page.get_all_hotels(
                    scroll=True,
                    scroll_timeout=self.config.scroll_timeout,
                    num_hotels=self.config.max_hotels,
                )
            else:
                from scraprrr.modules.hotel.extractor import HotelExtractor

                extractor = HotelExtractor()
                hotel_containers = hotel_page.get_hotel_containers()
                raw_hotels = extractor.extract_all(hotel_containers)

            hotels = self._create_hotels(raw_hotels)

            result = HotelSearchResult(
                location=location,
                search_timestamp=search_timestamp,
                status="success",
                total_results=len(hotels),
                hotels=hotels,
                raw_data={"raw_hotels": raw_hotels},
            )

            logger.info(f"Search completed: {len(hotels)} hotels found")

            if save_results:
                self.save_results(result, location)

            return result

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return HotelSearchResult(
                location=location,
                search_timestamp=search_timestamp,
                status="error",
                total_results=0,
                error_message=str(e),
            )

    def _create_hotels(self, raw_hotels: List[Dict[str, Any]]) -> List[Hotel]:
        """Convert raw hotel dictionaries to Hotel objects."""
        hotels = []
        for raw in raw_hotels:
            try:
                if not raw.get("hotel_name"):
                    continue
                hotel = Hotel(**raw)
                hotels.append(hotel)
            except Exception as e:
                logger.warning(f"Failed to validate hotel: {e}")
        return hotels

    def save_results(self, result: HotelSearchResult, location: str) -> None:
        """Save search results to files."""
        timestamp = result.search_timestamp
        files_saved = []

        if self.config.save_csv and result.hotels:
            csv_path = generate_output_filename(
                prefix="trave_hotel_results",
                extension="csv",
                output_dir=self.config.output_dir,
                timestamp=timestamp,
                location=location,
            )
            save_to_csv(result.to_dataframe_data(), csv_path)
            files_saved.append(("CSV", csv_path))

        if self.config.save_json:
            json_path = generate_output_filename(
                prefix="trave_hotel_results",
                extension="json",
                output_dir=self.config.output_dir,
                timestamp=timestamp,
                location=location,
            )
            save_to_json(result.to_dict(), json_path)
            files_saved.append(("JSON", json_path))

        if files_saved:
            logger.info(f"Saved {len(files_saved)} file(s)")
            for file_type, file_path in files_saved:
                logger.info(f"  - {file_type}: {file_path}")


def scrape_hotels(
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
    """
    config = HotelScraperConfig(selenium_remote_url=selenium_url)
    with HotelScraper(config) as scraper:
        return scraper.search(location=location)
