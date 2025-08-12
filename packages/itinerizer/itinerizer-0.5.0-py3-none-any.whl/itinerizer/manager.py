"""
High-level API for managing itineraries.
"""

from datetime import date
from typing import Optional, List
from uuid import UUID

from .models import Itinerary, Traveler, Segment
from .storage import JSONItineraryStore
from .validation import ItineraryValidator


class ItineraryManager:
    """High-level API for itinerary management"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the itinerary manager.
        
        Args:
            storage_path: Optional custom path for storing itineraries
        """
        self.storage = JSONItineraryStore()
        self.validator = ItineraryValidator()
        
        if storage_path:
            # Override default storage path
            from pathlib import Path
            self.storage.singleton._storage_path = Path(storage_path) / "itineraries"
            self.storage.singleton._storage_path.mkdir(parents=True, exist_ok=True)
            self.storage.singleton._backup_path = Path(storage_path) / "backups"
            self.storage.singleton._backup_path.mkdir(parents=True, exist_ok=True)
    
    def create_itinerary(
        self,
        title: str,
        start_date: date,
        end_date: date,
        travelers: List[Traveler],
        **kwargs
    ) -> Itinerary:
        """
        Create a new itinerary.
        
        Args:
            title: Title of the itinerary
            start_date: Start date of the trip
            end_date: End date of the trip
            travelers: List of travelers
            **kwargs: Additional itinerary fields
            
        Returns:
            Created itinerary
            
        Raises:
            ValueError: If validation fails
        """
        itinerary = Itinerary(
            title=title,
            start_date=start_date,
            end_date=end_date,
            travelers=travelers,
            **kwargs
        )
        
        # Validate
        validation = self.validator.validate(itinerary)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.errors}")
        
        # Save
        self.storage.save(itinerary)
        return itinerary
    
    def get_itinerary(self, itinerary_id: UUID) -> Optional[Itinerary]:
        """
        Get an itinerary by ID.
        
        Args:
            itinerary_id: UUID of the itinerary
            
        Returns:
            Itinerary if found, None otherwise
        """
        return self.storage.load(itinerary_id)
    
    def update_itinerary(self, itinerary: Itinerary) -> Itinerary:
        """
        Update an existing itinerary.
        
        Args:
            itinerary: Itinerary to update
            
        Returns:
            Updated itinerary
            
        Raises:
            ValueError: If validation fails
        """
        # Validate
        validation = self.validator.validate(itinerary)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.errors}")
        
        # Save (handles version increment)
        self.storage.save(itinerary)
        return itinerary
    
    def add_segment(self, itinerary_id: UUID, segment: Segment) -> Itinerary:
        """
        Add a segment to an itinerary.
        
        Args:
            itinerary_id: UUID of the itinerary
            segment: Segment to add
            
        Returns:
            Updated itinerary
            
        Raises:
            ValueError: If itinerary not found or validation fails
        """
        itinerary = self.storage.load(itinerary_id)
        if not itinerary:
            raise ValueError(f"Itinerary {itinerary_id} not found")
        
        # Add and sort segments
        itinerary.segments.append(segment)
        itinerary.segments.sort(key=lambda s: s.start_datetime)
        
        # Update and save
        return self.update_itinerary(itinerary)
    
    def remove_segment(self, itinerary_id: UUID, segment_id: UUID) -> Itinerary:
        """
        Remove a segment from an itinerary.
        
        Args:
            itinerary_id: UUID of the itinerary
            segment_id: UUID of the segment to remove
            
        Returns:
            Updated itinerary
            
        Raises:
            ValueError: If itinerary or segment not found
        """
        itinerary = self.storage.load(itinerary_id)
        if not itinerary:
            raise ValueError(f"Itinerary {itinerary_id} not found")
        
        # Find and remove segment
        original_count = len(itinerary.segments)
        itinerary.segments = [s for s in itinerary.segments if s.id != segment_id]
        
        if len(itinerary.segments) == original_count:
            raise ValueError(f"Segment {segment_id} not found in itinerary")
        
        # Update and save
        return self.update_itinerary(itinerary)
    
    def delete_itinerary(self, itinerary_id: UUID) -> bool:
        """
        Delete an itinerary.
        
        Args:
            itinerary_id: UUID of the itinerary to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.storage.delete(itinerary_id)
    
    def list_itineraries(self) -> List[UUID]:
        """
        List all itinerary IDs.
        
        Returns:
            List of itinerary UUIDs
        """
        return self.storage.list_all()
    
    def search_itineraries(
        self,
        status: Optional[str] = None,
        trip_type: Optional[str] = None,
        traveler_email: Optional[str] = None
    ) -> List[Itinerary]:
        """
        Search itineraries by criteria.
        
        Args:
            status: Filter by status
            trip_type: Filter by trip type
            traveler_email: Filter by traveler email
            
        Returns:
            List of matching itineraries
        """
        results = []
        for itinerary_id in self.list_itineraries():
            itinerary = self.get_itinerary(itinerary_id)
            if not itinerary:
                continue
            
            # Apply filters
            if status and itinerary.status != status:
                continue
            if trip_type and itinerary.trip_type != trip_type:
                continue
            if traveler_email:
                emails = [t.email for t in itinerary.travelers if t.email]
                if traveler_email not in emails:
                    continue
            
            results.append(itinerary)
        
        return results