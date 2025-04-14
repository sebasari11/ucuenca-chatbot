from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.database import Base
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

    chunks = relationship(
        "ResourceChunk", back_populates="resource", cascade="all, delete-orphan"
    )
