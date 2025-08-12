"""
Itinerizer data models for travel itinerary management.
"""

from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Union, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


# ============== ENUMS ==============

class ItineraryStatus(str, Enum):
    DRAFT = "DRAFT"
    PLANNED = "PLANNED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SegmentType(str, Enum):
    FLIGHT = "FLIGHT"
    HOTEL = "HOTEL"
    CAR_RENTAL = "CAR_RENTAL"
    TRAIN = "TRAIN"
    MEETING = "MEETING"
    ACTIVITY = "ACTIVITY"
    TRANSFER = "TRANSFER"
    CUSTOM = "CUSTOM"


class SegmentStatus(str, Enum):
    TENTATIVE = "TENTATIVE"
    CONFIRMED = "CONFIRMED"
    WAITLISTED = "WAITLISTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class TravelerType(str, Enum):
    ADULT = "ADULT"
    CHILD = "CHILD"
    INFANT = "INFANT"
    SENIOR = "SENIOR"


# ============== BASE MODELS ==============

class StrictModel(BaseModel):
    """Base model with strict validation"""
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        extra='forbid',
        json_encoders={
            UUID: str,
            Decimal: str,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )


class Money(StrictModel):
    amount: Decimal = Field(..., ge=0)
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    
    @field_validator('amount', mode='before')
    @classmethod
    def coerce_decimal(cls, v):
        if isinstance(v, (int, float, str)):
            return Decimal(str(v)).quantize(Decimal('0.01'))
        return v


class Coordinates(StrictModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class Address(StrictModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = Field(..., pattern="^[A-Z]{2}$")


class Location(StrictModel):
    name: str
    code: Optional[str] = None
    address: Optional[Address] = None
    coordinates: Optional[Coordinates] = None
    timezone: Optional[str] = None


class Company(StrictModel):
    name: str
    code: Optional[str] = None
    website: Optional[str] = None


class LoyaltyProgram(StrictModel):
    carrier: str
    number: str
    tier: Optional[str] = None


class Traveler(StrictModel):
    id: UUID = Field(default_factory=uuid4)
    type: TravelerType
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    passport_number: Optional[str] = None
    passport_expiry: Optional[date] = None
    passport_country: Optional[str] = Field(None, pattern="^[A-Z]{2}$")
    loyalty_programs: List[LoyaltyProgram] = Field(default_factory=list)
    special_requests: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============== SEGMENTS ==============

class BaseSegment(StrictModel):
    """Base class for all segment types"""
    id: UUID = Field(default_factory=uuid4)
    type: SegmentType
    status: SegmentStatus = SegmentStatus.TENTATIVE
    start_datetime: datetime
    end_datetime: datetime
    traveler_ids: List[UUID] = Field(..., min_length=1)
    
    confirmation_number: Optional[str] = None
    booking_reference: Optional[str] = None
    provider: Optional[Company] = None
    
    price: Optional[Money] = None
    taxes: Optional[Money] = None
    fees: Optional[Money] = None
    total_price: Optional[Money] = None
    
    notes: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_datetime_order(self):
        if self.end_datetime <= self.start_datetime:
            raise ValueError("end_datetime must be after start_datetime")
        return self


class FlightSegment(BaseSegment):
    type: Literal[SegmentType.FLIGHT] = SegmentType.FLIGHT
    flight_number: str
    airline: Company
    origin: Location
    destination: Location
    departure_datetime: datetime
    arrival_datetime: datetime
    
    aircraft: Optional[str] = None
    cabin: Optional[Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]] = None
    booking_class: Optional[str] = None
    seat_assignments: Dict[str, str] = Field(default_factory=dict)  # traveler_id -> seat
    duration_minutes: Optional[int] = None
    
    @model_validator(mode='before')
    @classmethod
    def sync_times(cls, values):
        # Sync times during initialization, not after
        if isinstance(values, dict):
            if 'departure_datetime' in values and 'start_datetime' not in values:
                values['start_datetime'] = values['departure_datetime']
            if 'arrival_datetime' in values and 'end_datetime' not in values:
                values['end_datetime'] = values['arrival_datetime']
            
            # Validate arrival after departure
            if 'arrival_datetime' in values and 'departure_datetime' in values:
                if values['arrival_datetime'] <= values['departure_datetime']:
                    raise ValueError("arrival must be after departure")
        return values


class HotelSegment(BaseSegment):
    type: Literal[SegmentType.HOTEL] = SegmentType.HOTEL
    property: Company
    location: Location
    check_in_date: date
    check_out_date: date
    check_in_time: str = "15:00"
    check_out_time: str = "11:00"
    
    room_type: Optional[str] = None
    room_count: int = 1
    board_basis: Optional[Literal[
        "ROOM_ONLY", "BED_BREAKFAST", "HALF_BOARD", 
        "FULL_BOARD", "ALL_INCLUSIVE"
    ]] = "ROOM_ONLY"
    cancellation_policy: Optional[str] = None
    amenities: List[str] = Field(default_factory=list)
    
    @model_validator(mode='before')
    @classmethod
    def sync_dates(cls, values):
        # Convert check-in/out dates to datetime for start/end during initialization
        if isinstance(values, dict):
            if 'check_in_date' in values and 'start_datetime' not in values:
                check_in_time = values.get('check_in_time', '15:00')
                check_in_hour = int(check_in_time.split(':')[0])
                values['start_datetime'] = datetime.combine(
                    values['check_in_date'], 
                    datetime.min.time().replace(hour=check_in_hour)
                )
            
            if 'check_out_date' in values and 'end_datetime' not in values:
                check_out_time = values.get('check_out_time', '11:00')
                check_out_hour = int(check_out_time.split(':')[0])
                values['end_datetime'] = datetime.combine(
                    values['check_out_date'],
                    datetime.min.time().replace(hour=check_out_hour)
                )
            
            # Validate checkout after checkin
            if 'check_out_date' in values and 'check_in_date' in values:
                if values['check_out_date'] <= values['check_in_date']:
                    raise ValueError("check_out_date must be after check_in_date")
        return values


class MeetingSegment(BaseSegment):
    type: Literal[SegmentType.MEETING] = SegmentType.MEETING
    title: str
    location: Location
    organizer: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)
    agenda: Optional[str] = None
    meeting_url: Optional[str] = None
    dial_in: Optional[str] = None


