from pydantic import BaseModel, Field
from typing import Union, Annotated, Optional, Literal


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

    model_config = {"from_attributes": True}
