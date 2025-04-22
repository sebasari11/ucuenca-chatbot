from pydantic import BaseModel
from typing import List


class AskRequest(BaseModel):
    query: str
    top_k: int = 3
    model: str = "gemma3:latest"


class AskResponse(BaseModel):
    answer: str
    context_chunks: List[str]
