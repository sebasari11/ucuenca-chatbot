from pydantic import BaseModel, ConfigDict, Field
from typing import Union, Annotated, Optional, Literal, List
from app.src.chunks.schemas import ChunkResponse
from app.src.resources.models import ResourceType
from datetime import datetime
from uuid import UUID


class ResourceBase(BaseModel):
    name: str


class PDFResourceCreate(ResourceBase):
    type: Literal["pdf"]
    filepath: str


class PostgresResourceCreate(ResourceBase):
    type: Literal["postgres"]
    host: str
    port: int
    user: str
    password: str
    database: str


ResourceCreate = Annotated[
    Union[PDFResourceCreate, PostgresResourceCreate], Field(discriminator="type")
]


class ResourceResponse(ResourceBase):
    external_id: UUID
    type: str
    filepath: Optional[str]
    host: Optional[str]
    port: Optional[int]
    user: Optional[str]
    database: Optional[str]
    processed: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    model_config = {"from_attributes": True}


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ResourceType] = None
    filepath: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    processed: Optional[bool] = None


class ResourceUpdateResponse(BaseModel):
    message: str
    resource: ResourceResponse
    model_config = {"from_attributes": True}


class ResourceProcessResponse(BaseModel):
    message: str
    resource_id: UUID
    chunks: List[ChunkResponse] = []
    model_config: ConfigDict = {"from_attributes": True}
