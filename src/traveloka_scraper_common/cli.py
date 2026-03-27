"""
Unified Command-line interface for Traveloka scrapers.

This module provides a single CLI for both flight and hotel scraping operations.

Usage:
    traveloka search flight --origin CGK --destination DPS
    traveloka search hotel --location Jakarta
    traveloka search batch --type flight --routes CGK-DPS,SUB-SIN
    traveloka search batch --type hotel --locations Jakarta,Bali
"""

import argparse
import logging
import sys
from typing import List, Optional


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
    # Reduce selenium logging noise
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# ============================================================================
# Flight Search Commands
# ============================================================================

def cmd_flight_search(args: argparse.Namespace) -> int:
    """Execute flight search command."""
    logger = logging.getLogger(__name__)
    logger.info(f"Starting flight search: {args.origin} → {args.destination}")

    from traveloka_flight_scraper.models import ScraperConfig
    from traveloka_flight_scraper.scraper import TravelokaScraper

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


def cmd_batch_search(args: argparse.Namespace) -> int:
    """Execute batch search command, routing to flight or hotel handler."""
    if args.type == "flight":
        return cmd_flight_batch(args)
    else:
        return cmd_hotel_batch(args)


def cmd_flight_batch(args: argparse.Namespace) -> int:
    """Execute flight batch search command."""
    logger = logging.getLogger(__name__)

    from traveloka_flight_scraper.models import ScraperConfig
    from traveloka_flight_scraper.scraper import TravelokaScraper

    # Parse routes
    if args.routes_file:
        with open(args.routes_file, "r") as f:
            routes = []
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split(",")
                    if len(parts) >= 2:
                        routes.append({
                            "origin_code": parts[0].strip(),
                            "destination_code": parts[1].strip(),
                        })
    else:
        routes = []
        for route_str in args.routes.split(","):
            parts = route_str.strip().split("-")
            if len(parts) >= 2:
                routes.append({
                    "origin_code": parts[0].strip(),
                    "destination_code": parts[1].strip(),
                })

    logger.info(f"Starting batch flight search for {len(routes)} routes")

    config = ScraperConfig(
        selenium_remote_url=args.selenium_url,
        scroll_enabled=not args.no_scroll,
        save_csv=not args.no_csv,
        save_json=args.json,
        output_dir=args.output_dir,
    )

    try:
        with TravelokaScraper(config) as scraper:
            results = scraper.search_multiple_routes(
                routes=routes,
                delay_between_searches=args.delay,
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


# ============================================================================
# Hotel Search Commands
# ============================================================================

def cmd_hotel_search(args: argparse.Namespace) -> int:
    """Execute hotel search command."""
    logger = logging.getLogger(__name__)
    logger.info(f"Searching hotels in: {args.location}")

    from traveloka_hotel_scraper.models import HotelScraperConfig
    from traveloka_hotel_scraper.scraper import TravelokaHotelScraper

    config = HotelScraperConfig(
        selenium_remote_url=args.selenium_url,
        scroll_enabled=not args.no_scroll,
        max_hotels=args.max_hotels,
        num_scrolls=args.num_scrolls,
        save_csv=not args.no_csv,
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
            print(f"\n✓ Search completed successfully!")
            print(f"  Found {result.total_results} hotels in {args.location}")

            if result.hotels:
                # Show sample hotels
                print(f"  Sample hotels:")
                for hotel in result.hotels[:3]:
                    print(f"    - {hotel.hotel_name}: {hotel.price}")

            return 0
        else:
            logger.error(f"Search failed: {result.error_message}")
            print(f"\n✗ Search failed: {result.error_message}")
            return 1

    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
        print("\n\nSearch interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n✗ Error: {e}")
        return 1


def cmd_hotel_batch(args: argparse.Namespace) -> int:
    """Execute hotel batch search command."""
    logger = logging.getLogger(__name__)

    from traveloka_hotel_scraper.models import HotelScraperConfig
    from traveloka_hotel_scraper.scraper import TravelokaHotelScraper

    # Parse locations
    if args.locations_file:
        with open(args.locations_file, "r") as f:
            locations = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        locations = [loc.strip() for loc in args.locations.split(",")]

    logger.info(f"Searching hotels in {len(locations)} locations")

    config = HotelScraperConfig(
        selenium_remote_url=args.selenium_url,
        scroll_enabled=not args.no_scroll,
        max_hotels=args.max_hotels,
        num_scrolls=args.num_scrolls,
        save_csv=not args.no_csv,
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
        print(f"\n✓ Batch search completed!")
        print(f"  Successful searches: {success_count}/{len(locations)}")
        print(f"  Total hotels found: {total_hotels}")

        return 0 if success_count == len(locations) else 1

    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
        print("\n\nSearch interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n✗ Error: {e}")
        return 1


# ============================================================================
# Argument Parser Setup
# ============================================================================

def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add common arguments shared by all search commands."""
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
    flight_parser = search_subparsers.add_parser(
        "flight",
        help="Search flights for a single route",
    )
    flight_parser.add_argument(
        "--origin", "-o",
        required=True,
        help="Origin airport IATA code (e.g., CGK, DPS)",
    )
    flight_parser.add_argument(
        "--origin-name",
        help="Origin airport name (optional, auto-resolved if not provided)",
    )
    flight_parser.add_argument(
        "--destination", "-d",
        required=True,
        help="Destination airport IATA code (e.g., SIN, DPS)",
    )
    flight_parser.add_argument(
        "--destination-name",
        help="Destination airport name (optional, auto-resolved if not provided)",
    )
    flight_parser.add_argument(
        "--max-tickets",
        type=int,
        default=0,
        help="Maximum tickets threshold (default: 0 = unlimited)",
    )
    add_common_arguments(flight_parser)
    flight_parser.set_defaults(func=cmd_flight_search)

    # Hotel search
    hotel_parser = search_subparsers.add_parser(
        "hotel",
        help="Search hotels in a specific location",
    )
    hotel_parser.add_argument(
        "location",
        help="City, hotel, or place name to search",
    )
    hotel_parser.add_argument(
        "--max-hotels",
        type=int,
        default=100,
        help="Maximum number of hotels to collect (default: 100)",
    )
    hotel_parser.add_argument(
        "--num-scrolls",
        type=int,
        default=20,
        help="Maximum number of scrolls (default: 20)",
    )
    hotel_parser.add_argument(
        "--selenium-url",
        default="http://localhost:4444/wd/hub",
        help="Selenium Grid server URL (default: http://localhost:4444/wd/hub)",
    )
    hotel_parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for results (default: current directory)",
    )
    hotel_parser.add_argument(
        "--no-scroll",
        action="store_true",
        help="Disable scrolling (only scrape visible hotels)",
    )
    hotel_parser.add_argument(
        "--no-csv",
        action="store_true",
        help="Disable CSV output",
    )
    hotel_parser.add_argument(
        "--save-json",
        action="store_true",
        help="Enable JSON output",
    )
    hotel_parser.set_defaults(func=cmd_hotel_search)

    # Batch search
    batch_parser = search_subparsers.add_parser(
        "batch",
        help="Search multiple routes or locations",
    )
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
        "--delay",
        type=float,
        default=5.0,
        help="Delay between searches in seconds (default: 5.0)",
    )
    batch_parser.set_defaults(func=cmd_batch_search)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    # Setup logging after parsing to respect verbose flag
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
