# app/api/routes/rooms.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.room import RoomCreate, RoomPublic, RoomUpdate
from app.services.room_service import (
    create_room,
    deactivate_room,
    get_room_by_id,
    init_sample_rooms,
    list_rooms,
    update_room,
)

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=List[RoomPublic])
def get_rooms(
    include_inactive: bool = Query(default=False, description="Set true to include inactive rooms"),
    db: Session = Depends(get_db),
):
    return list_rooms(db, include_inactive=include_inactive)


@router.get("/{room_id}", response_model=RoomPublic)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@router.post("/", response_model=RoomPublic, status_code=status.HTTP_201_CREATED)
def add_room(data: RoomCreate, db: Session = Depends(get_db)):
    try:
        return create_room(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating room: {str(e)}")


@router.put("/{room_id}", response_model=RoomPublic)
def edit_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)):
    room = get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    try:
        return update_room(db, room, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating room: {str(e)}")


@router.delete("/{room_id}", response_model=RoomPublic)
def remove_room(room_id: int, db: Session = Depends(get_db)):
    room = get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    try:
        return deactivate_room(db, room)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating room: {str(e)}")


@router.post("/init-sample-data")
def seed_sample_rooms(db: Session = Depends(get_db)):
    """
    Keeps your original endpoint name for convenience.
    Later we can protect this as an admin-only endpoint.
    """
    try:
        return init_sample_rooms(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sample data: {str(e)}")
