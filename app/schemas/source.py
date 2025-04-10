from pydantic import BaseModel, Field
from typing import Optional, Literal


class SourceBase(BaseModel):
    name: str
    type: Literal["pdf", "postgres"]


class PDFSourceCreate(SourceBase):
    filepath: str


class PostgresSourceCreate(SourceBase):
    host: str
    port: int
    user: str
    password: str
    database: str


class SourceResponse(SourceBase):
    id: int
    filepath: Optional[str]
    host: Optional[str]
    port: Optional[int]
    user: Optional[str]
    database: Optional[str]

    class Config:
        orm_mode = True
