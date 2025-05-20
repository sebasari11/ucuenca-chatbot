from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError
from app.core.database import get_session
from app.core.security import decode_token
from app.core.logging import get_logger
from app.src.users.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
logger = get_logger(__name__)


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
) -> User:
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            logger.error("Token inválido: [User Name] no encontrado")
            raise HTTPException(status_code=401, detail="[User Name] Token inválido")
    except JWTError as e:
        logger.error(f"Token inválido: {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido")

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
