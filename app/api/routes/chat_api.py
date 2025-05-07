from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.chat_session import ChatSession
from app.services.chat_service import ChatService
from app.schemas.chat_schema import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_chat_service(session: AsyncSession = Depends(get_session)):
    return ChatService(session)


@router.post("/sessions/start", response_model=ChatSessionResponse)
async def start_chat(
    session_data: ChatSessionCreate = None,
    service: ChatService = Depends(get_chat_service),
):
    session: ChatSession = await service.create_chat_session(
        user_id=session_data.user_id if session_data else None
    )
    return session


@router.post("/sessions/send_message", response_model=ChatMessageResponse)
async def send_message(
    message: ChatMessageCreate,
    service: ChatService = Depends(get_chat_service),
):
    model = message.model or "gemma3:latest"

    return await service.answer_question(
        message.chat_session_id, message.question, model=model, top_k=5
    )


@router.get(
    "/sessions/{chat_session_id}/messages", response_model=list[ChatMessageResponse]
)
async def get_session_messages(
    chat_session_id: int,
    service: ChatService = Depends(get_chat_service),
):
    return await service.get_chat_message_by_session_id(chat_session_id)


@router.delete("/sessions/{chat_session_id}")
async def delete_chat_session(
    chat_session_id: int,
    service: ChatService = Depends(get_chat_service),
):
    return await service.delete_chat_session(chat_session_id)
