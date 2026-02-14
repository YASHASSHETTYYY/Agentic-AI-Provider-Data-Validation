from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.user import create_user, get_by_email


def bootstrap_admin_user(db: Session) -> None:
    admin = get_by_email(db, settings.bootstrap_admin_email)
    if admin:
        return
    create_user(
        db=db,
        email=settings.bootstrap_admin_email,
        password=settings.bootstrap_admin_password,
        is_superuser=True,
    )
