from datetime import datetime
from typing import Optional
from pydantic import BaseModel,UUID4
from uuid import UUID

class Base(BaseModel):
    pass


class CommonBase(BaseModel):
    id: UUID
    create_at: datetime
    update_at: datetime