from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select, delete
from app.core.logging import get_logger
from app.src.chats.models import ChatSession, ChatMessage
from app.src.chats.schemas import (
    ChatMessageCreate,
    ChunkSearchResult,
    ChatMessageResponse,
)
from uuid import UUID
from app.src.chunks.service import ChunkService
from app.core.exceptions import NotFoundException
from app.utils.nlp import (
    answer_with_gemini,
    answer_with_ollama,
    get_embedding,
    build_contextual_prompt,
    build_chat_session_name_prompt,
)
from app.faiss_index.manager import FaissManager


logger = get_logger(__name__)


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        self.chunk_service = ChunkService(session)
        self.faiss = FaissManager()

    async def create_chat_session(self, user_id: int) -> ChatSession:
        chat_session = ChatSession(user_id=user_id, session_name="Nuevo Chat")
        self.session.add(chat_session)
        await self.session.commit()
        await self.session.refresh(chat_session)
        return chat_session

    async def get_chat_messages_by_session_id(
        self, chat_session_id: UUID
    ) -> List[ChatMessage]:
        chat_session = await self.get_chat_session_by_external_id(chat_session_id)

        query = select(ChatMessage).where(
            ChatMessage.chat_session_id == chat_session.id
        )
        result = await self.session.execute(query)
        chat_messages = result.scalars().all()
        return [
            ChatMessageResponse(
                id=msg.id,
                timestamp=msg.timestamp,
                question=msg.question,
                answer=msg.answer,
                chat_session_id=chat_session.external_id,
            )
            for msg in chat_messages
        ]

    async def get_chat_session_by_id(self, chat_session_id: int) -> ChatSession:
        chat_session = await self.session.get(ChatSession, chat_session_id)
        if not chat_session:
            raise NotFoundException("Chat session not found.")
        return chat_session

    async def get_chat_session_by_external_id(
        self, chat_session_id: UUID
    ) -> ChatSession:
        query = select(ChatSession).where(ChatSession.external_id == chat_session_id)
        chat_session = await self.session.execute(query)
        if not chat_session:
            raise NotFoundException("Chat session not found.")
        return chat_session.scalar_one_or_none()

    async def add_message_to_chat_session(
        self, message: ChatMessageCreate
    ) -> ChatMessage:
        chat_session = await self.get_chat_session_by_external_id(
            message.chat_session_id
        )
        message_data = message.model_dump()
        message_data["chat_session_id"] = chat_session.id
        chat_message = ChatMessage(**message_data)
        self.session.add(chat_message)
        await self.session.commit()
        await self.session.refresh(chat_message)

        return chat_message

    async def answer_question(
        self, chat_session_id: UUID, question: str, model: str, top_k: int
    ) -> ChatMessageResponse:
        chunks = await self.search_embeddings(question, top_k)        
        if not chunks:
            raise NotFoundException("No se encontraron resultados relevantes.")

        context = "\n".join([chunk.content for chunk in chunks])
        prompt = build_contextual_prompt(context, question)

        answer = await self._generate_answer_with_model(model, prompt, chat_session_id)

        if not answer:
            raise RuntimeError("No se pudo generar una respuesta.")

        chat_message: ChatMessage = await self.add_message_to_chat_session(
            message=ChatMessageCreate(
                chat_session_id=chat_session_id,
                question=question,
                answer=answer,
                model=model,
            )
        )
        return ChatMessageResponse(
            id=chat_message.id,
            answer=answer,
            timestamp=chat_message.timestamp,
            chat_session_id=chat_session_id,
            question=question,
        )

    async def search_embeddings(
        self, question: str, top_k: int
    ) -> List[ChunkSearchResult]:
        embedding = get_embedding(question=question, backend="sentence")
        chunk_ids, similarities = self.faiss.search(embedding, k=top_k)

        results = []
        for chunk_id, similarity in zip(chunk_ids, similarities):
            chunk = await self.chunk_service.get_active_chunk_by_id(chunk_id)
            if chunk:
                results.append(
                    ChunkSearchResult(
                        chunk_id=chunk.id,
                        content=chunk.chunk_text,
                        similarity=float(similarity),
                    )
                )

        results.sort(key=lambda x: x.similarity)

        print("After sorting:")
        for chunk in results:
            logger.info("*" * 20)
            logger.info(f"ID: {chunk.chunk_id}, Similarity: {chunk.similarity}")
            logger.info(f"Content: {chunk.content}")
            logger.info("*" * 20)

        return results

    def _format_history_for_gemini(self, messages_from_db: List[ChatMessage]) -> List[dict]:
        formatted_history = []
        for msg in messages_from_db:
            formatted_history.append({
                "role": "user",
                "parts": [{"text": msg.question}]
            })
            formatted_history.append({
                "role": "model",
                "parts": [{"text": msg.answer}]
            })
        return formatted_history


    async def _generate_answer_with_model(self, model: str, prompt: str, chat_session_id: UUID = None) -> str:
        if model == "gemma3:latest":
            return await answer_with_ollama(model, prompt)
        elif model == "gemini":
            chat_history = await self.get_chat_messages_by_session_id(chat_session_id)
            formatted_history = self._format_history_for_gemini(chat_history)
            logger.info(f"Formatted history for Gemini: {formatted_history}")
            return await answer_with_gemini(prompt, formatted_history)
        else:
            raise ValueError(f"Unsupported model: {model}")

    async def delete_chat_session(self, chat_session_id: UUID) -> dict:
        query = delete(ChatSession).where(ChatSession.external_id == chat_session_id)
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundException("Chat session not found.")
        await self.session.commit()
        return {"detail": "Chat session deleted."}

    async def generate_chat_session_name(self, chat_session_id: UUID) -> str:
        chat_session = await self.get_chat_session_by_external_id(chat_session_id)
        message_context = [
            f"Question: {msg.question} \n Answer: {msg.answer}"
            for msg in chat_session.messages
        ]
        if not chat_session:
            raise NotFoundException("Chat session not found.")
        chat_session_name = "Nuevo Chat"
        if len(message_context) > 0:
            prompt = build_chat_session_name_prompt("\n".join(message_context))
            chat_session_name = await self._generate_answer_with_model(
                "gemma3:latest", prompt
            )
        chat_session.session_name = chat_session_name
        await self.session.commit()
        await self.session.refresh(chat_session)
        return chat_session
