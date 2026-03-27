# Pull Request: Unified CLI and Clean Architecture Refactor

## Summary

This PR refactors the entire codebase to provide a unified CLI for both flight and hotel scrapers, with a clean modular architecture that separates concerns between CLI, core infrastructure, and domain-specific scraper modules.

## Changes

### 🏗️ Architecture Restructure

**New Package Structure (`src/scraprrr/`):**

```
scraprrr/
├── cli/              # Command-line interface layer
│   ├── commands/     # Command handlers (flight.py, hotel.py)
│   ├── parsers/      # Argument parsers
│   └── main.py       # CLI entry point
├── core/             # Shared infrastructure
│   ├── base.py       # Base scraper class (abstract)
│   ├── driver.py     # WebDriver management
│   └── utils.py      # Common utilities, ScraperConfig
└── modules/          # Domain-specific scrapers
    ├── flight/       # Flight scraper module
    └── hotel/        # Hotel scraper module
```

**Benefits:**
- Clear separation of concerns (CLI, core, modules)
- Scalable: easy to add new scraper modules (e.g., car, train)
- Testable: each layer can be tested independently
- Maintainable: clear boundaries between components

### 🎯 Unified CLI

**New Commands:**

```bash
# Single CLI for both scrapers
scraprrr search flight --origin CGK --destination DPS
scraprrr search hotel --location Jakarta
scraprrr search batch --type flight --routes CGK-DPS,SUB-SIN
scraprrr search batch --type hotel --locations Jakarta,Bali

# Also available as 'traveloka' command
traveloka search flight --origin CGK --destination DPS
```

**Features:**
- `--verbose/-v` flag for debug logging on all subcommands
- Progress bars for hotel/flight extraction
- Status icons (✓/✗) for clear feedback
- Backward compatible with legacy commands

### 📦 Installation

> **Important:** This package is **NOT published to PyPI**. Install from local repository:

```bash
pip install -e .
```

### 📝 Key Changes by Component

#### CLI (`src/scraprrr/cli/`)
- New unified entry point with subcommands
- Separate command handlers and argument parsers
- Progress bars and status messages
- Verbose logging support

#### Core (`src/scraprrr/core/`)
- `BaseScraper` abstract class for all scrapers
- Shared `ScraperConfig` with common options
- WebDriver management (deduplicated)
- Common utilities (file I/O, data processing)

#### Flight Module (`src/scraprrr/modules/flight/`)
- `FlightScraper` class extending `BaseScraper`
- `FlightPage` for page object interactions
- `FlightExtractor` for data extraction
- `FlightTicket`, `FlightSearchResult` models

#### Hotel Module (`src/scraprrr/modules/hotel/`)
- `HotelScraper` class extending `BaseScraper`
- `HotelPage` for page object interactions
- `HotelExtractor` for data extraction
- `Hotel`, `HotelSearchResult` models
- Incremental scroll-and-parse with progress bar

### 🔧 Configuration Changes

**pyproject.toml:**
- Package renamed to `scraprrr` v2.0.0
- New CLI entry points: `scraprrr`, `traveloka`
- Legacy entry points maintained for backward compatibility

**Removed:**
- `num_scrolls` parameter from `HotelScraperConfig` (uses dynamic stopping)
- Duplicate code between flight/hotel scrapers

### 📚 Documentation

**README.md Updates:**
- Disclaimer note (documentation/learning purposes)
- Complete project structure tree
- Installation options (local, Git)
- CLI usage examples with all three methods
- Python API examples
- Troubleshooting section

## Breaking Changes

| Old | New |
|-----|-----|
| `traveloka-scraper` | `scraprrr search flight` (legacy still works) |
| `traveloka-hotel-scraper` | `scraprrr search hotel` (legacy still works) |
| `--num-scrolls` (hotel) | Removed (uses dynamic stopping) |

## Backward Compatibility

✅ **Legacy CLI commands still work:**
- `traveloka-scraper search --origin CGK --destination DPS`
- `traveloka-hotel-scraper search Jakarta`

✅ **Old package imports work via re-export layer:**
- `from traveloka_flight_scraper import TravelokaScraper`
- `from traveloka_hotel_scraper import TravelokaHotelScraper`

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scraprrr --cov-report=term-missing
```

## Files Changed

- **52 files changed**: +3,029 insertions, -558 deletions
- **New files**: 27 (new architecture)
- **Modified**: 15 (refactored to use new architecture)
- **Moved to backup/**: 10 (legacy code preservation)

## Migration Guide

### For CLI Users

```bash
# Old
traveloka-scraper search --origin CGK --destination DPS

# New (recommended)
scraprrr search flight --origin CGK --destination DPS
# or
traveloka search flight --origin CGK --destination DPS
```

### For Python API Users

```python
# Old
from traveloka_flight_scraper import TravelokaScraper

# New (recommended)
from scraprrr import FlightScraper

# Both work (backward compatible)
```

## Checklist

- [x] Code follows project conventions
- [x] All imports work correctly
- [x] CLI commands tested
- [x] Backward compatibility maintained
- [x] Documentation updated
- [x] Progress bars added for user feedback
- [x] Verbose logging works on all commands

## Related Issues

- Closes #ISSUE_NUMBER (if applicable)

## Screenshots

### CLI Progress Bars

**Hotel Extraction:**
```
Scroll 1: 40 hotels visible
  Parsing hotels...
  |██████████████████████████████| 40/40 (100%) - 35 unique
  +17 new hotels (total: 35)
```

**Flight Extraction:**
```
Scroll 1: 25 tickets visible
  Extracting tickets...
  |██████████████████████████████| 25/25 (100%) - 23 extracted
```

---

**Branch:** `refactor/unified-cli`
**Base Branch:** `master`
