"""
Utility functions for Traveloka hotel scraper.

This module re-exports shared utilities from traveloka_scraper_common.
"""

from traveloka_scraper_common.utils import (
    generate_output_filename,
    save_to_csv,
    save_to_json,
)

__all__ = [
    "generate_output_filename",
    "save_to_csv",
    "save_to_json",
]
