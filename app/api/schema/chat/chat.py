from app.api.schema import Base
from typing import Any, Optional,Dict

class ChatStreamInput(Base):
    query: str

class ChatStreamChunk(Base):
    content: str
    is_final: bool = False
    meta_data:Optional[Dict[str,Any]] = {}
