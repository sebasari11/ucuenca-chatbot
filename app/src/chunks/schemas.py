from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID


class ChunkBase(BaseModel):
    resource_id : int     
    chunk_text: str
    embedding: List[float]
    order: int


class ChunkResponse(ChunkBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
