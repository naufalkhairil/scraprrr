"""
Hotel CLI commands for Scraprrr.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse

logger = logging.getLogger(__name__)


def cmd_hotel_search(args: "argparse.Namespace") -> int:
    """Execute hotel search command."""
    from scraprrr.modules.hotel import HotelScraper
    from scraprrr.modules.hotel.models import HotelScraperConfig

    logger.info(f"Searching hotels in: {args.location}")

    config = HotelScraperConfig(
        selenium_remote_url=args.selenium_url,
        scroll_enabled=not args.no_scroll,
        max_hotels=args.max_hotels,
        save_csv=not args.no_csv,
        save_json=args.save_json,
        output_dir=args.output_dir,
    )

    try:
        with HotelScraper(config) as scraper:
            result = scraper.search(
                location=args.location,
                save_results=True,
            )

        if result.status == "success":
            print(f"\n✓ Search completed successfully!")
            print(f"  Found {result.total_results} hotels in {args.location}")

            if result.hotels:
                print(f"  Sample hotels:")
                for hotel in result.hotels[:3]:
                    print(f"    - {hotel.hotel_name}: {hotel.price}")

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


def cmd_hotel_batch(args: "argparse.Namespace") -> int:
    """Execute hotel batch search command."""
    from scraprrr.modules.hotel import HotelScraper
    from scraprrr.modules.hotel.models import HotelScraperConfig

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
        save_csv=not args.no_csv,
        save_json=args.save_json,
        output_dir=args.output_dir,
    )

    try:
        with HotelScraper(config) as scraper:
            results = []
            for i, location in enumerate(locations):
                logger.info(f"\n{'='*50}")
                logger.info(f"Searching location {i + 1}/{len(locations)}: {location}")

                result = scraper.search(
                    location=location,
                    save_results=True,
                )
                results.append(result)

                if i < len(locations) - 1:
                    import time
                    logger.info(f"Waiting {args.delay}s before next search...")
                    time.sleep(args.delay)

        success_count = sum(1 for r in results if r.status == "success")
        total_hotels = sum(r.total_results for r in results)

        print(f"\n✓ Batch search completed!")
        print(f"  Successful searches: {success_count}/{len(locations)}")
        print(f"  Total hotels found: {total_hotels}")

        return 0 if success_count == len(results) else 1

    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"\n✗ Error: {e}")
        return 1
