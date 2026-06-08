from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    # fastapi-users supplies: id, email, hashed_password,
    # is_active, is_superuser, is_verified
    __tablename__ = "users"
    role:       Mapped[str] = mapped_column(String, default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
