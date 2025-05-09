from pydantic import BaseModel, Field
from typing import Union, Annotated, Optional, Literal
from app.models.source import SourceType


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


class SourceUpdateResponse(BaseModel):
    message: str
    source: SourceResponse
    model_config = {"from_attributes": True}
