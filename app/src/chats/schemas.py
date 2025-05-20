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
    id: UUID
    created_at: datetime
    messages: List[ChatMessageResponse]
    model_config = ConfigDict(from_attributes=True)


class ChunkSearchResult(BaseModel):
    chunk_id: int
    content: str
    similarity: float
