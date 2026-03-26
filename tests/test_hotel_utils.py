"""
Tests for Traveloka hotel scraper utilities.
"""

import os
import tempfile
from datetime import datetime

import pytest

from traveloka_hotel_scraper.utils import (
    generate_output_filename,
    save_to_csv,
    save_to_json,
)


class TestGenerateOutputFilename:
    """Test generate_output_filename function."""

    def test_basic_filename(self):
        """Test basic filename generation."""
        filepath = generate_output_filename(
            prefix="trave_hotel_results",
            extension="csv",
        )
        assert filepath.endswith(".csv")
        assert "trave_hotel_results" in filepath

    def test_filename_with_location(self):
        """Test filename with location."""
        filepath = generate_output_filename(
            prefix="trave_hotel_results",
            extension="csv",
            location="Jakarta",
        )
        assert "jakarta" in filepath.lower()

    def test_filename_with_timestamp(self):
        """Test filename with custom timestamp."""
        timestamp = datetime(2026, 3, 26, 10, 30, 0)
        filepath = generate_output_filename(
            prefix="trave_hotel_results",
            extension="csv",
            timestamp=timestamp,
            location="Bali",
        )
        assert "20260326103000" in filepath

    def test_filename_with_output_dir(self):
        """Test filename with output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = generate_output_filename(
                prefix="trave_hotel_results",
                extension="csv",
                output_dir=tmpdir,
            )
            assert tmpdir in filepath
            assert os.path.exists(os.path.dirname(filepath))

    def test_filename_sanitizes_location(self):
        """Test that location is sanitized for filename."""
        filepath = generate_output_filename(
            prefix="trave_hotel_results",
            extension="csv",
            location="New York City",
        )
        assert "new_york_city" in filepath.lower()

    def test_filename_json_extension(self):
        """Test filename with JSON extension."""
        filepath = generate_output_filename(
            prefix="trave_hotel_results",
            extension="json",
        )
        assert filepath.endswith(".json")


class TestSaveToCSV:
    """Test save_to_csv function."""

    def test_save_csv_basic(self):
        """Test basic CSV saving."""
        data = [
            {"hotel_name": "Hotel 1", "price": "Rp 500.000"},
            {"hotel_name": "Hotel 2", "price": "Rp 600.000"},
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.csv")
            save_to_csv(data, filepath)
            assert os.path.exists(filepath)

            # Verify content
            with open(filepath, "r") as f:
                content = f.read()
                assert "hotel_name" in content
                assert "Hotel 1" in content

    def test_save_csv_empty_data(self):
        """Test saving empty data."""
        data = []
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.csv")
            save_to_csv(data, filepath)
            assert os.path.exists(filepath)

    def test_save_csv_creates_directory(self):
        """Test that save_to_csv creates output directory."""
        data = [{"hotel_name": "Hotel 1"}]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "subdir")
            filepath = os.path.join(output_dir, "test.csv")
            save_to_csv(data, filepath)
            assert os.path.exists(output_dir)
            assert os.path.exists(filepath)


class TestSaveToJSON:
    """Test save_to_json function."""

    def test_save_json_basic(self):
        """Test basic JSON saving."""
        data = {
            "location": "Jakarta",
            "status": "success",
            "total_results": 10,
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.json")
            save_to_json(data, filepath)
            assert os.path.exists(filepath)

            # Verify content
            import json
            with open(filepath, "r") as f:
                loaded = json.load(f)
                assert loaded["location"] == "Jakarta"
                assert loaded["status"] == "success"

    def test_save_json_unicode(self):
        """Test saving JSON with unicode characters."""
        data = {
            "hotel_name": "Grand Hôtel",
            "location": "São Paulo",
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.json")
            save_to_json(data, filepath)

            import json
            with open(filepath, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                assert loaded["hotel_name"] == "Grand Hôtel"

    def test_save_json_nested_data(self):
        """Test saving nested JSON data."""
        data = {
            "location": "Jakarta",
            "hotels": [
                {"name": "Hotel 1", "price": "Rp 500.000"},
                {"name": "Hotel 2", "price": "Rp 600.000"},
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.json")
            save_to_json(data, filepath)

            import json
            with open(filepath, "r") as f:
                loaded = json.load(f)
                assert len(loaded["hotels"]) == 2
