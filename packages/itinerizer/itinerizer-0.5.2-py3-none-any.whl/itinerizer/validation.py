"""
Validation utilities for Itinerizer.
"""

from dataclasses import dataclass
from typing import List, Optional, Set

from .models import Itinerary, SegmentType


@dataclass
class ValidationError:
    code: str
    message: str
    field: Optional[str] = None


@dataclass
class ValidationResult:
    errors: List[ValidationError] = None
    warnings: List[ValidationError] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


class ItineraryValidator:
    """Business rule validation for itineraries"""
    
    def validate(self, itinerary: Itinerary) -> ValidationResult:
        result = ValidationResult()
        
        # Check segment chronology
        self._validate_segment_order(itinerary, result)
        
        # Check date consistency
        self._validate_dates(itinerary, result)
        
        # Business rules
        if itinerary.trip_type == "BUSINESS" and not itinerary.cost_center:
            result.warnings.append(
                ValidationError("MISSING_COST_CENTER", "Business trip should have cost center")
            )
        
        # Check traveler consistency
        self._validate_travelers(itinerary, result)
        
        return result
    
    def _validate_segment_order(self, itinerary: Itinerary, result: ValidationResult):
        """Validate segment chronology with smart overlap detection"""
        if not itinerary.segments:
            return
        
        # Define segment categories
        BACKGROUND_SEGMENTS = {SegmentType.HOTEL}  # Can overlap with other segments
        FOREGROUND_SEGMENTS = {SegmentType.MEETING, SegmentType.ACTIVITY, SegmentType.CUSTOM}  # Can overlap with background
        EXCLUSIVE_SEGMENTS = {SegmentType.FLIGHT, SegmentType.TRANSFER}  # Cannot overlap with anything
        
        sorted_segments = sorted(itinerary.segments, key=lambda s: s.start_datetime)
        
        for i in range(len(sorted_segments)):
            current = sorted_segments[i]
            
            # Check for conflicts with other segments
            for j in range(i + 1, len(sorted_segments)):
                other = sorted_segments[j]
                
                # Check if segments overlap
                if current.end_datetime > other.start_datetime:
                    # Determine if this overlap is allowed
                    current_type = current.type
                    other_type = other.type
                    
                    # Hotels can overlap with meetings/activities/custom segments
                    if (current_type in BACKGROUND_SEGMENTS and other_type in FOREGROUND_SEGMENTS) or \
                       (other_type in BACKGROUND_SEGMENTS and current_type in FOREGROUND_SEGMENTS):
                        continue  # This overlap is allowed
                    
                    # Hotels can also overlap with transportation (checking in before flight, checking out after arrival)
                    if (current_type in BACKGROUND_SEGMENTS and other_type in EXCLUSIVE_SEGMENTS) or \
                       (other_type in BACKGROUND_SEGMENTS and current_type in EXCLUSIVE_SEGMENTS):
                        continue  # This overlap is allowed (hotel spans the travel days)
                    
                    # Background segments (hotels) can overlap with each other (e.g., switching hotels)
                    if current_type in BACKGROUND_SEGMENTS and other_type in BACKGROUND_SEGMENTS:
                        # Only warn if they overlap significantly (more than check-in/out time overlap)
                        overlap_hours = (min(current.end_datetime, other.end_datetime) - 
                                       max(current.start_datetime, other.start_datetime)).total_seconds() / 3600
                        if overlap_hours > 4:  # More than 4 hours overlap
                            result.warnings.append(
                                ValidationError(
                                    "HOTEL_OVERLAP",
                                    f"Hotels overlap significantly: {current.id} and {other.id}"
                                )
                            )
                        continue
                    
                    # Exclusive segments (flights/transfers) cannot overlap with EACH OTHER
                    if current_type in EXCLUSIVE_SEGMENTS and other_type in EXCLUSIVE_SEGMENTS:
                        result.errors.append(
                            ValidationError(
                                "EXCLUSIVE_SEGMENT_OVERLAP",
                                f"Transportation segments cannot overlap: {current.id} ({current_type.value}) and {other.id} ({other_type.value})"
                            )
                        )
                        continue
                    
                    # Foreground segments (meetings/activities) can overlap with each other but generate a warning
                    if current_type in FOREGROUND_SEGMENTS and other_type in FOREGROUND_SEGMENTS:
                        result.warnings.append(
                            ValidationError(
                                "ACTIVITY_OVERLAP",
                                f"Activities/meetings overlap: {current.id} and {other.id} - verify this is intentional"
                            )
                        )
                        continue
                    
                    # Any other overlap is an error
                    result.errors.append(
                        ValidationError(
                            "SEGMENT_OVERLAP",
                            f"Segments overlap: {current.id} ({current_type.value}) and {other.id} ({other_type.value})"
                        )
                    )
                    
        # Check for large gaps (but only between exclusive segments like flights)
        exclusive_segments = [s for s in sorted_segments if s.type in EXCLUSIVE_SEGMENTS]
        for i in range(len(exclusive_segments) - 1):
            current = exclusive_segments[i]
            next_seg = exclusive_segments[i + 1]
            
            gap = (next_seg.start_datetime - current.end_datetime).total_seconds()
            
            if gap > 86400:  # More than 24 hours
                result.warnings.append(
                    ValidationError(
                        "LARGE_GAP",
                        f"Large gap between transportation segments: {current.id} and {next_seg.id}"
                    )
                )
    
    def _validate_dates(self, itinerary: Itinerary, result: ValidationResult):
        """Validate date consistency"""
        if itinerary.segments:
            earliest = min(s.start_datetime.date() for s in itinerary.segments)
            latest = max(s.end_datetime.date() for s in itinerary.segments)
            
            if earliest < itinerary.start_date:
                result.errors.append(
                    ValidationError(
                        "SEGMENT_BEFORE_START",
                        f"Segment starts before itinerary start date"
                    )
                )
            
            if latest > itinerary.end_date:
                result.errors.append(
                    ValidationError(
                        "SEGMENT_AFTER_END",
                        f"Segment ends after itinerary end date"
                    )
                )
    
    def _validate_travelers(self, itinerary: Itinerary, result: ValidationResult):
        """Validate traveler consistency"""
        traveler_ids = {t.id for t in itinerary.travelers}
        
        for segment in itinerary.segments:
            for tid in segment.traveler_ids:
                if tid not in traveler_ids:
                    result.errors.append(
                        ValidationError(
                            "INVALID_TRAVELER",
                            f"Segment {segment.id} references unknown traveler {tid}"
                        )
                    )