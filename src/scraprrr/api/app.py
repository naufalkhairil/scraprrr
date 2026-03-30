"""
FastAPI application factory.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scraprrr import __version__
from scraprrr.api.core.config import get_settings
from scraprrr.api.core.job_manager import job_manager
from scraprrr.api.routes import flights_router, hotels_router, jobs_router

logger = logging.getLogger(__name__)

settings = get_settings()


def check_selenium_connection(selenium_url: str) -> bool:
    """Check if Selenium server is reachable."""
    try:
        response = requests.get(selenium_url.replace("/wd/hub", "/status"), timeout=5)
        return response.status_code == 200
    except Exception:
        return False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Scraprrr API starting up...")
    logger.info(f"Selenium URL: {settings.selenium_remote_url}")

    selenium_connected = check_selenium_connection(settings.selenium_remote_url)
    if selenium_connected:
        logger.info("✓ Selenium server is connected")
    else:
        logger.warning("✗ Selenium server is not reachable")

    yield

    # Shutdown
    logger.info("Scraprrr API shutting down...")

    # Clean up any running jobs
    cancelled_count = 0
    for job in job_manager.get_jobs_by_status("running"):
        await job_manager.cancel_job(job.job_id)
        cancelled_count += 1

    if cancelled_count > 0:
        logger.info(f"Cancelled {cancelled_count} running jobs")

    logger.info("Scraprrr API shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Include routers
    app.include_router(flights_router, prefix="/api/v1")
    app.include_router(hotels_router, prefix="/api/v1")
    app.include_router(jobs_router, prefix="/api/v1")

    # Health check endpoint
    @app.get(
        "/health",
        tags=["health"],
        summary="Health Check",
        description="Check API health status and Selenium connection.",
    )
    async def health_check() -> dict:
        """Health check endpoint."""
        selenium_connected = check_selenium_connection(settings.selenium_remote_url)

        return {
            "status": "healthy" if selenium_connected else "degraded",
            "version": __version__,
            "timestamp": datetime.now().isoformat(),
            "selenium_connected": selenium_connected,
            "selenium_url": settings.selenium_remote_url,
        }

    # Root endpoint
    @app.get(
        "/",
        tags=["root"],
        summary="API Root",
        description="Welcome message and API information.",
    )
    async def root() -> dict:
        """Root endpoint with API information."""
        return {
            "name": settings.title,
            "version": settings.version,
            "description": settings.description,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        }

    return app


# Create app instance
app = create_app()
