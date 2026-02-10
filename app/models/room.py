# app/models/room.py
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    price = Column(Float, nullable=False)
    room_type = Column(String, nullable=False)  # Single, Double, Suite
    image_url = Column(String, nullable=False)

    max_guests = Column(Integer, default=2, nullable=False)
    amenities = Column(Text, default="", nullable=False)  # stored as comma string
    total_rooms = Column(Integer, default=5, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    bookings = relationship("Booking", back_populates="room")
