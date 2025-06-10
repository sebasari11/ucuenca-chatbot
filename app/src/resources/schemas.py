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


class ResourceResponseBase(ResourceBase):
    external_id: UUID
    type: str
    filepath: Optional[str]
    processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = {"from_attributes": True}


class ResourceResponse(ResourceResponseBase):
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    chunks: List[ChunkResponse] = []
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
