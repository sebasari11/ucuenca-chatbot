from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List


class ChatMessageCreate(BaseModel):
    chat_session_id: UUID
    question: str
    answer: str | None = None
    model: str | None = None


class ChatMessageResponse(BaseModel):
    id: int
    timestamp: datetime
    question: str
    chat_session_id: UUID
    answer: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ChatSessionResponse(BaseModel):
    external_id: UUID
    created_at: datetime
    session_name: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ChatSessionResponseWithMessages(ChatSessionResponse):
    messages: List[ChatMessageResponse] = []
    user_id: UUID | None = None
    session_name: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ChunkSearchResult(BaseModel):
    chunk_id: int
    content: str
    similarity: float
