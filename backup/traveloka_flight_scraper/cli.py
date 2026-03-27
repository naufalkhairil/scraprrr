"""
Command-line interface for Traveloka Flight Scraper.

This module provides a CLI for running flight searches from the command line.
"""

import argparse
import logging
import sys
from typing import List, Optional

from traveloka_flight_scraper.models import ScraperConfig
from traveloka_flight_scraper.scraper import (
    TravelokaScraper,
    scrape_multiple_routes,
    scrape_traveloka_flights,
)

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the CLI.

    Args:
        verbose: If True, set log level to DEBUG. Otherwise, INFO.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="traveloka-scraper",
        description="Scrape flight data from Traveloka.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search single route
  traveloka-scraper search --origin CGK --destination DPS

  # Search with custom Selenium URL
  traveloka-scraper search --origin CGK --destination SIN --selenium-url http://localhost:4444/wd/hub

  # Search multiple predefined routes
  traveloka-scraper search-multiple

  # Search without scrolling (faster, fewer results)
  traveloka-scraper search --origin CGK --destination DPS --no-scroll

  # Enable verbose logging
  traveloka-scraper search --origin CGK --destination DPS --verbose
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search flights for a single route",
    )
    search_parser.add_argument(
        "--origin",
        "-o",
        required=True,
        help="Origin airport IATA code (e.g., CGK, DPS)",
    )
    search_parser.add_argument(
        "--origin-name",
        help="Origin airport name (optional, auto-resolved if not provided)",
    )
    search_parser.add_argument(
        "--destination",
        "-d",
        required=True,
        help="Destination airport IATA code (e.g., SIN, DPS)",
    )
    search_parser.add_argument(
        "--destination-name",
        help="Destination airport name (optional, auto-resolved if not provided)",
    )
    search_parser.add_argument(
        "--selenium-url",
        default="http://localhost:4444/wd/hub",
        help="Selenium Grid server URL (default: http://localhost:4444/wd/hub)",
    )
    search_parser.add_argument(
        "--no-scroll",
        action="store_true",
        help="Disable scrolling to load more tickets",
    )
    search_parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to save output files (default: current directory)",
    )
    search_parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Disable CSV output",
    )
    search_parser.add_argument(
        "--json",
        action="store_true",
        help="Enable JSON output",
    )
    search_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (debug) logging",
    )
    search_parser.add_argument(
        "--max-tickets",
        type=int,
        default=0,
        help="Maximum tickets threshold (default: 0 = unlimited, stops when exceeded)",
    )

    # Search multiple routes command
    multiple_parser = subparsers.add_parser(
        "search-multiple",
        help="Search multiple predefined routes",
    )
    multiple_parser.add_argument(
        "--selenium-url",
        default="http://localhost:4444/wd/hub",
        help="Selenium Grid server URL (default: http://localhost:4444/wd/hub)",
    )
    multiple_parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="Delay in seconds between searches (default: 5.0)",
    )
    multiple_parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to save output files (default: current directory)",
    )
    multiple_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    return parser


def cmd_search(args: argparse.Namespace) -> int:
    """Execute the search command."""
    # Setup logging
    setup_logging(verbose=args.verbose)

    logger.info(f"Starting search: {args.origin} → {args.destination}")

    config = ScraperConfig(
        selenium_remote_url=args.selenium_url,
        scroll_enabled=not args.no_scroll,
        save_csv=not args.no_csv,
        save_json=args.json,
        output_dir=args.output_dir,
        max_tickets=args.max_tickets,
    )

    try:
        with TravelokaScraper(config) as scraper:
            result = scraper.search_flights(
                origin_code=args.origin,
                origin_name=args.origin_name,
                destination_code=args.destination,
                destination_name=args.destination_name,
                save_results=True,
            )

        if result.status == "success":
            logger.info(f"Search completed successfully: {result.total_results} flights found")
            print(f"\n✓ Search completed successfully!")
            print(f"  Found {result.total_results} flights")
            print(f"  Route: {result.origin.code} → {result.destination.code}")

            if result.tickets:
                # Show price range if available
                prices = [t.price for t in result.tickets if t.price]
                if prices:
                    print(f"  Price range: {prices[0]} - {prices[-1]}")

            return 0
        else:
            logger.error(f"Search failed: {result.error_message}")
            print(f"\n✗ Search failed: {result.error_message}")
            return 1

    except KeyboardInterrupt:
        logger.warning("Search interrupted by user")
        print("\n\nSearch interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n✗ Error: {e}")
        return 1


def cmd_search_multiple(args: argparse.Namespace) -> int:
    """Execute the search-multiple command."""
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    logger.info("Starting batch search for multiple routes")
    
    try:
        results = scrape_multiple_routes(
            selenium_url=args.selenium_url,
        )

        success_count = sum(1 for r in results if r.status == "success")
        total_tickets = sum(r.total_results for r in results)

        logger.info(f"Batch search complete: {success_count}/{len(results)} successful, {total_tickets} total flights")
        print(f"\n✓ Batch search completed!")
        print(f"  Successful searches: {success_count}/{len(results)}")
        print(f"  Total flights found: {total_tickets}")

        return 0 if success_count == len(results) else 1

    except KeyboardInterrupt:
        logger.warning("Search interrupted by user")
        print("\n\nSearch interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n✗ Error: {e}")
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "search":
        return cmd_search(args)
    elif args.command == "search-multiple":
        return cmd_search_multiple(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
