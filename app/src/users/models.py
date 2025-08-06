from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid
from datetime import datetime
from app.core.database import Base

class UserRole(enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False
    )
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.now(), nullable=True)

    sessions = relationship("ChatSession", back_populates="user")
    
