from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class SourceType(str, enum.Enum):
    pdf = "pdf"
    postgres = "postgres"


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(SourceType), nullable=False)
    filepath = Column(String, nullable=True)
    host = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    user = Column(String, nullable=True)
    password = Column(String, nullable=True)
    database = Column(String, nullable=True)
    processed = Column(Boolean, default=False, nullable=False)

    chunks = relationship(
        "ResourceChunk", back_populates="resource", cascade="all, delete-orphan"
    )
