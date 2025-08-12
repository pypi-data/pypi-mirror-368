"""
Validation utilities for Itinerizer.
"""

from dataclasses import dataclass
from typing import List, Optional

from .models import Itinerary


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
        """Validate segment chronology"""
        if not itinerary.segments:
            return
        
        sorted_segments = sorted(itinerary.segments, key=lambda s: s.start_datetime)
        
        for i in range(len(sorted_segments) - 1):
            current = sorted_segments[i]
            next_seg = sorted_segments[i + 1]
            
            gap = (next_seg.start_datetime - current.end_datetime).total_seconds()
            
            if gap < 0:
                result.errors.append(
                    ValidationError(
                        "SEGMENT_OVERLAP",
                        f"Segments overlap: {current.id} and {next_seg.id}"
                    )
                )
            elif gap > 86400:  # More than 24 hours
                result.warnings.append(
                    ValidationError(
                        "LARGE_GAP",
                        f"Large gap between segments: {current.id} and {next_seg.id}"
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