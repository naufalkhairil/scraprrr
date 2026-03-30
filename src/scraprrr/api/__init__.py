"""
FastAPI backend for Scraprrr.

This module provides a REST API for flight and hotel scraping operations.
"""

from scraprrr.api.app import create_app, app

__all__ = ["create_app", "app"]
