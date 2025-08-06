from sqlalchemy import Column, Integer, String, Enum, Boolean, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from sqlalchemy.dialects.postgresql import UUID
import uuid


class ResourceType(str, enum.Enum):
    pdf = "pdf"
    postgres = "postgres"
    url = "url"


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False
    )
    name = Column(String, nullable=False)
    type = Column(Enum(ResourceType), nullable=False)
    filepath = Column(String, nullable=True)
    host = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    user = Column(String, nullable=True)
    password = Column(String, nullable=True)
    database = Column(String, nullable=True)
    processed = Column(Boolean, default=False, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    active = Column(Boolean, default=True, nullable=False)


    chunks = relationship(
        "ResourceChunk", back_populates="resource", cascade="all, delete-orphan"
    )
