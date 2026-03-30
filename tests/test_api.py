"""
Tests for the Scraprrr API.
"""

import pytest
from fastapi.testclient import TestClient

from scraprrr.api.app import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints."""

    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "Scraprrr API"

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "selenium_connected" in data


class TestFlightEndpoints:
    """Test flight API endpoints."""

    def test_list_airports(self):
        """Test listing airports."""
        response = client.get("/api/v1/flights/airports")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "CGK" in data
        assert "DPS" in data

    def test_search_flights_invalid_params(self):
        """Test flight search with invalid parameters."""
        # Missing required fields
        response = client.post("/api/v1/flights/search", json={})
        assert response.status_code == 422  # Validation error

        # Invalid origin code
        response = client.post(
            "/api/v1/flights/search",
            json={"origin": "INVALID", "destination": "DPS"}
        )
        assert response.status_code == 400

        # Same origin and destination
        response = client.post(
            "/api/v1/flights/search",
            json={"origin": "CGK", "destination": "CGK"}
        )
        assert response.status_code == 400

    def test_search_flights_async(self):
        """Test async flight search."""
        response = client.post(
            "/api/v1/flights/search/async",
            json={"origin": "CGK", "destination": "DPS"}
        )
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["job_type"] == "flight_search"
        assert data["status"] in ["pending", "running"]

    def test_get_job_not_found(self):
        """Test getting non-existent job."""
        response = client.get("/api/v1/flights/job/non-existent-id")
        assert response.status_code == 404


class TestHotelEndpoints:
    """Test hotel API endpoints."""

    def test_list_popular_destinations(self):
        """Test listing popular destinations."""
        response = client.get("/api/v1/hotels/popular-destinations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "jakarta" in data
        assert "bali" in data

    def test_search_hotel_invalid_params(self):
        """Test hotel search with invalid parameters."""
        # Empty location
        response = client.post(
            "/api/v1/hotels/search",
            json={"location": ""}
        )
        assert response.status_code == 400

        # Missing location
        response = client.post("/api/v1/hotels/search", json={})
        assert response.status_code == 422

    def test_search_hotels_async(self):
        """Test async hotel search."""
        response = client.post(
            "/api/v1/hotels/search/async",
            json={"location": "Jakarta"}
        )
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["job_type"] == "hotel_search"
        assert data["status"] in ["pending", "running"]


class TestJobManagementEndpoints:
    """Test job management endpoints."""

    def test_list_jobs(self):
        """Test listing all jobs."""
        response = client.get("/api/v1/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "jobs" in data
        assert isinstance(data["jobs"], list)

    def test_get_job_stats(self):
        """Test getting job statistics."""
        response = client.get("/api/v1/jobs/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_jobs" in data
        assert "by_status" in data
        assert "by_type" in data

    def test_cleanup_jobs(self):
        """Test cleaning up old jobs."""
        response = client.post("/api/v1/jobs/cleanup?max_age_seconds=0")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted_count" in data

    def test_job_workflow(self):
        """Test complete job workflow."""
        # Create async job
        response = client.post(
            "/api/v1/flights/search/async",
            json={"origin": "CGK", "destination": "DPS"}
        )
        assert response.status_code == 202
        job_data = response.json()
        job_id = job_data["job_id"]

        # Get job status
        response = client.get(f"/api/v1/jobs/{job_id}")
        assert response.status_code in [200, 202, 404]

        # List all jobs
        response = client.get("/api/v1/jobs")
        assert response.status_code == 200
        assert response.json()["total"] >= 1


class TestSchemas:
    """Test API schemas validation."""

    def test_flight_search_request_schema(self):
        """Test flight search request schema."""
        from scraprrr.api.schemas import FlightSearchRequest

        # Valid request
        request = FlightSearchRequest(
            origin="CGK",
            destination="DPS"
        )
        assert request.origin == "CGK"
        assert request.destination == "DPS"
        assert request.save_results is True

    def test_hotel_search_request_schema(self):
        """Test hotel search request schema."""
        from scraprrr.api.schemas import HotelSearchRequest

        # Valid request
        request = HotelSearchRequest(
            location="Jakarta"
        )
        assert request.location == "Jakarta"
        assert request.save_results is True

    def test_job_status_response_schema(self):
        """Test job status response schema."""
        from scraprrr.api.core.job_manager import JobInfo, JobStatus

        job_info = JobInfo(
            job_id="test-id",
            job_type="flight_search",
            status=JobStatus.COMPLETED,
            params={"origin": "CGK"},
        )

        response_dict = job_info.to_dict()
        assert response_dict["job_id"] == "test-id"
        assert response_dict["status"] == "completed"
        assert response_dict["progress"] == 0
