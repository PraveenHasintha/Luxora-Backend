# app/services/booking_service.py
from datetime import datetime
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.room import Room
from app.schemas.booking import BookingCreate
from app.utils.dates import parse_date
from app.utils.ids import generate_booking_id


def _today_date() -> datetime.date:
    return datetime.now().date()


def find_room_by_type(db: Session, room_type: str) -> Room | None:
    return (
        db.query(Room)
        .filter(Room.room_type == room_type, Room.is_active == True)  # noqa: E712
        .first()
    )


def count_overlapping_confirmed(db: Session, room_id: int, check_in: datetime, check_out: datetime) -> int:
    return (
        db.query(Booking)
        .filter(
            Booking.room_id == room_id,
            Booking.status == "confirmed",
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
        .count()
    )


def check_availability(db: Session, room_type: str, check_in_str: str, check_out_str: str) -> Dict:
    check_in = parse_date(check_in_str)
    check_out = parse_date(check_out_str)

    # Validate dates
    if check_in.date() <= _today_date():
        raise ValueError("Check-in date must be in the future")
    if check_out <= check_in:
        raise ValueError("Check-out date must be after check-in date")

    room = find_room_by_type(db, room_type)
    if not room:
        return {"available": False, "message": "Room type not found"}

    overlapping = count_overlapping_confirmed(db, room.id, check_in, check_out)
    available_rooms = room.total_rooms - overlapping

    if available_rooms <= 0:
        return {"available": False, "message": "Room not available for selected dates"}

    nights = (check_out - check_in).days
    total_price = room.price * nights

    return {
        "available": True,
        "room": {
            "name": room.name,
            "room_type": room.room_type,
            "price_per_night": room.price,
            "total_nights": nights,
            "total_price": total_price,
            "available_rooms": available_rooms,
        },
    }


def _generate_unique_booking_id(db: Session) -> str:
    # Try a few times to avoid collision
    for _ in range(20):
        code = generate_booking_id()
        exists = db.query(Booking).filter(Booking.booking_id == code).first()
        if not exists:
            return code
    # Extremely unlikely
    raise RuntimeError("Could not generate unique booking id")


def create_booking(db: Session, data: BookingCreate) -> Booking:
    check_in = parse_date(data.check_in)
    check_out = parse_date(data.check_out)

    if check_in.date() <= _today_date():
        raise ValueError("Check-in date must be in the future")
    if check_out <= check_in:
        raise ValueError("Check-out date must be after check-in date")

    room = find_room_by_type(db, data.room_type)
    if not room:
        raise LookupError("Room not found")

    overlapping = count_overlapping_confirmed(db, room.id, check_in, check_out)
    if overlapping >= room.total_rooms:
        raise ValueError("Room no longer available")

    nights = (check_out - check_in).days
    total_price = room.price * nights

    booking = Booking(
        booking_id=_generate_unique_booking_id(db),
        name=data.name,
        email=data.email,
        phone=data.phone,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        guests=data.guests,
        price_per_night=room.price,
        total_nights=nights,
        total_price=total_price,
        special_requests=data.special_requests or "",
        status="confirmed",  # MVP: auto-confirm
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def list_bookings(db: Session) -> List[Dict]:
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).all()

    # Build simple, frontend-friendly dicts with room info
    results: List[Dict] = []
    for b in bookings:
        room = db.query(Room).filter(Room.id == b.room_id).first()
        results.append(
            {
                "id": b.id,
                "booking_id": b.booking_id,
                "name": b.name,
                "email": b.email,
                "phone": b.phone,
                "room_type": room.room_type if room else "Unknown",
                "room_name": room.name if room else None,
                "check_in": b.check_in,
                "check_out": b.check_out,
                "guests": b.guests,
                "price_per_night": b.price_per_night,
                "total_nights": b.total_nights,
                "total_price": b.total_price,
                "status": b.status,
                "special_requests": b.special_requests,
                "created_at": b.created_at,
            }
        )
    return results


def cancel_booking(db: Session, booking_id: str) -> Booking:
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise LookupError("Booking not found")

    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking
