"""
Pydantic data models for Traveloka hotel data.

This module provides structured data models for representing hotel search
parameters, results, and hotel information with validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HotelLocation(BaseModel):
    """Information about hotel location."""

    address: str = Field(..., description="Hotel address or area")
    city: Optional[str] = Field(None, description="City name")


class Hotel(BaseModel):
    """Complete hotel information extracted from Traveloka."""

    # Basic information
    hotel_name: str = Field(..., description="Name of the hotel")
    location: str = Field(..., description="Hotel location/area")
    star_rating: Optional[int] = Field(None, description="Hotel star rating (1-5)")

    # Ratings and reviews
    rating_score: Optional[str] = Field(None, description="Guest rating score (e.g., '8.8/10')")
    review_count: Optional[str] = Field(None, description="Number of reviews (e.g., '3,4K reviews')")

    # Images
    main_image_url: Optional[str] = Field(None, description="URL to main hotel image")
    supporting_images: List[str] = Field(default_factory=list, description="List of supporting image URLs")

    # Pricing
    original_price: Optional[str] = Field(None, description="Original price before discount")
    price: Optional[str] = Field(None, description="Current price")
    total_price: Optional[str] = Field(None, description="Total price with taxes and fees")

    # Additional information
    booking_info: Optional[str] = Field(None, description="Booking activity info (e.g., 'Booked 8 times')")
    hotel_type: Optional[str] = Field(None, description="Type of accommodation")
    ranking: Optional[str] = Field(None, description="Ranking badge (e.g., 'No. 5 in Hotel with City View')")
    features: List[str] = Field(default_factory=list, description="List of hotel features/amenities")

    # Metadata
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
                "main_image_url": "https://example.com/hotel.jpg",
                "supporting_images": ["https://example.com/img1.jpg"],
                "original_price": "Rp 1.320.000",
                "price": "Rp 990.000",
                "total_price": "Total Rp 1.197.900 for 1 room",
                "booking_info": "Booked 8 times",
                "hotel_type": "Hotels",
                "ranking": "No. 5 in Hotel with City View",
                "features": ["Express check-out", "Fitness center"],
                "extracted_at": "2026-03-26T10:00:00",
            }
        }
    )


class HotelSearchResult(BaseModel):
    """Result of a hotel search operation."""

    # Search parameters
    location: str = Field(..., description="Search location")
    search_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the search was performed",
    )

    # Results
    status: str = Field(..., description="Search status ('success' or 'error')")
    total_results: int = Field(..., description="Number of hotels found")
    hotels: List[Hotel] = Field(
        default_factory=list,
        description="List of hotels",
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
        Convert hotels to a format suitable for DataFrame creation.

        Returns:
            List of dictionaries, one per hotel.
        """
        return [hotel.model_dump() for hotel in self.hotels]


class HotelScraperConfig(BaseModel):
    """Configuration for the TravelokaHotelScraper."""

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
        description="Whether to scroll to load more hotels",
    )
    scroll_timeout: int = Field(
        default=60,
        description="Maximum time in seconds to scroll",
    )
    scroll_pause: float = Field(
        default=2.0,
        description="Time to wait between scrolls in seconds",
    )
    max_hotels: int = Field(
        default=100,
        description="Maximum hotels to collect (0 for unlimited)",
    )
    num_scrolls: int = Field(
        default=20,
        description="Maximum number of scrolls to perform",
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
