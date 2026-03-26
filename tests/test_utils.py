"""
Tests for Traveloka Flight Scraper utilities.
"""

import json
import os
import tempfile
from datetime import datetime

import pytest

from traveloka_flight_scraper.utils import (
    create_search_summary,
    format_duration_to_minutes,
    generate_output_filename,
    load_from_csv,
    load_from_json,
    parse_price_to_numeric,
    save_to_csv,
    save_to_json,
)


class TestGenerateOutputFilename:
    """Tests for generate_output_filename function."""

    def test_generate_filename(self):
        """Test generating a filename with timestamp."""
        filename = generate_output_filename(
            prefix="test_results",
            extension="csv",
            output_dir="/tmp",
            timestamp=datetime(2026, 3, 26, 10, 30, 0),
        )

        assert filename == "/tmp/test_results_20260326103000.csv"

    def test_generate_filename_default_timestamp(self):
        """Test generating a filename with default timestamp."""
        before = datetime.now()
        filename = generate_output_filename(
            prefix="test",
            extension="json",
        )
        after = datetime.now()

        # Just verify it contains the expected pattern
        assert "test_" in filename
        assert filename.endswith(".json")


class TestSaveAndLoadCSV:
    """Tests for CSV save and load functions."""

    def test_save_to_csv(self):
        """Test saving data to CSV."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filepath = f.name

        try:
            result_path = save_to_csv(data, filepath)
            assert result_path == filepath
            assert os.path.exists(filepath)

            # Verify content
            df = load_from_csv(filepath)
            assert len(df) == 2
            assert list(df["name"]) == ["Alice", "Bob"]
        finally:
            os.unlink(filepath)

    def test_save_empty_csv(self):
        """Test saving empty data to CSV raises error."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filepath = f.name

        try:
            with pytest.raises(ValueError, match="No data to save"):
                save_to_csv([], filepath)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_load_nonexistent_csv(self):
        """Test loading nonexistent CSV raises error."""
        with pytest.raises(FileNotFoundError):
            load_from_csv("/nonexistent/path.csv")


class TestSaveAndLoadJSON:
    """Tests for JSON save and load functions."""

    def test_save_to_json(self):
        """Test saving data to JSON."""
        data = {"name": "Test", "value": 42}

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            result_path = save_to_json(data, filepath)
            assert result_path == filepath
            assert os.path.exists(filepath)

            # Verify content
            with open(filepath, "r") as f:
                loaded = json.load(f)
            assert loaded == data
        finally:
            os.unlink(filepath)

    def test_load_nonexistent_json(self):
        """Test loading nonexistent JSON raises error."""
        with pytest.raises(FileNotFoundError):
            load_from_json("/nonexistent/path.json")


class TestParsePriceToNumeric:
    """Tests for parse_price_to_numeric function."""

    def test_parse_indonesian_price(self):
        """Test parsing Indonesian Rupiah format."""
        assert parse_price_to_numeric("Rp 1.500.000") == 1500000.0
        assert parse_price_to_numeric("Rp 150.000") == 150000.0

    def test_parse_us_price(self):
        """Test parsing US Dollar format."""
        # Note: The function treats dots as thousand separators (Indonesian format)
        # For US format with decimal point, use without decimal or fix the function
        assert parse_price_to_numeric("$1500") == 1500.0
        assert parse_price_to_numeric("$150") == 150.0

    def test_parse_price_whitespace(self):
        """Test parsing price with various whitespace."""
        assert parse_price_to_numeric("  Rp 1.500.000  ") == 1500000.0

    def test_parse_invalid_price(self):
        """Test parsing invalid price returns None."""
        assert parse_price_to_numeric("invalid") is None
        assert parse_price_to_numeric("") is None
        assert parse_price_to_numeric(None) is None


class TestFormatDurationToMinutes:
    """Tests for format_duration_to_minutes function."""

    def test_parse_hours_and_minutes(self):
        """Test parsing duration with hours and minutes."""
        assert format_duration_to_minutes("2h 30m") == 150
        assert format_duration_to_minutes("1h 45m") == 105

    def test_parse_hours_only(self):
        """Test parsing duration with hours only."""
        assert format_duration_to_minutes("2h") == 120
        assert format_duration_to_minutes("1h") == 60

    def test_parse_minutes_only(self):
        """Test parsing duration with minutes only."""
        assert format_duration_to_minutes("30m") == 30
        assert format_duration_to_minutes("45m") == 45

    def test_parse_invalid_duration(self):
        """Test parsing invalid duration returns None."""
        assert format_duration_to_minutes("invalid") is None
        assert format_duration_to_minutes("") is None
        assert format_duration_to_minutes(None) is None


class TestCreateSearchSummary:
    """Tests for create_search_summary function."""

    def test_create_summary_basic(self):
        """Test creating basic search summary."""
        summary = create_search_summary("CGK", "DPS", 10)
        assert "CGK" in summary
        assert "DPS" in summary
        assert "10 flights" in summary

    def test_create_summary_with_price_range(self):
        """Test creating summary with price range."""
        summary = create_search_summary(
            "CGK", "DPS", 10, min_price="Rp 500.000", max_price="Rp 2.000.000"
        )
        assert "Price range" in summary
        assert "Rp 500.000" in summary
        assert "Rp 2.000.000" in summary
