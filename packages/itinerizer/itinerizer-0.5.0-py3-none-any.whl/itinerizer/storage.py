"""
Storage implementations for Itinerizer.
"""

from __future__ import annotations
import json
import threading
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, ContextManager
from uuid import UUID
from contextlib import contextmanager

try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False

from .models import (
    Itinerary, Segment, SegmentType,
    FlightSegment, HotelSegment, MeetingSegment,
    ActivitySegment, TransferSegment, CustomSegment
)


class ItinerarySingleton:
    """Thread-safe singleton for managing itinerary file access"""
    
    _instance: Optional[ItinerarySingleton] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls) -> ItinerarySingleton:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._file_locks: Dict[UUID, threading.RLock] = {}
        self._file_cache: Dict[UUID, tuple[Any, datetime]] = {}
        self._cache_ttl = 300  # 5 minutes
        self._storage_path = Path("data/itineraries")
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._backup_path = Path("data/backups")
        self._backup_path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_lock(self, itinerary_id: UUID) -> threading.RLock:
        """Get or create a lock for a specific itinerary"""
        if itinerary_id not in self._file_locks:
            with self._lock:
                if itinerary_id not in self._file_locks:
                    self._file_locks[itinerary_id] = threading.RLock()
        return self._file_locks[itinerary_id]
    
    @contextmanager
    def edit_lock(self, itinerary_id: UUID) -> ContextManager[None]:
        """Context manager for exclusive write access"""
        lock = self._get_file_lock(itinerary_id)
        lock.acquire()
        try:
            # Create backup before editing
            file_path = self.get_file_path(itinerary_id)
            if file_path.exists():
                backup_name = f"{itinerary_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = self._backup_path / backup_name
                shutil.copy2(file_path, backup_path)
            
            yield
            
            # Invalidate cache after edit
            if itinerary_id in self._file_cache:
                del self._file_cache[itinerary_id]
        finally:
            lock.release()
    
    @contextmanager
    def read_lock(self, itinerary_id: UUID) -> ContextManager[None]:
        """Context manager for shared read access"""
        lock = self._get_file_lock(itinerary_id)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()
    
    def get_file_path(self, itinerary_id: UUID) -> Path:
        """Get the file path for an itinerary"""
        return self._storage_path / f"{itinerary_id}.json"
    
    def get_cache(self, itinerary_id: UUID) -> Optional[Any]:
        """Get cached itinerary if available and not expired"""
        if itinerary_id in self._file_cache:
            data, timestamp = self._file_cache[itinerary_id]
            if (datetime.now() - timestamp).seconds < self._cache_ttl:
                return data
            else:
                del self._file_cache[itinerary_id]
        return None
    
    def set_cache(self, itinerary_id: UUID, data: Any):
        """Set cache for an itinerary"""
        self._file_cache[itinerary_id] = (data, datetime.now())


