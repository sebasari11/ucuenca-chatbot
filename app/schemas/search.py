from pydantic import BaseModel
from typing import List, Optional


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    chunk_id: int
    content: str
    similarity: float


class SearchResponse(BaseModel):
    results: List[SearchResult]


class SearchSmartResponse(BaseModel):
    answer: str
