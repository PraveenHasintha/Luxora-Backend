# app/db/init_db.py
from app.db.session import engine
from app.db.base import Base

# Import models so SQLAlchemy registers them before create_all
from app.models.user import User  # noqa: F401
from app.models.room import Room  # noqa: F401
from app.models.booking import Booking  # noqa: F401


def init_db() -> None:
    """
    Creates database tables if they don't exist.
    (SQLite dev-friendly; later can be replaced by migrations.)
    """
    Base.metadata.create_all(bind=engine)
