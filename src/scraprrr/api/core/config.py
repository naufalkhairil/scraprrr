"""
FastAPI application configuration.
"""

from pydantic import BaseModel


class APISettings(BaseModel):
    """API settings configuration."""

    title: str = "Scraprrr API"
    description: str = "REST API for Traveloka flight and hotel scraping"
    version: str = "1.0.0"
    debug: bool = False
    
    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # Job settings
    max_concurrent_jobs: int = 5
    job_result_ttl: int = 3600  # Results kept for 1 hour
    
    # Selenium settings
    selenium_remote_url: str = "http://localhost:4444/wd/hub"
    
    class Config:
        frozen = True


def get_settings() -> APISettings:
    """Get API settings."""
    return APISettings()
