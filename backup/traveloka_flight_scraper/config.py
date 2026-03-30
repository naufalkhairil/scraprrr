"""
Configuration management for Traveloka Flight Scraper.

This module handles loading and managing configuration data such as airport mappings.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration data for the scraper."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the ConfigManager.

        Args:
            config_dir: Directory containing configuration files. 
                       Defaults to the project root (parent of src/).
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default: look for mappings/ directory in project root
            # This allows users to easily find and edit configuration files
            self.config_dir = Path(__file__).parent.parent.parent

        self._airports: Optional[Dict[str, str]] = None

    @property
    def airports(self) -> Dict[str, str]:
        """
        Get the airport mappings.

        Returns:
            Dictionary mapping airport codes to airport names.
        """
        if self._airports is None:
            self._airports = self._load_airports()
        return self._airports

    def _load_airports(self) -> Dict[str, str]:
        """
        Load airport mappings from JSON file.

        Searches for airports.json in the following order:
        1. mappings/airports.json in project root (default)
        2. project root/airports.json (fallback for backwards compatibility)
        3. Package directory (fallback)

        Returns:
            Dictionary mapping airport codes to airport names.
        """
        # Try mappings/ directory first (preferred location)
        airports_file = self.config_dir / "mappings" / "airports.json"
        
        # Fallback to project root
        if not airports_file.exists():
            root_airports = self.config_dir / "airports.json"
            if root_airports.exists():
                airports_file = root_airports
                logger.debug(f"Using fallback airports file: {airports_file}")
            else:
                # Fallback to package directory
                package_airports = Path(__file__).parent / "airports.json"
                if package_airports.exists():
                    airports_file = package_airports
                    logger.debug(f"Using package fallback airports file: {airports_file}")
                else:
                    logger.warning(f"Airports file not found in mappings/, project root, or package")
                    return {}

        try:
            with open(airports_file, "r", encoding="utf-8") as f:
                airports = json.load(f)
            logger.info(f"Loaded {len(airports)} airports from {airports_file}")
            return airports
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse airports.json: {e}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load airports.json: {e}")
            return {}

    def get_airport_name(self, code: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get airport name by code.

        Args:
            code: Airport IATA code.
            default: Default value if code not found.

        Returns:
            Airport name or default value.
        """
        code_upper = code.upper()
        if code_upper in self.airports:
            return self.airports[code_upper]
        
        if default is not None:
            return default
        return f"{code_upper} Airport"

    def get_airport_code(self, name: str) -> Optional[str]:
        """
        Get airport code by name (case-insensitive search).

        Args:
            name: Airport name or partial name.

        Returns:
            Airport code or None if not found.
        """
        name_lower = name.lower()
        for code, airport_name in self.airports.items():
            if name_lower in airport_name.lower():
                return code
        return None

    def add_airport(self, code: str, name: str) -> None:
        """
        Add or update an airport mapping (runtime only, doesn't save to file).

        Args:
            code: Airport IATA code.
            name: Airport name.
        """
        self.airports[code.upper()] = name
        logger.debug(f"Added airport: {code.upper()} - {name}")

    def list_airports(self) -> Dict[str, str]:
        """
        Get all airport mappings.

        Returns:
            Copy of the airport mappings dictionary.
        """
        return self.airports.copy()


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_dir: Optional[str] = None) -> ConfigManager:
    """
    Get or create the global ConfigManager instance.

    Args:
        config_dir: Optional custom config directory.

    Returns:
        ConfigManager instance.
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_dir)
    return _config_manager


def get_airport_name(code: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get airport name by code using the global config manager.

    Args:
        code: Airport IATA code.
        default: Default value if code not found.

    Returns:
        Airport name or default value.
    """
    return get_config_manager().get_airport_name(code, default)


def get_airport_code(name: str) -> Optional[str]:
    """
    Get airport code by name using the global config manager.

    Args:
        name: Airport name or partial name.

    Returns:
        Airport code or None if not found.
    """
    return get_config_manager().get_airport_code(name)
