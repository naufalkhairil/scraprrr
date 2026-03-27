"""
Base scraper class for Scraprrr.

This module provides the abstract base class that all scrapers inherit from.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar

from selenium.webdriver.remote.webdriver import WebDriver

from scraprrr.core.driver import create_driver, quit_driver
from scraprrr.core.utils import ScraperConfig

logger = logging.getLogger(__name__)

# Type variable for result type
T = TypeVar("T")


class BaseScraper(ABC, Generic[T]):
    """
    Abstract base class for all scrapers.

    Provides common functionality like WebDriver management and configuration.

    Type Parameters:
        T: The result type returned by search operations.
    """

    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the scraper.

        Args:
            config: Optional scraper configuration. Uses defaults if not provided.
        """
        logger.info(f"Initializing {self.__class__.__name__}...")
        self.config = config or ScraperConfig()
        self.driver: Optional[WebDriver] = None
        self._is_initialized = False

    def initialize(self) -> "BaseScraper[T]":
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

    def __enter__(self) -> "BaseScraper[T]":
        """Context manager entry."""
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

    @abstractmethod
    def search(self, **kwargs: Any) -> T:
        """
        Perform a search operation.

        Args:
            **kwargs: Search parameters (varies by scraper type).

        Returns:
            Search result of type T.
        """
        pass

    @abstractmethod
    def save_results(self, result: T) -> None:
        """
        Save search results to files.

        Args:
            result: Search result to save.
        """
        pass
