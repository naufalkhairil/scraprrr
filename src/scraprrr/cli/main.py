"""
Main CLI entry point for Scraprrr.

Unified command-line interface for flight and hotel scraping.
"""

import argparse
import logging
import sys
from typing import List, Optional


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the unified CLI."""
    parser = argparse.ArgumentParser(
        prog="traveloka",
        description="Unified CLI for Traveloka flight and hotel scraping",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search flights
  traveloka search flight --origin CGK --destination DPS

  # Search hotels
  traveloka search hotel --location Jakarta

  # Batch search flights
  traveloka search batch --type flight --routes CGK-DPS,SUB-SIN

  # Batch search hotels
  traveloka search batch --type hotel --locations Jakarta,Bali,Surabaya

  # Search with custom settings
  traveloka search flight --origin CGK --destination SIN --no-scroll --json

  # Enable verbose logging
  traveloka search flight --origin CGK --destination DPS --verbose
        """,
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search for flights or hotels",
    )

    search_subparsers = search_parser.add_subparsers(
        dest="search_type",
        help="Type of search",
    )

    # Flight search
    from scraprrr.cli.parsers.flight_parser import add_flight_arguments
    from scraprrr.cli.commands.flight import cmd_flight_search

    flight_parser = search_subparsers.add_parser("flight", help="Search flights for a single route")
    add_flight_arguments(flight_parser)
    flight_parser.set_defaults(func=cmd_flight_search)

    # Hotel search
    from scraprrr.cli.parsers.hotel_parser import add_hotel_arguments
    from scraprrr.cli.commands.hotel import cmd_hotel_search

    hotel_parser = search_subparsers.add_parser("hotel", help="Search hotels in a specific location")
    add_hotel_arguments(hotel_parser)
    hotel_parser.set_defaults(func=cmd_hotel_search)

    # Batch search
    from scraprrr.cli.commands.flight import cmd_flight_batch
    from scraprrr.cli.commands.hotel import cmd_hotel_batch

    batch_parser = search_subparsers.add_parser("batch", help="Search multiple routes or locations")
    batch_parser.add_argument(
        "--type",
        choices=["flight", "hotel"],
        required=True,
        help="Type of batch search",
    )

    # Mutually exclusive group for batch input
    batch_group = batch_parser.add_mutually_exclusive_group(required=True)
    batch_group.add_argument(
        "--routes",
        help="Comma-separated routes (e.g., CGK-DPS,SUB-SIN)",
    )
    batch_group.add_argument(
        "--routes-file",
        help="File with one route per line (e.g., CGK,DPS)",
    )
    batch_group.add_argument(
        "--locations",
        help="Comma-separated locations (e.g., Jakarta,Bali)",
    )
    batch_group.add_argument(
        "--locations-file",
        help="File with one location per line",
    )

    batch_parser.add_argument(
        "--max-hotels",
        type=int,
        default=100,
        help="Maximum hotels per location (for hotel searches, default: 100)",
    )
    batch_parser.add_argument(
        "--num-scrolls",
        type=int,
        default=20,
        help="Maximum scrolls (for hotel searches, default: 20)",
    )
    batch_parser.add_argument(
        "--max-tickets",
        type=int,
        default=0,
        help="Maximum tickets threshold (for flight searches, default: 0 = unlimited)",
    )
    batch_parser.add_argument(
        "--selenium-url",
        default="http://localhost:4444/wd/hub",
        help="Selenium Grid server URL (default: http://localhost:4444/wd/hub)",
    )
    batch_parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for results (default: current directory)",
    )
    batch_parser.add_argument(
        "--no-scroll",
        action="store_true",
        help="Disable scrolling (only scrape visible results)",
    )
    batch_parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Disable CSV output",
    )
    batch_parser.add_argument(
        "--save-json",
        action="store_true",
        help="Enable JSON output",
    )
    batch_parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Delay between searches in seconds (default: 5.0)",
    )
    batch_parser.set_defaults(
        func=lambda args: cmd_flight_batch(args) if args.type == "flight" else cmd_hotel_batch(args)
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    setup_logging(verbose=args.verbose)

    if args.command == "search":
        if args.search_type is None:
            parser.parse_args(["search", "--help"])
            return 1
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
