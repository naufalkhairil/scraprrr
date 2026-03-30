"""
CLI entry point for the Scraprrr API server.

Usage:
    scraprrr-serve --host 0.0.0.0 --port 8000 --workers 4
"""

import logging
import os
import sys

import click
import uvicorn

from scraprrr import __version__


@click.command()
@click.option(
    "--host",
    "-h",
    default="0.0.0.0",
    help="Host to bind the server to (default: 0.0.0.0)",
)
@click.option(
    "--port",
    "-p",
    default=8000,
    help="Port to bind the server to (default: 8000)",
)
@click.option(
    "--reload",
    "-r",
    is_flag=True,
    default=False,
    help="Enable auto-reload for development",
)
@click.option(
    "--workers",
    "-w",
    default=1,
    help="Number of worker processes (default: 1). Use multiple workers for production.",
)
@click.option(
    "--log-level",
    "-l",
    default="info",
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
    help="Logging level (default: info)",
)
@click.option(
    "--selenium-url",
    default="http://localhost:4444/wd/hub",
    help="Selenium Grid URL (default: http://localhost:4444/wd/hub)",
)
@click.option(
    "--max-jobs",
    default=5,
    help="Maximum concurrent scraping jobs (default: 5)",
)
@click.version_option(version=__version__, prog_name="Scraprrr API Server")
def main(
    host: str,
    port: int,
    reload: bool,
    workers: int,
    log_level: str,
    selenium_url: str,
    max_jobs: int,
) -> None:
    """
    Start the Scraprrr API server.

    This command starts a FastAPI server that provides REST endpoints
    for scraping flights and hotels from Traveloka.

    Examples:

        # Start server on default port (development)
        scraprrr-serve

        # Start server with auto-reload (development)
        scraprrr-serve --reload

        # Start server with multiple workers (production)
        scraprrr-serve --workers 4

        # Start server on custom host/port
        scraprrr-serve --host 0.0.0.0 --port 8080

        # Start with custom Selenium URL
        scraprrr-serve --selenium-url http://selenium:4444/wd/hub

        # Configure max concurrent jobs
        scraprrr-serve --max-jobs 10

    Worker Configuration:

        - Development: Use --reload --workers 1
        - Production: Use --workers 4 (or more based on CPU cores)
        - Each worker can handle --max-jobs concurrent scraping operations

        Note: When using multiple workers, jobs are NOT shared between workers.
        For production with multiple workers, consider using Redis for job storage.
    """
    # Set environment variables
    os.environ["SELENIUM_REMOTE_URL"] = selenium_url
    os.environ["SCRAPRRR_MAX_JOBS"] = str(max_jobs)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    logger = logging.getLogger("scraprrr.api")
    logger.info(f"Starting Scraprrr API server v{__version__}")
    logger.info(f"Host: {host}, Port: {port}, Workers: {workers}, Max Jobs: {max_jobs}")
    logger.info(f"Selenium URL: {selenium_url}")
    logger.info(f"API docs available at: http://{host}:{port}/docs")

    if reload and workers > 1:
        logger.warning("Reload mode enabled - forcing workers=1 (reload only works with 1 worker)")
        workers = 1

    uvicorn.run(
        "scraprrr.api.app:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level=log_level,
    )


if __name__ == "__main__":
    main()
