from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now())

    messages = relationship(
        "ChatMessage",
        back_populates="chat_session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    user = relationship("User", back_populates="sessions")
