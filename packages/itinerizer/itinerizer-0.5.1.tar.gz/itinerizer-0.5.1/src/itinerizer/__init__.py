"""
Itinerizer - A comprehensive travel itinerary management system.

This package provides a complete solution for managing travel itineraries
with JSON storage, including flights, hotels, meetings, and other travel segments.
"""

from .__version__ import __version__, __author__, __email__, __description__, __url__

# Import all models
from .models import (
    # Enums
    ItineraryStatus,
    SegmentType,
    SegmentStatus,
    TravelerType,
    
    # Base models
    StrictModel,
    Money,
    Coordinates,
    Address,
    Location,
    Company,
    LoyaltyProgram,
    Traveler,
    TravelPreferences,
    
    # Segments
    BaseSegment,
    FlightSegment,
    HotelSegment,
    MeetingSegment,
    ActivitySegment,
    TransferSegment,
    CustomSegment,
    Segment,
    
    # Main model
    Itinerary,
)

# Import storage
from .storage import (
    JSONItineraryStore,
    ItinerarySingleton,
)

# Import validation
from .validation import (
    ValidationError,
    ValidationResult,
    ItineraryValidator,
)

# Import manager
from .manager import ItineraryManager

# Define public API
__all__ = [
    # Version info
    "__version__",
    
    # Manager (main API)
    "ItineraryManager",
    
    # Models
    "Itinerary",
    "Traveler",
    "Location",
    "Company",
    "Money",
    "Address",
    "Coordinates",
    "LoyaltyProgram",
    "TravelPreferences",
    
    # Segments
    "Segment",
    "FlightSegment",
    "HotelSegment",
    "MeetingSegment",
    "ActivitySegment",
    "TransferSegment",
    "CustomSegment",
    "BaseSegment",
    
    # Enums
    "ItineraryStatus",
    "SegmentType",
    "SegmentStatus",
    "TravelerType",
    
    # Storage
    "JSONItineraryStore",
    
    # Validation
    "ValidationError",
    "ValidationResult",
    "ItineraryValidator",
]