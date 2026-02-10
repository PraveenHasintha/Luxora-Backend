# app/services/auth_service.py
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def create_user(db: Session, data: UserCreate) -> User:
    email = data.email.lower().strip()

    existing = get_user_by_email(db, email)
    if existing:
        raise ValueError("Email is already registered")

    user = User(
        name=data.name.strip(),
        email=email,
        password=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user
