from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.api.deps import get_current_user
from app.src.chats.models import ChatSession
from app.src.users.models import User
from app.src.chats.service import ChatService
from app.src.chats.schemas import (
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionResponseWithMessages,
)
from uuid import UUID

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_chat_service(session: AsyncSession = Depends(get_session)):
    return ChatService(session)


@router.post("/sessions/start", response_model=ChatSessionResponse)
async def start_chat(
    service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    session: ChatSession = await service.create_chat_session(
        user_id=current_user.id,
    )

    return session


@router.post("/sessions/send_message", response_model=ChatMessageResponse)
async def send_message(
    message: ChatMessageCreate,
    service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    model = message.model or "gemma3:latest"

    return await service.answer_question(
        message.chat_session_id, message.question, model=model, top_k=10
    )


@router.get(
    "/sessions/{chat_session_id}/messages",
    response_model=list[ChatMessageResponse],
)
async def get_session_messages(
    chat_session_id: UUID,
    service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_chat_messages_by_session_id(chat_session_id)


@router.delete("/sessions/{chat_session_id}")
async def delete_chat_session(
    chat_session_id: UUID,
    service: ChatService = Depends(get_chat_service),
    current_user: User = Depends(get_current_user),
):
    return await service.delete_chat_session(chat_session_id)
