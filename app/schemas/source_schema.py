from pydantic import BaseModel, ConfigDict, Field
from typing import Union, Annotated, Optional, Literal
from app.schemas.chunk_schema import ChunkResponse
from app.models.source import SourceType
from typing import List


class SourceBase(BaseModel):
    name: str


class PDFSourceCreate(SourceBase):
    type: Literal["pdf"]
    filepath: str


class PostgresSourceCreate(SourceBase):
    type: Literal["postgres"]
    host: str
    port: int
    user: str
    password: str
    database: str


SourceCreate = Annotated[
    Union[PDFSourceCreate, PostgresSourceCreate], Field(discriminator="type")
]


class SourceResponse(SourceBase):
    id: int
    type: str
    filepath: Optional[str]
    host: Optional[str]
    port: Optional[int]
    user: Optional[str]
    database: Optional[str]
    processed: Optional[bool]
    model_config = {"from_attributes": True}


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[SourceType] = None
    filepath: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    processed: Optional[bool] = None
    updated_by_id: int


class SourceUpdateResponse(BaseModel):
    message: str
    source: SourceResponse
    model_config = {"from_attributes": True}


class SourceProcessResponse(BaseModel):
    message: str
    resource_id: int
    chunks: List[ChunkResponse] = []
    model_config: ConfigDict = {"from_attributes": True}
