from sqlalchemy import Column, Integer, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from app.models.source import Source
from app.core.database import Base


class ResourceChunk(Base):
    __tablename__ = "resource_chunks"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("sources.id"))
    chunk_text = Column(Text, nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)
    order = Column(Integer, nullable=False)

    resource = relationship("Source", back_populates="chunks")
