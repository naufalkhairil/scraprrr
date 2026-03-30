"""
Pydantic data models for Traveloka hotel data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from scraprrr.core.utils import ScraperConfig as BaseScraperConfig


class HotelLocation(BaseModel):
    """Information about hotel location."""

    address: str = Field(..., description="Hotel address or area")
    city: Optional[str] = Field(None, description="City name")


class Hotel(BaseModel):
    """Complete hotel information extracted from Traveloka."""

    hotel_name: str = Field(..., description="Name of the hotel")
    location: str = Field(..., description="Hotel location/area")
    star_rating: Optional[int] = Field(None, description="Hotel star rating (1-5)")

    rating_score: Optional[str] = Field(None, description="Guest rating score")
    review_count: Optional[str] = Field(None, description="Number of reviews")

    main_image_url: Optional[str] = Field(None, description="URL to main hotel image")
    supporting_images: List[str] = Field(default_factory=list, description="Supporting image URLs")

    original_price: Optional[str] = Field(None, description="Original price before discount")
    price: Optional[str] = Field(None, description="Current price")
    total_price: Optional[str] = Field(None, description="Total price with taxes")

    booking_info: Optional[str] = Field(None, description="Booking activity info")
    hotel_type: Optional[str] = Field(None, description="Type of accommodation")
    ranking: Optional[str] = Field(None, description="Ranking badge")
    features: List[str] = Field(default_factory=list, description="Hotel features/amenities")

    extracted_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the hotel was extracted",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "hotel_name": "Mercure Jakarta Gatot Subroto",
                "location": "Gatot Subroto, South Jakarta",
                "star_rating": 4,
                "rating_score": "8.8/10",
                "review_count": "Very Good",
                "price": "Rp 990.000",
                "total_price": "Total Rp 1.197.900 for 1 room",
                "booking_info": "Booked 8 times",
                "hotel_type": "Hotels",
                "features": ["Express check-out", "Fitness center"],
                "extracted_at": "2026-03-26T10:00:00",
            }
        }
    )


class HotelSearchResult(BaseModel):
    """Result of a hotel search operation."""

    location: str = Field(..., description="Search location")
    search_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the search was performed",
    )

    status: str = Field(..., description="Search status ('success' or 'error')")
    total_results: int = Field(..., description="Number of hotels found")
    hotels: List[Hotel] = Field(
        default_factory=list,
        description="List of hotels",
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
        """Convert hotels to DataFrame-compatible format."""
        return [hotel.model_dump() for hotel in self.hotels]


class HotelScraperConfig(BaseScraperConfig):
    """Configuration for the HotelScraper."""

    max_hotels: int = Field(
        default=100,
        description="Maximum hotels to collect (0 for unlimited)",
    )
