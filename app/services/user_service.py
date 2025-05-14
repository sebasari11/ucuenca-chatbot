from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy import delete, select, or_
from fastapi import HTTPException, status
from typing import List
from datetime import datetime
from app.core.security import verify_password
from app.core.logging import get_logger
from app.core.exceptions import NotFoundException
from app.services.chat_service import ChatService
from app.models.user import User
from app.models.chat_session import ChatSession
from app.schemas.user_schema import UserCreate, UserUpdate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = get_logger(__name__)


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.chat_service = ChatService(session)

    @staticmethod
    def _get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    async def create_user(self, user: UserCreate) -> User:
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=self._get_password_hash(user.password),
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def update_user(self, user_id: int, update_data: UserUpdate) -> User:
        logger.debug(f"Updating user with id: {user_id}")

        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException(f"User with id {user_id} not found.")

        if not any([update_data.password, update_data.full_name]):
            raise ValueError("No data provided for update.")

        if update_data.full_name:
            user.full_name = update_data.full_name

        if update_data.password:
            user.hashed_password = self._get_password_hash(update_data.password)

        user.updated_at = datetime.now()

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_chat_sessions_by_user_id(self, user_id: int) -> List[ChatSession]:
        query = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
        )
        result = await self.session.execute(query)
        chat_sessions = result.scalars().all()
        if not chat_sessions:
            raise NotFoundException(
                "No se encontraron sesiones de chat para el usuario especificado."
            )
        return chat_sessions

    async def authenticate_user(self, identifier: str, password: str):
        query = select(User).where(
            or_(User.username == identifier, User.email == identifier)
        )
        result = await self.session.execute(query)
        user = result.scalars().first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )
        return user
