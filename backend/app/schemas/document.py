from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentItem(BaseModel):
    id: int
    message_id: int = 0
    filename: str
    file_size: Optional[int] = None
    chunk_count: int = 0
    status: str = "completed"
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