class ActivitySegment(BaseSegment):
    type: Literal[SegmentType.ACTIVITY] = SegmentType.ACTIVITY
    name: str
    description: Optional[str] = None
    location: Location
    category: Optional[str] = None
    voucher_number: Optional[str] = None


class TransferSegment(BaseSegment):
    type: Literal[SegmentType.TRANSFER] = SegmentType.TRANSFER
    transfer_type: Literal["TAXI", "SHUTTLE", "PRIVATE", "PUBLIC", "RIDE_SHARE"]
    pickup_location: Location
    dropoff_location: Location
    vehicle_details: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None


class CustomSegment(BaseSegment):
    type: Literal[SegmentType.CUSTOM] = SegmentType.CUSTOM
    title: str
    description: Optional[str] = None
    location: Optional[Location] = None
    custom_data: Dict[str, Any] = Field(default_factory=dict)


# Union type for segments
Segment = Union[
    FlightSegment, HotelSegment, MeetingSegment,
    ActivitySegment, TransferSegment, CustomSegment
]


# ============== ITINERARY MODEL ==============

class TravelPreferences(StrictModel):
    seat_preference: Optional[Literal["AISLE", "WINDOW", "MIDDLE"]] = None
    meal_preference: Optional[str] = None
    hotel_chain_preference: List[str] = Field(default_factory=list)
    accessibility: List[str] = Field(default_factory=list)


class Itinerary(StrictModel):
    # Identification
    id: UUID = Field(default_factory=uuid4)
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Basic Info
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: ItineraryStatus = ItineraryStatus.DRAFT
    
    # Trip Details
    start_date: date
    end_date: date
    origin: Optional[Location] = None
    destinations: List[Location] = Field(default_factory=list)
    
    # People
    travelers: List[Traveler] = Field(..., min_length=1)
    primary_traveler_id: Optional[UUID] = None
    created_by: Optional[str] = None
    
    # Components - Using discriminated union
    segments: List[Segment] = Field(default_factory=list)
    
    # Financial
    total_price: Optional[Money] = None
    currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    
    # Organization
    trip_type: Optional[Literal["LEISURE", "BUSINESS", "MIXED"]] = None
    cost_center: Optional[str] = None
    project_code: Optional[str] = None
    
    # Preferences
    preferences: Optional[TravelPreferences] = None
    
    # Extensibility
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after or equal to start_date")
        return self
    
    @model_validator(mode='after')
    def validate_primary_traveler(self):
        if self.primary_traveler_id:
            traveler_ids = {t.id for t in self.travelers}
            if self.primary_traveler_id not in traveler_ids:
                raise ValueError("primary_traveler_id must reference an existing traveler")
        return self
    
    def calculate_total_price(self) -> Optional[Money]:
        """Calculate total price from segments"""
        if not self.segments:
            return None
        
        total = Decimal(0)
        currency = None
        
        for segment in self.segments:
            if segment.total_price:
                if currency and currency != segment.total_price.currency:
                    raise ValueError("Mixed currencies in segments")
                currency = segment.total_price.currency
                total += segment.total_price.amount
        
        return Money(amount=total, currency=currency) if currency else None