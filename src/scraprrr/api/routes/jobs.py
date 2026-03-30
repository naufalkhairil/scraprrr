"""
Job management API routes with session support.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Header

from scraprrr.api.core.exceptions import JobNotFoundException
from scraprrr.api.core.job_manager import JobStatus, job_manager
from scraprrr.api.schemas import JobListResponse, JobStatusResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get(
    "",
    response_model=JobListResponse,
    summary="List All Jobs",
    description="Get a list of all scraping jobs with their current status. Filtered by session if X-Session-ID header is provided.",
)
async def list_jobs(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
) -> JobListResponse:
    """
    List all jobs, optionally filtered by session.
    
    Args:
        x_session_id: Optional session ID to filter jobs. If provided, only jobs
                     for that session will be returned.
    """
    if x_session_id:
        jobs = job_manager.get_session_jobs(x_session_id)
        logger.debug(f"Listing jobs for session {x_session_id}: {len(jobs)} jobs")
    else:
        jobs = job_manager.get_all_jobs()
        logger.debug(f"Listing all jobs: {len(jobs)} jobs")
    
    return JobListResponse(
        total=len(jobs),
        jobs=[JobStatusResponse(**job.to_dict()) for job in jobs],
    )


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    summary="Get Job Status",
    description="Get the status of any scraping job by ID.",
)
async def get_job(job_id: str) -> JobStatusResponse:
    """Get status for any job."""
    job_info = job_manager.get_job(job_id)

    if not job_info:
        raise JobNotFoundException(job_id)

    return JobStatusResponse(**job_info.to_dict())


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel Job",
    description="Cancel any running scraping job by ID.",
)
async def cancel_job(job_id: str) -> None:
    """Cancel any running job."""
    job_info = job_manager.get_job(job_id)

    if not job_info:
        raise JobNotFoundException(job_id)

    success = await job_manager.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Job cannot be cancelled (already completed or failed)"},
        )


@router.post(
    "/cleanup",
    summary="Cleanup Old Jobs",
    description="Remove completed/failed jobs older than specified age.",
)
async def cleanup_jobs(
    max_age_seconds: int = 3600,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
) -> dict:
    """
    Clean up old completed jobs.
    
    Args:
        max_age_seconds: Maximum age of jobs to keep (default: 1 hour)
        x_session_id: Optional session ID to clean up only that session's jobs
    """
    deleted_count = job_manager.cleanup_old_jobs(
        max_age_seconds=max_age_seconds,
        session_id=x_session_id,
    )
    return {
        "message": f"Cleaned up {deleted_count} old jobs",
        "deleted_count": deleted_count,
    }


@router.get(
    "/stats",
    summary="Get Job Statistics",
    description="Get statistics about all jobs.",
)
async def get_job_stats(
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
) -> dict:
    """
    Get job statistics.
    
    Args:
        x_session_id: Optional session ID to get stats for that session only
    """
    if x_session_id:
        jobs = job_manager.get_session_jobs(x_session_id)
    else:
        jobs = job_manager.get_all_jobs()

    stats = {
        "total_jobs": len(jobs),
        "by_status": {
            "pending": len([j for j in jobs if j.status == JobStatus.PENDING]),
            "running": len([j for j in jobs if j.status == JobStatus.RUNNING]),
            "completed": len([j for j in jobs if j.status == JobStatus.COMPLETED]),
            "failed": len([j for j in jobs if j.status == JobStatus.FAILED]),
            "cancelled": len([j for j in jobs if j.status == JobStatus.CANCELLED]),
        },
        "by_type": {},
    }

    for job in jobs:
        job_type = job.job_type
        if job_type not in stats["by_type"]:
            stats["by_type"][job_type] = 0
        stats["by_type"][job_type] += 1

    return stats
