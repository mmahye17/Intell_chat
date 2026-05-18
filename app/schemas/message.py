from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    conv_id: Optional[int] = None   # null=新对话
    title: Optional[str] = "新对话"
    query: str


class MessageItem(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SourceItem(BaseModel):
    content: str
    score: float


class SendMessageResponse(BaseModel):
    conv_id: int
    title: str
    user_message: MessageItem
    assistant_message: MessageItem
    sources: list[SourceItem] = []
