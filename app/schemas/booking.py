# app/schemas/booking.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AvailabilityCheck(BaseModel):
    room_type: str = Field(min_length=2, max_length=30)
    check_in: str
    check_out: str


class AvailabilityRoomInfo(BaseModel):
    name: str
    room_type: str
    price_per_night: float
    total_nights: int
    total_price: float
    available_rooms: int


class AvailabilityResponse(BaseModel):
    available: bool
    room: Optional[AvailabilityRoomInfo] = None
    message: Optional[str] = None


class BookingCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str
    phone: str = Field(min_length=6, max_length=30)

    room_type: str = Field(min_length=2, max_length=30)
    check_in: str
    check_out: str
    guests: int = Field(ge=1, le=20)

    special_requests: Optional[str] = ""


class BookingPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: str

    name: str
    email: str
    phone: str

    room_type: str
    room_name: Optional[str] = None

    check_in: datetime
    check_out: datetime
    guests: int

    price_per_night: float
    total_nights: int
    total_price: float

    status: str
    special_requests: Optional[str] = ""
    created_at: datetime


class BookingCreateResponse(BaseModel):
    message: str
    booking: BookingPublic