class JSONItineraryStore:
    """JSON-based storage for itineraries"""
    
    def __init__(self):
        self.singleton = ItinerarySingleton()
    
    def _serialize_segment(self, segment: Segment) -> dict:
        """Serialize a segment with type discrimination"""
        data = segment.model_dump(mode='json')
        # Ensure UUIDs are strings
        if 'traveler_ids' in data:
            data['traveler_ids'] = [str(tid) for tid in data['traveler_ids']]
        if 'id' in data:
            data['id'] = str(data['id'])
        return data
    
    def _deserialize_segment(self, data: dict) -> Segment:
        """Deserialize a segment based on its type"""
        segment_type = data.get('type')
        
        # Convert string UUIDs back to UUID objects
        if 'traveler_ids' in data:
            data['traveler_ids'] = [UUID(tid) for tid in data['traveler_ids']]
        if 'id' in data:
            data['id'] = UUID(data['id'])
        
        # Map type to class
        type_map = {
            SegmentType.FLIGHT: FlightSegment,
            SegmentType.HOTEL: HotelSegment,
            SegmentType.MEETING: MeetingSegment,
            SegmentType.ACTIVITY: ActivitySegment,
            SegmentType.TRANSFER: TransferSegment,
            SegmentType.CUSTOM: CustomSegment,
        }
        
        segment_class = type_map.get(segment_type)
        if not segment_class:
            raise ValueError(f"Unknown segment type: {segment_type}")
        
        return segment_class.model_validate(data)
    
    def save(self, itinerary: Itinerary) -> UUID:
        """Save an itinerary to JSON storage"""
        with self.singleton.edit_lock(itinerary.id):
            # Check for existing version
            existing = self._load_raw(itinerary.id)
            if existing:
                # This is an update - check version and increment
                if existing.get('version', 0) >= itinerary.version:
                    raise ValueError(
                        f"Version conflict: current version {existing['version']} "
                        f">= new version {itinerary.version}"
                    )
                # Increment version for updates
                itinerary.version = existing.get('version', 0) + 1
            
            itinerary.updated_at = datetime.now()
            
            # Serialize
            data = itinerary.model_dump(mode='json')
            
            # Handle segments specially
            data['segments'] = [self._serialize_segment(s) for s in itinerary.segments]
            
            # Convert UUIDs and dates to strings
            data['id'] = str(itinerary.id)
            if data.get('primary_traveler_id'):
                data['primary_traveler_id'] = str(data['primary_traveler_id'])
            
            for traveler in data['travelers']:
                traveler['id'] = str(traveler['id'])
            
            # Write to file
            file_path = self.singleton.get_file_path(itinerary.id)
            
            if HAS_ORJSON:
                json_bytes = orjson.dumps(
                    data,
                    option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
                )
                temp_path = file_path.with_suffix('.tmp')
                temp_path.write_bytes(json_bytes)
            else:
                temp_path = file_path.with_suffix('.tmp')
                with open(temp_path, 'w') as f:
                    json.dump(data, f, indent=2, sort_keys=True, default=str)
            
            # Atomic replace
            temp_path.replace(file_path)
            
            # Update cache
            self.singleton.set_cache(itinerary.id, itinerary)
            
            return itinerary.id
    
    def load(self, itinerary_id: UUID) -> Optional[Itinerary]:
        """Load an itinerary from JSON storage"""
        # Check cache first
        cached = self.singleton.get_cache(itinerary_id)
        if cached:
            return cached
        
        with self.singleton.read_lock(itinerary_id):
            data = self._load_raw(itinerary_id)
            if data:
                # Convert string UUIDs back
                data['id'] = UUID(data['id'])
                if data.get('primary_traveler_id'):
                    data['primary_traveler_id'] = UUID(data['primary_traveler_id'])
                
                for traveler in data.get('travelers', []):
                    traveler['id'] = UUID(traveler['id'])
                
                # Deserialize segments
                segments = []
                for seg_data in data.get('segments', []):
                    segments.append(self._deserialize_segment(seg_data))
                data['segments'] = segments
                
                itinerary = Itinerary.model_validate(data)
                self.singleton.set_cache(itinerary_id, itinerary)
                return itinerary
        
        return None
    
    def _load_raw(self, itinerary_id: UUID) -> Optional[Dict[str, Any]]:
        """Load raw JSON data"""
        file_path = self.singleton.get_file_path(itinerary_id)
        if not file_path.exists():
            return None
        
        if HAS_ORJSON:
            json_bytes = file_path.read_bytes()
            return orjson.loads(json_bytes)
        else:
            with open(file_path, 'r') as f:
                return json.load(f)
    
    def delete(self, itinerary_id: UUID) -> bool:
        """Delete an itinerary"""
        with self.singleton.edit_lock(itinerary_id):
            file_path = self.singleton.get_file_path(itinerary_id)
            if file_path.exists():
                file_path.unlink()
                return True
        return False
    
    def list_all(self) -> List[UUID]:
        """List all itinerary IDs"""
        itineraries = []
        for file_path in self.singleton._storage_path.glob("*.json"):
            try:
                itinerary_id = UUID(file_path.stem)
                itineraries.append(itinerary_id)
            except ValueError:
                continue
        return itineraries