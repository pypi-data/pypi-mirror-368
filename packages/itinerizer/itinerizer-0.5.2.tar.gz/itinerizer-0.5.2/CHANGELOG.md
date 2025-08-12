# Changelog

All notable changes to Itinerizer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.2] - 2025-01-11

### Fixed
- **Critical**: Fixed overlap validation to support realistic business travel scenarios
- Implemented smart segment categorization:
  - **Background segments** (hotels): Can overlap with any other segments
  - **Foreground segments** (meetings/activities): Can overlap with hotels and each other (with warnings)
  - **Exclusive segments** (flights/transfers): Cannot overlap with each other
- The library now properly handles multi-day hotel stays with meetings and activities during the stay

### Changed
- Complete rewrite of `ItineraryValidator._validate_segment_order()` method
- Hotels no longer conflict with flights, transfers, meetings, or activities
- Only transportation segments (flights/transfers) are validated for mutual exclusivity
- Meeting/activity overlaps generate warnings instead of errors

### Impact
- Resolves the major limitation that made the library unsuitable for real-world business travel
- Enables proper modeling of typical business trips with hotels spanning multiple days
- Maintains safety by preventing impossible scenarios (overlapping flights)

## [0.5.1] - 2025-01-11

### Fixed
- **Critical**: Fixed infinite recursion bug in `FlightSegment.sync_times()` method
- **Critical**: Fixed infinite recursion bug in `HotelSegment.sync_dates()` method
- Changed validators from `mode='after'` to `mode='before'` to prevent re-validation loops
- Both segment types now properly sync their datetime fields without causing recursion

### Technical Details
- FlightSegment now syncs `start_datetime` with `departure_datetime` during initialization
- HotelSegment now syncs `start_datetime` and `end_datetime` from check-in/out dates during initialization
- Validation still ensures arrival times are after departure times

## [0.5.0] - 2025-01-11

### Added
- Complete PyPI package structure with proper packaging
- Modular architecture with separate models, storage, validation, and manager modules
- Optional FastAPI server component for REST API
- Optional Flask web UI component
- Comprehensive type hints and validation using Pydantic v2
- Thread-safe singleton pattern for file storage
- Automatic backup creation before modifications
- In-memory caching with TTL for improved performance
- Support for orjson for faster JSON operations (optional)
- Full test suite with pytest
- Docker support for containerized deployment
- CI/CD pipeline with GitHub Actions

### Changed
- Restructured code into `src/itinerizer` package layout
- Improved error handling and validation messages
- Enhanced documentation with docstrings
- Updated dependencies to latest stable versions

### Fixed
- Version conflict detection in concurrent updates
- Segment overlap validation
- Date consistency checks between itinerary and segments

## [0.4.0] - 2024-12-01

### Added
- Web UI with Flask implementation
- NLP support for natural language itinerary creation
- Analytics dashboard for trip statistics
- API testing interface
- Responsive design for mobile devices

### Changed
- Improved segment validation logic
- Enhanced error pages with better user feedback
- Optimized database queries for better performance

### Fixed
- Session management issues in web UI
- CORS configuration for API endpoints
- File locking issues in concurrent access scenarios

## [0.3.0] - 2024-10-15

### Added
- FastAPI REST API server
- Swagger/OpenAPI documentation
- Advanced search and filtering capabilities
- Batch operations support
- WebSocket support for real-time updates

### Changed
- Refactored storage layer for better abstraction
- Improved JSON serialization performance
- Enhanced validation rules

### Fixed
- Memory leaks in long-running processes
- Race conditions in file access
- UUID serialization issues

## [0.2.0] - 2024-08-20

### Added
- Support for multiple segment types (Flight, Hotel, Meeting, Activity, Transfer, Custom)
- Traveler management with loyalty programs
- Money handling with currency support
- Location and address models
- Business trip features (cost center, project codes)

### Changed
- Migrated from dataclasses to Pydantic for better validation
- Improved error messages and validation feedback
- Enhanced itinerary status workflow

### Fixed
- Date/time timezone handling
- Decimal precision in money calculations
- Validation of overlapping segments

## [0.1.0] - 2024-06-01

### Added
- Initial release with basic itinerary management
- JSON file storage
- Simple CRUD operations
- Basic validation
- Command-line interface

### Features
- Create, read, update, delete itineraries
- Add and remove segments
- List all itineraries
- Basic search functionality

## [0.0.1] - 2024-05-01

### Added
- Project initialization
- Basic project structure
- Initial planning and design documents

---

## Roadmap

### [0.6.0] - Planned
- GraphQL API support
- PostgreSQL storage backend option
- Advanced analytics and reporting
- Multi-language support
- Mobile app API endpoints

### [0.7.0] - Planned
- Real-time collaboration features
- Integration with booking platforms
- Email notifications
- Calendar synchronization
- PDF export functionality

### [1.0.0] - Planned
- Production-ready release
- Complete documentation
- Performance optimizations
- Security audit completion
- Enterprise features