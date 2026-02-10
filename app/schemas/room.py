# app/schemas/room.py
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoomBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10)
    price: float = Field(gt=0)
    room_type: str = Field(min_length=2, max_length=30)  # Single, Double, Suite
    image_url: str = Field(min_length=5)
    max_guests: int = Field(default=2, ge=1, le=20)
    amenities: List[str] = Field(default_factory=list)
    total_rooms: int = Field(default=5, ge=1, le=999)
    is_active: bool = True

    @field_validator("room_type", mode="before")
    @classmethod
    def normalize_room_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("amenities", mode="before")
    @classmethod
    def normalize_amenities(cls, v: Any) -> List[str]:
        """
        Accepts either:
        - list[str]  -> kept
        - "WiFi, AC" -> converted to ["WiFi", "AC"]
        - "" / None  -> []
        """
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            raw = v.strip()
            if not raw:
                return []
            return [part.strip() for part in raw.split(",") if part.strip()]
        return []


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, min_length=10)
    price: Optional[float] = Field(default=None, gt=0)
    room_type: Optional[str] = Field(default=None, min_length=2, max_length=30)
    image_url: Optional[str] = Field(default=None, min_length=5)
    max_guests: Optional[int] = Field(default=None, ge=1, le=20)
    amenities: Optional[List[str]] = None
    total_rooms: Optional[int] = Field(default=None, ge=1, le=999)
    is_active: Optional[bool] = None

    @field_validator("room_type", mode="before")
    @classmethod
    def normalize_room_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("amenities", mode="before")
    @classmethod
    def normalize_amenities(cls, v: Any) -> Optional[List[str]]:
        if v is None:
            return None
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            raw = v.strip()
            if not raw:
                return []
            return [part.strip() for part in raw.split(",") if part.strip()]
        return None


class RoomPublic(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
