"""
Core infrastructure for Scraprrr.

This module provides shared utilities used across all scraper modules.
"""

from scraprrr.core.driver import create_driver, quit_driver
from scraprrr.core.utils import ScraperConfig
from scraprrr.core.base import BaseScraper

__all__ = [
    "create_driver",
    "quit_driver",
    "ScraperConfig",
    "BaseScraper",
]
