"""
Pydantic data models for Traveloka flight data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from scraprrr.core.utils import ScraperConfig as BaseScraperConfig


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

    airline_name: str = Field(..., description="Name of the airline")
    airline_logo: Optional[str] = Field(None, description="URL to airline logo")

    departure_time: str = Field(..., description="Departure time")
    departure_airport: str = Field(..., description="Departure airport code")
    arrival_time: str = Field(..., description="Arrival time")
    arrival_airport: str = Field(..., description="Arrival airport code")
    duration: str = Field(..., description="Flight duration")
    flight_type: str = Field(..., description="Flight type (Direct/Transit)")

    price: str = Field(..., description="Current ticket price")
    original_price: Optional[str] = Field(None, description="Original price before discount")

    baggage: str = Field(..., description="Baggage allowance information")
    promos: List[str] = Field(default_factory=list, description="List of active promotions")
    special_tag: Optional[str] = Field(None, description="Special tag")
    highlight_label: Optional[str] = Field(None, description="Highlight label")

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

    origin: AirportInfo = Field(..., description="Origin airport")
    destination: AirportInfo = Field(..., description="Destination airport")
    search_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the search was performed",
    )

    status: str = Field(..., description="Search status ('success' or 'error')")
    total_results: int = Field(..., description="Number of flights found")
    tickets: List[FlightTicket] = Field(
        default_factory=list,
        description="List of flight tickets",
    )
    error_message: Optional[str] = Field(None, description="Error message if search failed")
    raw_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Raw extracted data before validation",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the search result to a dictionary."""
        return self.model_dump()

    def to_dataframe_data(self) -> List[Dict[str, Any]]:
        """Convert tickets to DataFrame-compatible format."""
        return [ticket.model_dump() for ticket in self.tickets]


class FlightScraperConfig(BaseScraperConfig):
    """Configuration for the FlightScraper."""

    max_tickets: int = Field(
        default=0,
        description="Maximum tickets threshold (0 for unlimited)",
    )
