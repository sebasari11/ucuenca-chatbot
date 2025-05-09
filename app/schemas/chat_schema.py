from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class ChatMessageCreate(BaseModel):
    chat_session_id: int
    question: str
    answer: str | None = None
    model: str | None = None


class ChatSessionCreate(BaseModel):
    user_id: int | None = None  # TODO remover opcional


class ChatMessageResponse(BaseModel):
    id: int
    timestamp: datetime
    question: str
    chat_session_id: int
    answer: str | None = None
    model_config = ConfigDict(from_attributes=True)


class ChatSessionResponse(BaseModel):
    id: int
    created_at: datetime
    messages: List[ChatMessageResponse]
    model_config = ConfigDict(from_attributes=True)


class ChunkSearchResult(BaseModel):
    chunk_id: int
    content: str
    similarity: float
