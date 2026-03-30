"""
Flight CLI argument parsers.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse


def add_flight_arguments(parser: "argparse.ArgumentParser") -> None:
    """Add flight search arguments to parser."""
    parser.add_argument(
        "--origin", "-o",
        required=True,
        help="Origin airport IATA code (e.g., CGK, DPS)",
    )
    parser.add_argument(
        "--origin-name",
        help="Origin airport name (optional, auto-resolved if not provided)",
    )
    parser.add_argument(
        "--destination", "-d",
        required=True,
        help="Destination airport IATA code (e.g., SIN, DPS)",
    )
    parser.add_argument(
        "--destination-name",
        help="Destination airport name (optional, auto-resolved if not provided)",
    )
    parser.add_argument(
        "--max-tickets",
        type=int,
        default=0,
        help="Maximum tickets threshold (default: 0 = unlimited)",
    )
    _add_common_arguments(parser)


def add_flight_batch_arguments(parser: "argparse.ArgumentParser") -> None:
    """Add flight batch search arguments to parser."""
    batch_group = parser.add_mutually_exclusive_group(required=True)
    batch_group.add_argument(
        "--routes",
        help="Comma-separated routes (e.g., CGK-DPS,SUB-SIN)",
    )
    batch_group.add_argument(
        "--routes-file",
        help="File with one route per line (e.g., CGK,DPS)",
    )
    parser.add_argument(
        "--max-tickets",
        type=int,
        default=0,
        help="Maximum tickets threshold (default: 0 = unlimited)",
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
