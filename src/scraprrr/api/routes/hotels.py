"""
Hotel API routes with improved timeout handling.
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
    HotelSearchAsyncRequest,
    HotelSearchRequest,
    JobStatusResponse,
)
from scraprrr.modules.hotel import HotelScraper, HotelSearchResult
from scraprrr.modules.hotel.models import HotelScraperConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hotels", tags=["hotels"])

# Timeout for hotel searches (in seconds)
HOTEL_SEARCH_TIMEOUT = 120  # 2 minutes


def _validate_hotel_request(request: HotelSearchRequest) -> None:
    """Validate hotel search request parameters."""
    if not request.location or len(request.location.strip()) == 0:
        raise InvalidSearchParametersException("Location cannot be empty")


def _execute_hotel_search_sync(
    request: HotelSearchRequest,
    selenium_url: str,
    job_info: Any = None,
) -> Dict[str, Any]:
    """
    Execute hotel search synchronously (runs in thread pool).
    
    This function is blocking and should be run in a thread pool executor.
    """
    logger.info(f"Starting hotel search: {request.location}")
    
    config = HotelScraperConfig(
        selenium_remote_url=selenium_url,
        save_csv=True,
        save_json=True,
        scroll_enabled=True,
        scroll_timeout=60,
        max_hotels=100,
    )

    scraper = None
    try:
        if job_info:
            job_info.progress = 30
            logger.info(f"Job progress: 30% - Initializing scraper")
        
        scraper = HotelScraper(config)
        scraper.initialize()
        
        if job_info:
            job_info.progress = 40
            logger.info(f"Job progress: 40% - Scraper initialized")
        
        result = scraper.search(
            location=request.location,
            save_results=request.save_results,
        )
        
        if job_info:
            job_info.progress = 80
            logger.info(f"Job progress: 80% - Search completed, {result.total_results} results")

        if result.status == "error":
            logger.error(f"Search returned error: {result.error_message}")
            raise RuntimeError(result.error_message or "Search failed")

        logger.info(f"Hotel search completed successfully: {result.total_results} hotels")
        return result.to_dict()

    except Exception as e:
        logger.error(f"Hotel search failed: {e}", exc_info=True)
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
    response_model=HotelSearchResult,
    summary="Search Hotels (Synchronous)",
    description="Search for hotels in a location. This is a synchronous operation that may take 30-60 seconds.",
)
async def search_hotels(request: HotelSearchRequest) -> HotelSearchResult:
    """
    Search for hotels synchronously.

    **Note:** This operation blocks until the search completes (30-60 seconds).
    For non-blocking searches, use the `/search/async` endpoint.
    """
    _validate_hotel_request(request)

    config = HotelScraperConfig(
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
                lambda: HotelScraper(config).search(
                    location=request.location,
                    save_results=request.save_results,
                )
            ),
            timeout=HOTEL_SEARCH_TIMEOUT
        )

        if result.status == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Hotel search failed",
                    "error": result.error_message,
                },
            )

        return result

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={"message": f"Hotel search timed out after {HOTEL_SEARCH_TIMEOUT} seconds"},
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": str(e)},
        )
    except Exception as e:
        logger.error(f"Hotel search failed: {e}")
        raise ScraperNotInitializedException()


@router.post(
    "/search/async",
    response_model=JobStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Search Hotels (Asynchronous)",
    description="Start an asynchronous hotel search job. Use the returned job_id to check status and retrieve results.",
)
async def search_hotels_async(
    request: HotelSearchAsyncRequest,
    x_session_id: str = Header(None, alias="X-Session-ID"),
) -> JobStatusResponse:
    """
    Search for hotels asynchronously.

    Returns immediately with a job_id. Use `/jobs/{job_id}` to check status.
    """
    _validate_hotel_request(request)

    job_info = job_manager.create_job(
        job_type="hotel_search",
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
                    lambda: _execute_hotel_search_sync(request, "http://localhost:4444/wd/hub", job_info)
                ),
                timeout=HOTEL_SEARCH_TIMEOUT
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Hotel search timed out after {HOTEL_SEARCH_TIMEOUT} seconds")
            raise TimeoutError(f"Search timed out after {HOTEL_SEARCH_TIMEOUT} seconds")

    await job_manager.submit(
        job_info.job_id,
        run_with_timeout,
    )

    return JobStatusResponse(**job_info.to_dict())


@router.get(
    "/job/{job_id}",
    response_model=JobStatusResponse,
    summary="Get Hotel Job Status",
    description="Get the status and results of a hotel search job.",
)
async def get_hotel_job(job_id: str) -> JobStatusResponse:
    """Get status and results for a hotel search job."""
    job_info = job_manager.get_job(job_id)

    if not job_info:
        raise JobNotFoundException(job_id)

    # Always return job status, even if running
    return JobStatusResponse(**job_info.to_dict())


@router.delete(
    "/job/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel Hotel Job",
    description="Cancel a running hotel search job.",
)
async def cancel_hotel_job(job_id: str) -> None:
    """Cancel a running hotel search job."""
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
    "/popular-destinations",
    summary="List Popular Destinations",
    description="Get list of popular hotel destinations.",
)
async def list_popular_destinations() -> Dict[str, str]:
    """
    Get list of popular hotel destinations.

    Returns a dictionary mapping destination IDs to display names.
    """
    return {
        "jakarta": "Jakarta, Indonesia",
        "bali": "Bali, Indonesia",
        "bandung": "Bandung, Indonesia",
        "yogyakarta": "Yogyakarta, Indonesia",
        "surabaya": "Surabaya, Indonesia",
        "singapore": "Singapore",
        "kuala-lumpur": "Kuala Lumpur, Malaysia",
        "bangkok": "Bangkok, Thailand",
        "tokyo": "Tokyo, Japan",
        "seoul": "Seoul, South Korea",
    }
