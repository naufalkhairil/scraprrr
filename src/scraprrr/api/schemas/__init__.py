"""
API schemas for request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ============== Flight Schemas ==============


class FlightSearchRequest(BaseModel):
    """Request schema for flight search."""

    origin: str = Field(..., description="Origin airport IATA code (e.g., 'CGK')")
    destination: str = Field(..., description="Destination airport IATA code (e.g., 'DPS')")
    origin_name: Optional[str] = Field(None, description="Origin airport name (optional)")
    destination_name: Optional[str] = Field(None, description="Destination airport name (optional)")
    save_results: bool = Field(
        default=True,
        description="Whether to save results to files",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "origin": "CGK",
                "destination": "DPS",
                "origin_name": "Jakarta",
                "destination_name": "Bali",
                "save_results": True,
            }
        }


class FlightSearchAsyncRequest(FlightSearchRequest):
    """Request schema for async flight search."""

    callback_url: Optional[str] = Field(
        None,
        description="Webhook URL to notify when job completes",
    )


# ============== Hotel Schemas ==============


class HotelSearchRequest(BaseModel):
    """Request schema for hotel search."""

    location: str = Field(..., description="City, hotel, or place name to search")
    save_results: bool = Field(
        default=True,
        description="Whether to save results to files",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "location": "Jakarta",
                "save_results": True,
            }
        }


class HotelSearchAsyncRequest(HotelSearchRequest):
    """Request schema for async hotel search."""

    callback_url: Optional[str] = Field(
        None,
        description="Webhook URL to notify when job completes",
    )


# ============== Common Schemas ==============


class JobStatusResponse(BaseModel):
    """Response schema for job status."""

    job_id: str = Field(..., description="Unique job identifier")
    job_type: str = Field(..., description="Type of job (flight_search/hotel_search)")
    status: str = Field(..., description="Current job status")
    params: Dict[str, Any] = Field(..., description="Job parameters")
    created_at: str = Field(..., description="Job creation timestamp")
    started_at: Optional[str] = Field(None, description="Job start timestamp")
    completed_at: Optional[str] = Field(None, description="Job completion timestamp")
    result: Optional[Any] = Field(None, description="Job result (if completed)")
    error: Optional[str] = Field(None, description="Error message (if failed)")
    progress: int = Field(..., description="Progress percentage (0-100)")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "job_type": "flight_search",
                "status": "completed",
                "params": {"origin": "CGK", "destination": "DPS"},
                "created_at": "2026-03-30T10:00:00",
                "started_at": "2026-03-30T10:00:01",
                "completed_at": "2026-03-30T10:01:00",
                "result": {"total_results": 50},
                "error": None,
                "progress": 100,
            }
        }


class JobListResponse(BaseModel):
    """Response schema for listing jobs."""

    total: int = Field(..., description="Total number of jobs")
    jobs: List[JobStatusResponse] = Field(..., description="List of job summaries")


class HealthCheckResponse(BaseModel):
    """Response schema for health check."""

    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    selenium_connected: bool = Field(..., description="Whether Selenium server is reachable")


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
