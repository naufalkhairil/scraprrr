"""
Custom exceptions for the API.
"""

from fastapi import HTTPException, status


class ScraprrrException(HTTPException):
    """Base exception for Scraprrr API."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict | None = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={"message": message, "details": details or {}},
        )


class JobNotFoundException(ScraprrrException):
    """Raised when a job is not found."""

    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job {job_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class JobStillRunningException(ScraprrrException):
    """Raised when trying to get results from a still-running job."""

    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job {job_id} is still running",
            status_code=status.HTTP_202_ACCEPTED,
            details={"status": "running"},
        )


class ScraperNotInitializedException(ScraprrrException):
    """Raised when scraper is not initialized."""

    def __init__(self):
        super().__init__(
            message="Scraper not initialized. Ensure Selenium server is running.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class InvalidSearchParametersException(ScraprrrException):
    """Raised when search parameters are invalid."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class RateLimitExceededException(ScraprrrException):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after},
        )
