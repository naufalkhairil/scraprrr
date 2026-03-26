"""
Tests for Traveloka hotel scraper CLI.
"""

import pytest

from traveloka_hotel_scraper.cli import create_parser, main


class TestCLIArgumentParsing:
    """Test CLI argument parsing."""

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None

    def test_search_command_basic(self):
        """Test search command with basic arguments."""
        parser = create_parser()
        args = parser.parse_args(["search", "Jakarta"])
        assert args.command == "search"
        assert args.location == "Jakarta"
        assert args.max_hotels == 100
        assert args.no_scroll is False

    def test_search_command_with_options(self):
        """Test search command with options."""
        parser = create_parser()
        args = parser.parse_args([
            "search",
            "Bali",
            "--max-hotels", "50",
            "--num-scrolls", "10",
            "--no-scroll",
            "--no-save-csv",
            "--save-json",
            "--output-dir", "/tmp",
        ])
        assert args.location == "Bali"
        assert args.max_hotels == 50
        assert args.num_scrolls == 10
        assert args.no_scroll is True
        assert args.no_save_csv is True
        assert args.save_json is True
        assert args.output_dir == "/tmp"

    def test_search_batch_command_locations(self):
        """Test batch search with comma-separated locations."""
        parser = create_parser()
        args = parser.parse_args([
            "search-batch",
            "Jakarta,Bandung,Surabaya",
        ])
        assert args.command == "search-batch"
        assert args.locations == "Jakarta,Bandung,Surabaya"
        assert args.locations_file is None

    def test_search_batch_command_file(self):
        """Test batch search with locations file."""
        parser = create_parser()
        args = parser.parse_args([
            "search-batch",
            "--locations-file", "cities.txt",
        ])
        assert args.command == "search-batch"
        assert args.locations_file == "cities.txt"
        assert args.locations is None

    def test_search_batch_with_options(self):
        """Test batch search with options."""
        parser = create_parser()
        args = parser.parse_args([
            "search-batch",
            "Jakarta,Bali",
            "--max-hotels", "75",
            "--delay", "10.5",
            "--output-dir", "./results",
        ])
        assert args.max_hotels == 75
        assert args.delay == 10.5
        assert args.output_dir == "./results"

    def test_global_options(self):
        """Test global options."""
        parser = create_parser()
        args = parser.parse_args([
            "-v",
            "--selenium-url", "http://custom:4444/wd/hub",
            "search",
            "Jakarta",
        ])
        assert args.verbose is True
        assert args.selenium_url == "http://custom:4444/wd/hub"

    def test_no_command_shows_help(self):
        """Test that no command shows help."""
        parser = create_parser()
        # Should return args with command=None
        args = parser.parse_args([])
        assert args.command is None


class TestCLIMain:
    """Test CLI main function."""

    def test_main_no_command(self):
        """Test main with no command."""
        result = main([])
        assert result == 1

    def test_main_unknown_command(self):
        """Test main with unknown command."""
        with pytest.raises(SystemExit) as exc_info:
            main(["unknown-command"])
        assert exc_info.value.code == 2  # argparse returns 2 for unknown arguments

    def test_main_search_command_help(self):
        """Test search command help."""
        with pytest.raises(SystemExit) as exc_info:
            main(["search", "--help"])
        assert exc_info.value.code == 0

    def test_main_batch_command_help(self):
        """Test batch command help."""
        with pytest.raises(SystemExit) as exc_info:
            main(["search-batch", "--help"])
        assert exc_info.value.code == 0
