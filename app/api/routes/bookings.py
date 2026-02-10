# app/api/routes/bookings.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.booking import (
    AvailabilityCheck,
    AvailabilityResponse,
    BookingCreate,
    BookingCreateResponse,
    BookingPublic,
)
from app.services.booking_service import cancel_booking, check_availability, create_booking, list_bookings

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/", response_model=List[BookingPublic])
def get_all_bookings(db: Session = Depends(get_db)):
    try:
        return list_bookings(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching bookings: {str(e)}")


@router.post("/check-availability", response_model=AvailabilityResponse)
def availability(data: AvailabilityCheck, db: Session = Depends(get_db)):
    try:
        return check_availability(db, data.room_type, data.check_in, data.check_out)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")


@router.post("/", response_model=BookingCreateResponse, status_code=status.HTTP_201_CREATED)
def add_booking(data: BookingCreate, db: Session = Depends(get_db)):
    try:
        booking = create_booking(db, data)

        # Return full booking (room_type/room_name included via list_bookings formatting style)
        # We’ll reuse list_bookings logic pattern for consistent output
        # Minimal approach: build response dict here.
        room_type = booking.room.room_type if booking.room else "Unknown"
        room_name = booking.room.name if booking.room else None

        booking_public = {
            "id": booking.id,
            "booking_id": booking.booking_id,
            "name": booking.name,
            "email": booking.email,
            "phone": booking.phone,
            "room_type": room_type,
            "room_name": room_name,
            "check_in": booking.check_in,
            "check_out": booking.check_out,
            "guests": booking.guests,
            "price_per_night": booking.price_per_night,
            "total_nights": booking.total_nights,
            "total_price": booking.total_price,
            "status": booking.status,
            "special_requests": booking.special_requests,
            "created_at": booking.created_at,
        }

        return {"message": "Booking created successfully", "booking": booking_public}
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")


@router.put("/{booking_id}/cancel", response_model=dict)
def cancel(booking_id: str, db: Session = Depends(get_db)):
    """
    FIXED: cancels by public booking_id string (e.g., LUX123456), not numeric id.
    """
    try:
        booking = cancel_booking(db, booking_id)
        return {"message": "Booking cancelled successfully", "booking_id": booking.booking_id}
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling booking: {str(e)}")
