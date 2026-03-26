"""
Command-line interface for Traveloka hotel scraper.

This module provides CLI commands for scraping hotel data from Traveloka.
"""

import argparse
import logging
import sys
from typing import List, Optional

from traveloka_hotel_scraper.models import HotelScraperConfig
from traveloka_hotel_scraper.scraper import (
    TravelokaHotelScraper,
    scrape_multiple_locations,
    scrape_traveloka_hotels,
)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Reduce selenium logging noise
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def cmd_search(args: argparse.Namespace) -> int:
    """Handle the 'search' command."""
    logger = logging.getLogger(__name__)
    logger.info(f"Searching hotels in: {args.location}")

    config = HotelScraperConfig(
        selenium_remote_url=args.selenium_url,
        scroll_enabled=not args.no_scroll,
        max_hotels=args.max_hotels,
        num_scrolls=args.num_scrolls,
        save_csv=not args.no_save_csv,
        save_json=args.save_json,
        output_dir=args.output_dir,
    )

    try:
        with TravelokaHotelScraper(config) as scraper:
            result = scraper.search_hotels(
                location=args.location,
                save_results=True,
            )

        if result.status == "success":
            logger.info(f"Successfully found {result.total_results} hotels")
            return 0
        else:
            logger.error(f"Search failed: {result.error_message}")
            return 1

    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def cmd_search_batch(args: argparse.Namespace) -> int:
    """Handle the 'search-batch' command."""
    logger = logging.getLogger(__name__)

    # Parse locations from comma-separated string or file
    if args.locations_file:
        with open(args.locations_file, "r") as f:
            locations = [line.strip() for line in f if line.strip()]
    else:
        locations = [loc.strip() for loc in args.locations.split(",")]

    logger.info(f"Searching hotels in {len(locations)} locations")

    config = HotelScraperConfig(
        selenium_remote_url=args.selenium_url,
        scroll_enabled=not args.no_scroll,
        max_hotels=args.max_hotels,
        num_scrolls=args.num_scrolls,
        save_csv=not args.no_save_csv,
        save_json=args.save_json,
        output_dir=args.output_dir,
    )

    try:
        with TravelokaHotelScraper(config) as scraper:
            results = scraper.search_multiple_locations(
                locations=locations,
                delay_between_searches=args.delay,
            )

        success_count = sum(1 for r in results if r.status == "success")
        total_hotels = sum(r.total_results for r in results)
        logger.info(f"Batch search complete: {success_count}/{len(locations)} successful, {total_hotels} total hotels")

        return 0 if success_count == len(locations) else 1

    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="traveloka-hotel-scraper",
        description="Scrape hotel data from Traveloka.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search hotels in Jakarta
  traveloka-hotel-scraper search Jakarta

  # Search with custom settings
  traveloka-hotel-scraper search Bali --max-hotels 50 --no-scroll

  # Batch search multiple locations
  traveloka-hotel-scraper search-batch "Jakarta,Bandung,Surabaya"

  # Batch search from file
  traveloka-hotel-scraper search-batch --locations-file cities.txt
        """,
    )

    # Global arguments
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--selenium-url",
        default="http://localhost:4444/wd/hub",
        help="Selenium Grid server URL (default: http://localhost:4444/wd/hub)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search hotels in a specific location",
    )
    search_parser.add_argument(
        "location",
        help="City, hotel, or place name to search",
    )
    search_parser.add_argument(
        "--max-hotels",
        type=int,
        default=100,
        help="Maximum number of hotels to collect (default: 100)",
    )
    search_parser.add_argument(
        "--num-scrolls",
        type=int,
        default=20,
        help="Maximum number of scrolls (default: 20)",
    )
    search_parser.add_argument(
        "--no-scroll",
        action="store_true",
        help="Disable scrolling (only scrape visible hotels)",
    )
    search_parser.add_argument(
        "--no-save-csv",
        action="store_true",
        help="Disable CSV output",
    )
    search_parser.add_argument(
        "--save-json",
        action="store_true",
        help="Enable JSON output",
    )
    search_parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for results (default: current directory)",
    )
    search_parser.set_defaults(func=cmd_search)

    # Batch search command
    batch_parser = subparsers.add_parser(
        "search-batch",
        help="Search hotels in multiple locations",
    )
    batch_group = batch_parser.add_mutually_exclusive_group(required=True)
    batch_group.add_argument(
        "locations",
        nargs="?",
        help="Comma-separated list of locations",
    )
    batch_group.add_argument(
        "--locations-file",
        help="File with one location per line",
    )
    batch_parser.add_argument(
        "--max-hotels",
        type=int,
        default=100,
        help="Maximum number of hotels per location (default: 100)",
    )
    batch_parser.add_argument(
        "--num-scrolls",
        type=int,
        default=20,
        help="Maximum number of scrolls (default: 20)",
    )
    batch_parser.add_argument(
        "--no-scroll",
        action="store_true",
        help="Disable scrolling (only scrape visible hotels)",
    )
    batch_parser.add_argument(
        "--no-save-csv",
        action="store_true",
        help="Disable CSV output",
    )
    batch_parser.add_argument(
        "--save-json",
        action="store_true",
        help="Enable JSON output",
    )
    batch_parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for results (default: current directory)",
    )
    batch_parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Delay between searches in seconds (default: 5.0)",
    )
    batch_parser.set_defaults(func=cmd_search_batch)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    setup_logging(args.verbose)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
