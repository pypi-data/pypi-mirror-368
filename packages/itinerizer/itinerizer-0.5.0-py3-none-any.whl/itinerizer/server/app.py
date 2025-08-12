"""
FastAPI application for Itinerizer REST API.
"""

import logging
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Path, Body, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..manager import ItineraryManager
from ..models import (
    Itinerary, ItineraryStatus, Traveler, Segment,
    Money, Location, TravelPreferences
)
from ..validation import ValidationResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# API Models
class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class ItinerarySummary(BaseModel):
    """Lightweight itinerary summary for list views"""
    id: UUID
    title: str
    status: ItineraryStatus
    start_date: date
    end_date: date
    traveler_count: int
    segment_count: int
    total_price: Optional[Money] = None
    trip_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    version: int


def create_app(storage_path: Optional[str] = None) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        storage_path: Optional custom storage path
        
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Itinerizer API",
        description="REST API for managing travel itineraries",
        version="0.5.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize manager
    manager = ItineraryManager(storage_path=storage_path)
    
    # Store manager in app state
    app.state.manager = manager
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": "0.5.0"}
    
    # Itinerary endpoints
    @app.get("/api/itineraries", response_model=APIResponse)
    async def list_itineraries(
        status: Optional[ItineraryStatus] = Query(None),
        trip_type: Optional[str] = Query(None),
        traveler_email: Optional[str] = Query(None)
    ):
        """List all itineraries with optional filters"""
        try:
            itineraries = manager.search_itineraries(
                status=status,
                trip_type=trip_type,
                traveler_email=traveler_email
            )
            
            summaries = []
            for itinerary in itineraries:
                summaries.append(ItinerarySummary(
                    id=itinerary.id,
                    title=itinerary.title,
                    status=itinerary.status,
                    start_date=itinerary.start_date,
                    end_date=itinerary.end_date,
                    traveler_count=len(itinerary.travelers),
                    segment_count=len(itinerary.segments),
                    total_price=itinerary.calculate_total_price(),
                    trip_type=itinerary.trip_type,
                    created_at=itinerary.created_at,
                    updated_at=itinerary.updated_at,
                    version=itinerary.version
                ))
            
            return APIResponse(
                data=summaries,
                metadata={"count": len(summaries)}
            )
        except Exception as e:
            logger.error(f"Error listing itineraries: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/itineraries/{itinerary_id}", response_model=APIResponse)
    async def get_itinerary(itinerary_id: UUID = Path(...)):
        """Get a specific itinerary by ID"""
        itinerary = manager.get_itinerary(itinerary_id)
        if not itinerary:
            raise HTTPException(status_code=404, detail="Itinerary not found")
        
        return APIResponse(data=itinerary.model_dump(mode='json'))
    
    @app.post("/api/itineraries", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
    async def create_itinerary(itinerary_data: Dict[str, Any] = Body(...)):
        """Create a new itinerary"""
        try:
            # Parse travelers
            travelers = []
            for t_data in itinerary_data.get('travelers', []):
                travelers.append(Traveler.model_validate(t_data))
            
            # Create itinerary
            itinerary = manager.create_itinerary(
                title=itinerary_data['title'],
                start_date=date.fromisoformat(itinerary_data['start_date']),
                end_date=date.fromisoformat(itinerary_data['end_date']),
                travelers=travelers,
                **{k: v for k, v in itinerary_data.items() 
                   if k not in ['title', 'start_date', 'end_date', 'travelers']}
            )
            
            return APIResponse(
                message="Itinerary created successfully",
                data={"id": str(itinerary.id), "version": itinerary.version}
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating itinerary: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.put("/api/itineraries/{itinerary_id}", response_model=APIResponse)
    async def update_itinerary(
        itinerary_id: UUID = Path(...),
        itinerary_data: Dict[str, Any] = Body(...)
    ):
        """Update an existing itinerary"""
        try:
            # Load existing
            existing = manager.get_itinerary(itinerary_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Itinerary not found")
            
            # Update fields
            for key, value in itinerary_data.items():
                if hasattr(existing, key) and key not in ['id', 'created_at']:
                    setattr(existing, key, value)
            
            # Save
            updated = manager.update_itinerary(existing)
            
            return APIResponse(
                message="Itinerary updated successfully",
                data={"id": str(updated.id), "version": updated.version}
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating itinerary: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/api/itineraries/{itinerary_id}", response_model=APIResponse)
    async def delete_itinerary(itinerary_id: UUID = Path(...)):
        """Delete an itinerary"""
        if manager.delete_itinerary(itinerary_id):
            return APIResponse(message="Itinerary deleted successfully")
        else:
            raise HTTPException(status_code=404, detail="Itinerary not found")
    
    # Segment endpoints
    @app.post("/api/itineraries/{itinerary_id}/segments", response_model=APIResponse)
    async def add_segment(
        itinerary_id: UUID = Path(...),
        segment_data: Dict[str, Any] = Body(...)
    ):
        """Add a segment to an itinerary"""
        try:
            # Import segment types
            from ..models import (
                FlightSegment, HotelSegment, MeetingSegment,
                ActivitySegment, TransferSegment, CustomSegment
            )
            
            # Map type to class
            type_map = {
                "FLIGHT": FlightSegment,
                "HOTEL": HotelSegment,
                "MEETING": MeetingSegment,
                "ACTIVITY": ActivitySegment,
                "TRANSFER": TransferSegment,
                "CUSTOM": CustomSegment,
            }
            
            segment_type = segment_data.get('type')
            segment_class = type_map.get(segment_type)
            if not segment_class:
                raise ValueError(f"Unknown segment type: {segment_type}")
            
            # Create segment
            segment = segment_class.model_validate(segment_data)
            
            # Add to itinerary
            updated = manager.add_segment(itinerary_id, segment)
            
            return APIResponse(
                message="Segment added successfully",
                data={"segment_id": str(segment.id), "itinerary_version": updated.version}
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error adding segment: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/api/itineraries/{itinerary_id}/segments/{segment_id}", response_model=APIResponse)
    async def remove_segment(
        itinerary_id: UUID = Path(...),
        segment_id: UUID = Path(...)
    ):
        """Remove a segment from an itinerary"""
        try:
            updated = manager.remove_segment(itinerary_id, segment_id)
            return APIResponse(
                message="Segment removed successfully",
                data={"itinerary_version": updated.version}
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Error removing segment: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Validation endpoint
    @app.post("/api/validate", response_model=APIResponse)
    async def validate_itinerary(itinerary_data: Dict[str, Any] = Body(...)):
        """Validate an itinerary without saving"""
        try:
            itinerary = Itinerary.model_validate(itinerary_data)
            validation = manager.validator.validate(itinerary)
            
            return APIResponse(
                success=validation.is_valid,
                data={
                    "is_valid": validation.is_valid,
                    "errors": [{"code": e.code, "message": e.message, "field": e.field} 
                              for e in validation.errors],
                    "warnings": [{"code": w.code, "message": w.message, "field": w.field} 
                                for w in validation.warnings]
                }
            )
        except Exception as e:
            return APIResponse(
                success=False,
                errors=[{"message": str(e)}]
            )
    
    return app


def get_app() -> FastAPI:
    """Get or create the FastAPI application"""
    return create_app()