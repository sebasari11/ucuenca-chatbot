from pydantic import BaseModel, ConfigDict
from app.schemas.chunck_schema import ChunkResponse
from typing import List


class IngestResponse(BaseModel):
    message: str
    resource_id: int
    chunks: List[ChunkResponse] = []
    model_config: ConfigDict = {"from_attributes": True}
