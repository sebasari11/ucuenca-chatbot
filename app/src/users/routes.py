from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.database import get_session
from app.core.security import create_access_token
from app.src.users.service import UserService
from app.src.users.schemas import UserCreate, UserResponse, UserUpdate, Token
from app.src.chats.schemas import ChatSessionResponse
from app.api.deps import get_current_user, get_current_admin_user
from app.src.users.models import User

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(session)


@router.post("/", response_model=UserResponse)
async def register_user(
    user: UserCreate, service: UserService = Depends(get_user_service)
):
    return await service.create_user(user)


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    user = await service.authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value}


@router.get("/", response_model=list[UserResponse])
async def list_users(
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_admin_user),
):
    return await service.get_users()


@router.get("/me/chat_sessions", response_model=list[ChatSessionResponse])
async def get_my_chat_sessions(
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_chat_sessions_by_user_id(current_user.id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    return await service.update_user(user_id, user_update)

@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
