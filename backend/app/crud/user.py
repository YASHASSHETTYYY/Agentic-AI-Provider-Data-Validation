from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_password_hash, verify_password
from app.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def create_user(db: Session, email: str, password: str, is_superuser: bool = False) -> User:
    user = User(
        email=email,
        hashed_password=create_password_hash(password),
        is_superuser=is_superuser,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
