# app/services/room_service.py
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.room import Room
from app.schemas.room import RoomCreate, RoomUpdate


def amenities_list_to_string(amenities: List[str]) -> str:
    # Store as "WiFi, AC, TV" (simple for SQLite)
    return ", ".join([a.strip() for a in amenities if a.strip()])


def list_rooms(db: Session, include_inactive: bool = False) -> List[Room]:
    q = db.query(Room)
    if not include_inactive:
        q = q.filter(Room.is_active == True)  # noqa: E712
    return q.order_by(Room.price.asc()).all()


def get_room_by_id(db: Session, room_id: int) -> Optional[Room]:
    return db.query(Room).filter(Room.id == room_id).first()


def create_room(db: Session, data: RoomCreate) -> Room:
    room = Room(
        name=data.name,
        description=data.description,
        price=data.price,
        room_type=data.room_type,
        image_url=data.image_url,
        max_guests=data.max_guests,
        amenities=amenities_list_to_string(data.amenities),
        total_rooms=data.total_rooms,
        is_active=data.is_active,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def update_room(db: Session, room: Room, data: RoomUpdate) -> Room:
    payload = data.model_dump(exclude_unset=True)

    if "amenities" in payload and payload["amenities"] is not None:
        payload["amenities"] = amenities_list_to_string(payload["amenities"])

    for key, value in payload.items():
        setattr(room, key, value)

    db.commit()
    db.refresh(room)
    return room


def deactivate_room(db: Session, room: Room) -> Room:
    room.is_active = False
    db.commit()
    db.refresh(room)
    return room


def init_sample_rooms(db: Session) -> dict:
    existing_count = db.query(Room).count()
    if existing_count > 0:
        return {"message": "Sample data already exists", "rooms_count": existing_count}

    sample_rooms = [
        {
            "name": "Cozy Single Room",
            "description": "Perfect for solo travelers. Comfortable single bed with modern amenities and city view.",
            "price": 120.0,
            "room_type": "Single",
            "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800",
            "max_guests": 1,
            "amenities": ["WiFi", "AC", "TV", "Mini Fridge", "City View"],
            "total_rooms": 8,
        },
        {
            "name": "Deluxe Double Room",
            "description": "Spacious room with queen bed, perfect for couples. Includes balcony and premium amenities.",
            "price": 180.0,
            "room_type": "Double",
            "image_url": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800",
            "max_guests": 2,
            "amenities": ["WiFi", "AC", "Smart TV", "Mini Bar", "City View", "Balcony", "Coffee Machine"],
            "total_rooms": 6,
        },
        {
            "name": "Luxury Suite",
            "description": "Ultimate luxury experience with separate living area, premium amenities, and stunning ocean view.",
            "price": 350.0,
            "room_type": "Suite",
            "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
            "max_guests": 4,
            "amenities": ["WiFi", "AC", "Smart TV", "Mini Bar", "Ocean View", "Jacuzzi", "Butler Service", "Living Area"],
            "total_rooms": 3,
        },
    ]

    created_names = []
    for r in sample_rooms:
        room = Room(
            name=r["name"],
            description=r["description"],
            price=r["price"],
            room_type=r["room_type"],
            image_url=r["image_url"],
            max_guests=r["max_guests"],
            amenities=amenities_list_to_string(r["amenities"]),
            total_rooms=r["total_rooms"],
            is_active=True,
        )
        db.add(room)
        created_names.append(room.name)

    db.commit()
    return {
        "message": "Sample room data created successfully",
        "rooms_created": created_names,
        "total_rooms": len(created_names),
    }
