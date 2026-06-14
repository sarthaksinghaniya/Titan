import uuid
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, BOOLEAN, TIMESTAMP

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(VARCHAR(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    is_admin: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
