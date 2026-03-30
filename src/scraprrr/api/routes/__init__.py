"""
API routes.
"""

from scraprrr.api.routes.flights import router as flights_router
from scraprrr.api.routes.hotels import router as hotels_router
from scraprrr.api.routes.jobs import router as jobs_router

__all__ = ["flights_router", "hotels_router", "jobs_router"]
