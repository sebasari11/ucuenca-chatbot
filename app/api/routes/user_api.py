from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.user_service import UserService
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.schemas.chat_schema import ChatSessionResponse

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


@router.post("/", response_model=UserResponse)
async def register_user(
    user: UserCreate, service: UserService = Depends(get_user_service)
):
    return await service.create_user(user)


@router.get("/{user_id}", response_model=list[ChatSessionResponse])
async def get_user_chat_sessions(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    return await service.get_chat_sessions_by_user_id(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(user_id, user_update)
