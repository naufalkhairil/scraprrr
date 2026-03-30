"""
Background job manager for async scraping operations.

Supports:
- Thread pool execution for blocking scraper code
- Session-based job isolation
- Concurrent job management with semaphores
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import uuid

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobInfo:
    """Information about a background job."""

    def __init__(
        self,
        job_id: str,
        job_type: str,
        session_id: str,
        status: JobStatus = JobStatus.PENDING,
        params: Optional[Dict[str, Any]] = None,
    ):
        self.job_id = job_id
        self.job_type = job_type
        self.session_id = session_id
        self.status = status
        self.params = params or {}
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Any = None
        self.error: Optional[str] = None
        self.progress: int = 0  # 0-100 percentage

    def to_dict(self) -> Dict[str, Any]:
        """Convert job info to dictionary."""
        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "session_id": self.session_id,
            "status": self.status.value,
            "params": self.params,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "progress": self.progress,
        }


class JobManager:
    """
    Manages background scraping jobs with thread pool execution.
    
    Features:
    - Thread pool for blocking scraper operations
    - Session-based job isolation
    - Concurrent job limiting with semaphores
    - Job cancellation support
    """

    def __init__(self, max_concurrent_jobs: int = 5):
        self.max_concurrent_jobs = max_concurrent_jobs
        self._jobs: Dict[str, JobInfo] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent_jobs)
        
        # Thread pool executor for blocking scraper code
        self._executor = ThreadPoolExecutor(
            max_workers=max_concurrent_jobs,
            thread_name_prefix="scraper_worker"
        )
        
        logger.info(f"JobManager initialized with max {max_concurrent_jobs} concurrent jobs")

    def create_job(
        self,
        job_type: str,
        params: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> JobInfo:
        """
        Create a new job.
        
        Args:
            job_type: Type of job (e.g., 'flight_search', 'hotel_search')
            params: Job parameters
            session_id: Optional session ID for job isolation
            
        Returns:
            Created JobInfo object
        """
        job_id = str(uuid.uuid4())
        job_info = JobInfo(
            job_id=job_id,
            job_type=job_type,
            session_id=session_id or "default",
            params=params,
        )
        self._jobs[job_id] = job_info
        logger.info(f"Created job {job_id} of type {job_type} for session {job_info.session_id}")
        return job_info

    def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Get job information by ID."""
        return self._jobs.get(job_id)

    def get_all_jobs(self) -> List[JobInfo]:
        """Get all jobs."""
        return list(self._jobs.values())

    def get_session_jobs(self, session_id: str) -> List[JobInfo]:
        """Get jobs for a specific session."""
        return [job for job in self._jobs.values() if job.session_id == session_id]

    def get_jobs_by_status(self, status: JobStatus) -> List[JobInfo]:
        """Get jobs filtered by status."""
        return [job for job in self._jobs.values() if job.status == status]

    async def submit(
        self,
        job_id: str,
        scraper_func: Callable,
        *args,
        **kwargs,
    ) -> None:
        """
        Submit a job for execution in thread pool.
        
        Args:
            job_id: Job ID to execute
            scraper_func: Async function that runs scraper in thread pool
            *args: Arguments to pass to scraper function
            **kwargs: Keyword arguments to pass to scraper function
        """
        if job_id not in self._jobs:
            raise ValueError(f"Job {job_id} not found")

        job_info = self._jobs[job_id]

        async def run_job():
            async with self._semaphore:
                try:
                    job_info.status = JobStatus.RUNNING
                    job_info.started_at = datetime.now()
                    job_info.progress = 10
                    logger.info(f"Job {job_id} started in thread pool")

                    # Run the async function (which internally uses run_in_executor)
                    result = await scraper_func(*args, **kwargs)

                    job_info.status = JobStatus.COMPLETED
                    job_info.result = result
                    job_info.progress = 100
                    logger.info(f"Job {job_id} completed successfully")

                except asyncio.CancelledError:
                    job_info.status = JobStatus.CANCELLED
                    job_info.error = "Job was cancelled"
                    job_info.progress = 0
                    logger.info(f"Job {job_id} cancelled")
                    raise

                except asyncio.TimeoutError as e:
                    job_info.status = JobStatus.FAILED
                    job_info.error = f"Job timed out: {str(e)}"
                    job_info.progress = 0
                    logger.error(f"Job {job_id} timed out: {e}")

                except Exception as e:
                    job_info.status = JobStatus.FAILED
                    job_info.error = str(e)
                    job_info.progress = 0
                    logger.error(f"Job {job_id} failed: {e}", exc_info=True)

                finally:
                    job_info.completed_at = datetime.now()
                    if job_id in self._running_tasks:
                        del self._running_tasks[job_id]

        task = asyncio.create_task(run_job())
        self._running_tasks[job_id] = task

    def _run_scraper_with_progress(
        self,
        scraper_func: Callable,
        job_info: JobInfo,
        *args,
        **kwargs,
    ) -> Any:
        """
        Run scraper function with progress updates.
        
        This wraps the blocking scraper call to provide progress feedback.
        """
        try:
            job_info.progress = 25  # Starting scraper
            result = scraper_func(*args, **kwargs)
            job_info.progress = 90  # Completed, processing result
            return result
        finally:
            job_info.progress = 100  # Done

    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job.
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            True if job was cancelled, False otherwise
        """
        if job_id not in self._jobs:
            return False

        job_info = self._jobs[job_id]

        if job_info.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
            logger.debug(f"Job {job_id} cannot be cancelled (status: {job_info.status})")
            return False

        if job_id in self._running_tasks:
            logger.info(f"Cancelling job {job_id}")
            self._running_tasks[job_id].cancel()
            try:
                await self._running_tasks[job_id]
            except asyncio.CancelledError:
                pass

        job_info.status = JobStatus.CANCELLED
        job_info.completed_at = datetime.now()
        return True

    def delete_job(self, job_id: str) -> bool:
        """Delete a job from the manager."""
        if job_id in self._jobs:
            del self._jobs[job_id]
            logger.info(f"Job {job_id} deleted")
            return True
        return False

    def cleanup_old_jobs(
        self,
        max_age_seconds: int = 3600,
        session_id: Optional[str] = None,
    ) -> int:
        """
        Clean up old completed jobs.
        
        Args:
            max_age_seconds: Maximum age of jobs to keep
            session_id: Optional session ID to filter jobs
            
        Returns:
            Number of jobs deleted
        """
        now = datetime.now()
        to_delete = []

        for job_id, job_info in self._jobs.items():
            # Filter by session if specified
            if session_id and job_info.session_id != session_id:
                continue
                
            if job_info.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                completed_at = job_info.completed_at or job_info.created_at
                age = (now - completed_at).total_seconds()
                if age > max_age_seconds:
                    to_delete.append(job_id)

        for job_id in to_delete:
            self.delete_job(job_id)

        logger.info(f"Cleaned up {len(to_delete)} old jobs")
        return len(to_delete)

    def get_stats(self) -> Dict[str, Any]:
        """Get job statistics."""
        all_jobs = self.get_all_jobs()

        stats = {
            "total_jobs": len(all_jobs),
            "by_status": {
                "pending": len(self.get_jobs_by_status(JobStatus.PENDING)),
                "running": len(self.get_jobs_by_status(JobStatus.RUNNING)),
                "completed": len(self.get_jobs_by_status(JobStatus.COMPLETED)),
                "failed": len(self.get_jobs_by_status(JobStatus.FAILED)),
                "cancelled": len(self.get_jobs_by_status(JobStatus.CANCELLED)),
            },
            "by_type": {},
        }

        for job in all_jobs:
            job_type = job.job_type
            if job_type not in stats["by_type"]:
                stats["by_type"][job_type] = 0
            stats["by_type"][job_type] += 1

        return stats

    async def shutdown(self) -> None:
        """Shutdown the job manager and cleanup resources."""
        logger.info("Shutting down JobManager...")
        
        # Cancel all running jobs
        cancelled_count = 0
        for job_id in list(self._running_tasks.keys()):
            await self.cancel_job(job_id)
            cancelled_count += 1
        
        # Shutdown thread pool
        self._executor.shutdown(wait=False)
        
        logger.info(f"JobManager shutdown complete. Cancelled {cancelled_count} jobs.")


# Global job manager instance
job_manager = JobManager(max_concurrent_jobs=5)
