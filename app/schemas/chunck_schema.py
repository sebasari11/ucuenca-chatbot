from pydantic import BaseModel, ConfigDict
from typing import List


class ChunckBase(BaseModel):
    resource_id: int
    chunk_text: str
    embedding: List[float]
    order: int


class ChunkCreate(ChunckBase):
    """Schema to create a new Chunck"""


class ChunkResponse(ChunckBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
