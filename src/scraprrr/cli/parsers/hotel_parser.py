"""
Hotel CLI argument parsers.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_hotel_arguments(parser: "argparse.ArgumentParser") -> None:
    """Add hotel search arguments to parser."""
    parser.add_argument(
        "location",
        help="City, hotel, or place name to search",
    )
    parser.add_argument(
        "--max-hotels",
        type=int,
        default=100,
        help="Maximum number of hotels to collect (default: 100)",
    )
    _add_common_arguments(parser)


def add_hotel_batch_arguments(parser: "argparse.ArgumentParser") -> None:
    """Add hotel batch search arguments to parser."""
    batch_group = parser.add_mutually_exclusive_group(required=True)
    batch_group.add_argument(
        "--locations",
        help="Comma-separated locations (e.g., Jakarta,Bali)",
    )
    batch_group.add_argument(
        "--locations-file",
        help="File with one location per line",
    )
    parser.add_argument(
        "--max-hotels",
        type=int,
        default=100,
        help="Maximum hotels per location (default: 100)",
    )
    _add_common_arguments(parser)


def _add_common_arguments(parser: "argparse.ArgumentParser") -> None:
    """Add common arguments shared by all commands."""
    parser.add_argument(
        "--selenium-url",
        default="http://localhost:4444/wd/hub",
        help="Selenium Grid server URL (default: http://localhost:4444/wd/hub)",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for results (default: current directory)",
    )
    parser.add_argument(
        "--no-scroll",
        action="store_true",
        help="Disable scrolling (only scrape visible results)",
    )
    parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Disable CSV output",
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="Enable JSON output",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Delay between searches in seconds (default: 5.0)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )
