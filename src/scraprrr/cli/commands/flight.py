"""
Flight CLI commands for Scraprrr.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse

logger = logging.getLogger(__name__)


def cmd_flight_search(args: "argparse.Namespace") -> int:
    """Execute flight search command."""
    from scraprrr.modules.flight import FlightScraper
    from scraprrr.modules.flight.models import FlightScraperConfig

    logger.info(f"Starting flight search: {args.origin} → {args.destination}")

    config = FlightScraperConfig(
        selenium_remote_url=args.selenium_url,
        scroll_enabled=not args.no_scroll,
        save_csv=not args.no_csv,
        save_json=args.save_json,
        output_dir=args.output_dir,
        max_tickets=args.max_tickets,
    )

    try:
        with FlightScraper(config) as scraper:
            result = scraper.search(
                origin=args.origin,
                destination=args.destination,
                origin_name=args.origin_name,
                destination_name=args.destination_name,
                save_results=True,
            )

        if result.status == "success":
            print(f"\n✓ Search completed successfully!")
            print(f"  Found {result.total_results} flights")
            print(f"  Route: {result.origin.code} → {result.destination.code}")

            if result.tickets:
                prices = [t.price for t in result.tickets if t.price]
                if prices:
                    print(f"  Price range: {prices[0]} - {prices[-1]}")

            return 0
        else:
            print(f"\n✗ Search failed: {result.error_message}")
            return 1

    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n✗ Error: {e}")
        return 1


def cmd_flight_batch(args: "argparse.Namespace") -> int:
    """Execute flight batch search command."""
    from scraprrr.modules.flight import FlightScraper
    from scraprrr.modules.flight.models import FlightScraperConfig

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

    config = FlightScraperConfig(
        selenium_remote_url=args.selenium_url,
        scroll_enabled=not args.no_scroll,
        save_csv=not args.no_csv,
        save_json=args.save_json,
        output_dir=args.output_dir,
    )

    try:
        with FlightScraper(config) as scraper:
            results = []
            for i, route in enumerate(routes):
                logger.info(f"\n{'='*50}")
                logger.info(f"Searching route {i + 1}/{len(routes)}: {route['origin_code']} → {route['destination_code']}")
                
                result = scraper.search(
                    origin=route["origin_code"],
                    destination=route["destination_code"],
                    save_results=True,
                )
                results.append(result)

                if i < len(routes) - 1:
                    import time
                    logger.info(f"Waiting {args.delay}s before next search...")
                    time.sleep(args.delay)

        success_count = sum(1 for r in results if r.status == "success")
        total_tickets = sum(r.total_results for r in results)

        print(f"\n✓ Batch search completed!")
        print(f"  Successful searches: {success_count}/{len(routes)}")
        print(f"  Total flights found: {total_tickets}")

        return 0 if success_count == len(results) else 1

    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n✗ Error: {e}")
        return 1
