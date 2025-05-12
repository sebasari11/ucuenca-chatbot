from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import verify_password


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def authenticate_user(self, email: str, password: str):
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )
        return user
