from pydantic import BaseModel, ConfigDict
from typing import List


class ChunkBase(BaseModel):
    resource_id: int
    chunk_text: str
    embedding: List[float]
    order: int


class ChunkCreate(ChunkBase):
    """Schema to create a new Chunk"""


class ChunkResponse(ChunkBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
