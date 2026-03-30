"""
CLI argument parsers for Scraprrr.
"""

from scraprrr.cli.parsers.flight_parser import add_flight_arguments, add_flight_batch_arguments
from scraprrr.cli.parsers.hotel_parser import add_hotel_arguments, add_hotel_batch_arguments

__all__ = [
    "add_flight_arguments",
    "add_flight_batch_arguments",
    "add_hotel_arguments",
    "add_hotel_batch_arguments",
]
