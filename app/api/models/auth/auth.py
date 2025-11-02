

from app.api.models import ModelBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class User(ModelBase):

    __tablename__ = "Users"

    username:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password:Mapped[str] = mapped_column(String, nullable=True)


    def __str__(self):
        return self.username