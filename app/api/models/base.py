from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

class ModelBase(DeclarativeBase):
    id:Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    create_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    update_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())