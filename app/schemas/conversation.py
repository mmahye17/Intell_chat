from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: Optional[str] = "新对话"


class ConversationRename(BaseModel):
    title: str


from app.schemas.message import MessageItem
from app.schemas.document import DocumentItem


class ConversationItem(BaseModel):
    id: int
    user_id: int
    title: str
    conversion_name: Optional[str] = None
    last_message: Optional[str] = None
    summary: Optional[str] = None
    message_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    conv_id: int
    title: str
    messages: list[MessageItem]
    documents: list[DocumentItem]
