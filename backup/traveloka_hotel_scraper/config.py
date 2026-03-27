"""
Configuration utilities for Traveloka hotel scraper.

This module provides configuration management and helper functions.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_default_locations() -> list:
    """Get list of default locations for hotel scraping."""
    return [
        "Jakarta",
        "Bandung",
        "Surabaya",
        "Bali",
        "Yogyakarta",
        "Medan",
        "Makassar",
        "Semarang",
        "Palembang",
        "Tangerang",
    ]


def get_location_suggestions(query: str) -> list:
    """
    Get location suggestions based on query.

    Args:
        query: Partial location name.

    Returns:
        List of matching location names.
    """
    default_locations = get_default_locations()
    if not query:
        return default_locations

    query_lower = query.lower()
    return [
        loc for loc in default_locations
        if query_lower in loc.lower()
    ]
