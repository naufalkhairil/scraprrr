"""
Flight API routes with improved timeout handling.
"""

import asyncio
import logging
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Header

from scraprrr.api.core.exceptions import (
    InvalidSearchParametersException,
    JobNotFoundException,
    JobStillRunningException,
    ScraperNotInitializedException,
)
from scraprrr.api.core.job_manager import JobStatus, job_manager
from scraprrr.api.schemas import (
    FlightSearchAsyncRequest,
    FlightSearchRequest,
    JobStatusResponse,
)
from scraprrr.modules.flight import FlightScraper, FlightSearchResult
from scraprrr.modules.flight.models import FlightScraperConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/flights", tags=["flights"])

# Timeout for flight searches (in seconds)
FLIGHT_SEARCH_TIMEOUT = 120  # 2 minutes


def _validate_flight_request(request: FlightSearchRequest) -> None:
    """Validate flight search request parameters."""
    if not request.origin or len(request.origin) != 3:
        raise InvalidSearchParametersException(
            "Origin must be a 3-letter IATA airport code"
        )

    if not request.destination or len(request.destination) != 3:
        raise InvalidSearchParametersException(
            "Destination must be a 3-letter IATA airport code"
        )

    if request.origin == request.destination:
        raise InvalidSearchParametersException(
            "Origin and destination cannot be the same"
        )


def _execute_flight_search_sync(
    request: FlightSearchRequest,
    selenium_url: str,
    job_info: Any = None,
) -> Dict[str, Any]:
    """
    Execute flight search synchronously (runs in thread pool).
    
    This function is blocking and should be run in a thread pool executor.
    """
    logger.info(f"Starting flight search: {request.origin} → {request.destination}")
    
    config = FlightScraperConfig(
        selenium_remote_url=selenium_url,
        save_csv=True,
        save_json=True,
        scroll_enabled=True,
        scroll_timeout=60,
    )

    scraper = None
    try:
        if job_info:
            job_info.progress = 30
            logger.info(f"Job progress: 30% - Initializing scraper")
        
        scraper = FlightScraper(config)
        scraper.initialize()
        
        if job_info:
            job_info.progress = 40
            logger.info(f"Job progress: 40% - Scraper initialized")
        
        result = scraper.search(
            origin=request.origin,
            destination=request.destination,
            origin_name=request.origin_name,
            destination_name=request.destination_name,
            save_results=request.save_results,
        )
        
        if job_info:
            job_info.progress = 80
            logger.info(f"Job progress: 80% - Search completed, {result.total_results} results")

        if result.status == "error":
            logger.error(f"Search returned error: {result.error_message}")
            raise RuntimeError(result.error_message or "Search failed")

        logger.info(f"Flight search completed successfully: {result.total_results} tickets")
        return result.to_dict()

    except Exception as e:
        logger.error(f"Flight search failed: {e}", exc_info=True)
        raise
    finally:
        # Ensure scraper is closed
        if scraper and scraper.driver:
            try:
                scraper.close()
                logger.info("Scraper closed successfully")
            except Exception as e:
                logger.warning(f"Error closing scraper: {e}")
        
        if job_info:
            job_info.progress = 90


@router.post(
    "/search",
    response_model=FlightSearchResult,
    summary="Search Flights (Synchronous)",
    description="Search for flights between origin and destination. This is a synchronous operation that may take 30-60 seconds.",
)
async def search_flights(request: FlightSearchRequest) -> FlightSearchResult:
    """
    Search for flights synchronously.

    **Note:** This operation blocks until the search completes (30-60 seconds).
    For non-blocking searches, use the `/search/async` endpoint.
    """
    _validate_flight_request(request)

    config = FlightScraperConfig(
        selenium_remote_url="http://localhost:4444/wd/hub",
        save_csv=request.save_results,
        save_json=request.save_results,
    )

    try:
        # Run blocking scraper in thread pool with timeout
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(
                job_manager._executor,
                lambda: FlightScraper(config).search(
                    origin=request.origin,
                    destination=request.destination,
                    origin_name=request.origin_name,
                    destination_name=request.destination_name,
                    save_results=request.save_results,
                )
            ),
            timeout=FLIGHT_SEARCH_TIMEOUT
        )

        if result.status == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Flight search failed",
                    "error": result.error_message,
                },
            )

        return result

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"message": f"Flight search timed out after {FLIGHT_SEARCH_TIMEOUT} seconds"},
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e)},
        )
    except Exception as e:
        logger.error(f"Flight search failed: {e}")
        raise ScraperNotInitializedException()


@router.post(
    "/search/async",
    response_model=JobStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Search Flights (Asynchronous)",
    description="Start an asynchronous flight search job. Use the returned job_id to check status and retrieve results.",
)
async def search_flights_async(
    request: FlightSearchAsyncRequest,
    x_session_id: str = Header(None, alias="X-Session-ID"),
) -> JobStatusResponse:
    """
    Search for flights asynchronously.

    Returns immediately with a job_id. Use `/jobs/{job_id}` to check status.
    """
    _validate_flight_request(request)

    job_info = job_manager.create_job(
        job_type="flight_search",
        params=request.model_dump(),
        session_id=x_session_id,
    )

    # Submit job to run in thread pool with timeout
    async def run_with_timeout():
        try:
            # Run blocking scraper in thread pool
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    job_manager._executor,
                    lambda: _execute_flight_search_sync(request, "http://localhost:4444/wd/hub", job_info)
                ),
                timeout=FLIGHT_SEARCH_TIMEOUT
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Flight search timed out after {FLIGHT_SEARCH_TIMEOUT} seconds")
            raise TimeoutError(f"Search timed out after {FLIGHT_SEARCH_TIMEOUT} seconds")

    await job_manager.submit(
        job_info.job_id,
        run_with_timeout,
    )

    return JobStatusResponse(**job_info.to_dict())


@router.get(
    "/job/{job_id}",
    response_model=JobStatusResponse,
    summary="Get Flight Job Status",
    description="Get the status and results of a flight search job.",
)
async def get_flight_job(job_id: str) -> JobStatusResponse:
    """Get status and results for a flight search job."""
    job_info = job_manager.get_job(job_id)

    if not job_info:
        raise JobNotFoundException(job_id)

    # Always return job status, even if running
    return JobStatusResponse(**job_info.to_dict())


@router.delete(
    "/job/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel Flight Job",
    description="Cancel a running flight search job.",
)
async def cancel_flight_job(job_id: str) -> None:
    """Cancel a running flight search job."""
    job_info = job_manager.get_job(job_id)

    if not job_info:
        raise JobNotFoundException(job_id)

    success = await job_manager.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Job cannot be cancelled (already completed or failed)"},
        )


@router.get(
    "/airports",
    summary="List Airports",
    description="Get list of supported airports with IATA codes.",
)
async def list_airports() -> Dict[str, str]:
    """
    Get list of supported airports.

    Returns a dictionary mapping IATA codes to airport names.
    """
    return {
        "CGK": "Soekarno-Hatta International Airport (Jakarta)",
        "DPS": "Ngurah Rai International Airport (Bali)",
        "SUB": "Juanda International Airport (Surabaya)",
        "SIN": "Changi Airport (Singapore)",
        "KUL": "Kuala Lumpur International Airport",
        "BKK": "Suvarnabhumi Airport (Bangkok)",
        "HND": "Haneda Airport (Tokyo)",
        "NRT": "Narita International Airport (Tokyo)",
        "ICN": "Incheon International Airport (Seoul)",
        "MNL": "Ninoy Aquino International Airport (Manila)",
    }
