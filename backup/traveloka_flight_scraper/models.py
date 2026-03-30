"""
Pydantic data models for Traveloka flight data.

This module provides structured data models for representing flight search
parameters, results, and ticket information with validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AirportInfo(BaseModel):
    """Information about an airport."""

    code: str = Field(..., description="IATA airport code (e.g., 'CGK')")
    name: str = Field(..., description="Full airport name")


class FlightInfo(BaseModel):
    """Information about a specific flight segment."""

    departure_time: str = Field(..., description="Departure time")
    departure_airport: str = Field(..., description="Departure airport code")
    arrival_time: str = Field(..., description="Arrival time")
    arrival_airport: str = Field(..., description="Arrival airport code")
    duration: str = Field(..., description="Flight duration")
    flight_type: str = Field(..., description="Flight type (Direct/Transit)")


class FlightTicket(BaseModel):
    """Complete flight ticket information extracted from Traveloka."""

    # Airline information
    airline_name: str = Field(..., description="Name of the airline")
    airline_logo: Optional[str] = Field(None, description="URL to airline logo")

    # Flight details
    departure_time: str = Field(..., description="Departure time")
    departure_airport: str = Field(..., description="Departure airport code")
    arrival_time: str = Field(..., description="Arrival time")
    arrival_airport: str = Field(..., description="Arrival airport code")
    duration: str = Field(..., description="Flight duration")
    flight_type: str = Field(..., description="Flight type (Direct/Transit)")

    # Pricing
    price: str = Field(..., description="Current ticket price")
    original_price: Optional[str] = Field(None, description="Original price before discount")

    # Additional information
    baggage: str = Field(..., description="Baggage allowance information")
    promos: List[str] = Field(default_factory=list, description="List of active promotions")
    special_tag: Optional[str] = Field(None, description="Special tag (e.g., 'Bigger Discount')")
    highlight_label: Optional[str] = Field(
        None,
        description="Highlight label (e.g., 'Cheapest', 'Best flight')",
    )

    # Metadata
    extracted_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the ticket was extracted",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "airline_name": "Garuda Indonesia",
                "airline_logo": "https://example.com/logo.png",
                "departure_time": "08:00",
                "departure_airport": "CGK",
                "arrival_time": "10:30",
                "arrival_airport": "DPS",
                "duration": "2h 30m",
                "flight_type": "Direct",
                "price": "Rp 1.500.000",
                "original_price": "Rp 2.000.000",
                "baggage": "20 kg",
                "promos": ["Member Discount"],
                "special_tag": "Bigger Discount",
                "highlight_label": "Cheapest",
                "extracted_at": "2026-03-26T10:00:00",
            }
        }
    )


class FlightSearchResult(BaseModel):
    """Result of a flight search operation."""

    # Search parameters
    origin: AirportInfo = Field(..., description="Origin airport")
    destination: AirportInfo = Field(..., description="Destination airport")
    search_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the search was performed",
    )

    # Results
    status: str = Field(..., description="Search status ('success' or 'error')")
    total_results: int = Field(..., description="Number of flights found")
    tickets: List[FlightTicket] = Field(
        default_factory=list,
        description="List of flight tickets",
    )
    error_message: Optional[str] = Field(None, description="Error message if search failed")

    # Raw data (for debugging/extensibility)
    raw_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Raw extracted data before validation",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the search result to a dictionary."""
        return self.model_dump()

    def to_dataframe_data(self) -> List[Dict[str, Any]]:
        """
        Convert tickets to a format suitable for DataFrame creation.

        Returns:
            List of dictionaries, one per ticket.
        """
        return [ticket.model_dump() for ticket in self.tickets]


class ScraperConfig(BaseModel):
    """Configuration for the TravelokaScraper."""

    # Selenium settings
    selenium_remote_url: str = Field(
        default="http://localhost:4444/wd/hub",
        description="URL of the Selenium Grid server",
    )
    page_load_timeout: int = Field(
        default=30,
        description="Timeout for page loads in seconds",
    )
    element_wait_timeout: int = Field(
        default=15,
        description="Timeout for element waits in seconds",
    )

    # Scraping settings
    scroll_enabled: bool = Field(
        default=True,
        description="Whether to scroll to load more tickets",
    )
    scroll_timeout: int = Field(
        default=60,
        description="Maximum time in seconds to scroll",
    )
    scroll_pause: float = Field(
        default=2.0,
        description="Time to wait between scrolls in seconds",
    )
    max_tickets: int = Field(
        default=0,
        description="Maximum tickets threshold (0 for unlimited, stops when exceeded)",
    )

    # Output settings
    save_csv: bool = Field(
        default=True,
        description="Whether to save results to CSV",
    )
    save_json: bool = Field(
        default=False,
        description="Whether to save results to JSON",
    )
    output_dir: str = Field(
        default=".",
        description="Directory to save output files",
    )
