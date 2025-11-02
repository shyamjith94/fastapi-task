from uuid import UUID
from app.api.models import ModelBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, ForeignKey
from app.api.models import User


class Files(ModelBase):
    __tablename__ = "files"
    
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    path:Mapped[str] = mapped_column(String, nullable=False)
    process_status:Mapped[bool] = mapped_column(Boolean, nullable=True) 

    user_id:Mapped[UUID] = mapped_column(ForeignKey("Users.id", ondelete="CASCADE"), nullable=False,)
    user:Mapped[User] = relationship("User",)
    
    def __str__(self):
        return self.file_name
    