"""
Selenium WebDriver management for Traveloka flight scraping.

This module re-exports the shared driver functions from traveloka_scraper_common.
"""

from traveloka_scraper_common.driver import create_driver, quit_driver

__all__ = ["create_driver", "quit_driver"]
