from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import httpx
from sqlalchemy import select, delete
from app.core.logging import get_logger
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.schemas.chat_schema import (
    ChatMessageCreate,
    ChunkSearchResult,
    ChatMessageResponse,
)
from app.services.chunk_service import ChunkService
from app.core.exceptions import NotFoundException
from app.utils.nlp import get_embedding, build_contextual_prompt
from app.faiss_index.manager import FaissManager

logger = get_logger(__name__)


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        self.chunk_service = ChunkService(session)
        self.faiss = FaissManager()

    async def create_chat_session(self, user_id: int) -> ChatSession:
        chat_session = ChatSession(user_id=user_id)
        self.session.add(chat_session)
        await self.session.commit()
        await self.session.refresh(chat_session)
        return chat_session

    async def get_chat_message_by_session_id(
        self, chat_session_id: int
    ) -> List[ChatMessage]:
        query = select(ChatMessage).where(
            ChatMessage.chat_session_id == chat_session_id
        )
        chat_messages = await self.session.execute(query)
        return chat_messages.scalars().all()

    async def get_chat_session_by_id(self, chat_session_id: int) -> ChatSession:
        chat_session = await self.session.get(ChatSession, chat_session_id)
        if not chat_session:
            raise NotFoundException("Chat session not found.")
        return chat_session

    async def add_message_to_chat_session(
        self, message: ChatMessageCreate
    ) -> ChatMessage:
        chat_message = ChatMessage(**message.model_dump())
        self.session.add(chat_message)
        await self.session.commit()
        await self.session.refresh(chat_message)
        return chat_message

    async def answer_question(
        self, chat_session_id: int, question: str, model: str, top_k: int
    ) -> ChatMessageResponse:
        chunks = await self.search_embeddings(question, top_k)
        print(f"Chunks encontrados: {len(chunks)}")
        for c in chunks:
            print("*" * 20)
            print(f"ID: {c.chunk_id}, Similarity: {c.similarity}")
            print(f"Content: {c.content}")
            print("*" * 20)
        if not chunks:
            raise NotFoundException("No se encontraron resultados relevantes.")

        context = "\n".join([chunk.content for chunk in chunks])
        prompt = build_contextual_prompt(context, question)

        answer = await self._generate_answer_with_model(model, prompt)

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
        print(f"Chat message: {chat_message.id}")
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
            chunk = await self.chunk_service.get_chunk_by_id(chunk_id)
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

    async def _generate_answer_with_model(self, model: str, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                )
                response.raise_for_status()
                return response.json().get("response", "").strip()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Error al comunicarse con Ollama ({model}): {e}")

    async def delete_chat_session(self, chat_session_id: int) -> dict:
        query = delete(ChatSession).where(ChatSession.id == chat_session_id)
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundException("Chat session not found.")
        await self.session.commit()
        return {"detail": "Chat session deleted."}
