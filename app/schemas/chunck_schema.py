from pydantic import BaseModel
from typing import List


class ChunkCreate(BaseModel):
    resource_id: int
    chunk_text: str
    embedding: List[float]
    order: int


class ChunkResponse(BaseModel):
    id: int
    resource_id: int
    chunk_text: str
    embedding: List[float]
    order: int
    model_config = {"from_attributes": True}
