from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from typing import List
from app.core.logging import get_logger
from sqlalchemy import delete, select, update
from fastapi import HTTPException
from datetime import datetime
from app.models.source import Source, SourceType
from app.services.chunk_service import ChunkService
from app.schemas.chunk_schema import ChunkCreate
from app.schemas.source_schema import SourceCreate, SourceUpdate
from app.core.exceptions import NotFoundException, AlreadyExistsException
from app.utils.pdf_reader import extract_text_from_pdf
from app.utils.nlp import sentence_chunker, generate_embeddings
from app.faiss_index.manager import FaissManager


faiss_manager = FaissManager()
logger = get_logger(__name__)


class SourceService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        self.chunk_service = ChunkService(session)

    def _create_pdf_source(self, source: SourceCreate):
        return Source(name=source.name, type=SourceType.pdf, filepath=source.filepath)

    def _create_postgres_source(self, source: SourceCreate):
        return Source(
            name=source.name,
            type=SourceType.postgres,
            host=source.host,
            port=source.port,
            user=source.user,
            password=source.password,
            database=source.database,
        )

    async def create_source(self, source: SourceCreate):
        if source.type == "pdf":
            new_source: Source = self._create_pdf_source(source)
        elif source.type == "postgres":
            new_source: Source = self._create_postgres_source(source)
        else:
            raise HTTPException(status_code=400, detail="Tipo de fuente no soportado")
        try:
            self.session.add(new_source)
            await self.session.commit()
            await self.session.refresh(new_source)
            return new_source
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error intento insertar el Recurso {source.name}: {str(e)}")
            raise

    async def get_by_id(self, source_id: int) -> Source:
        query = select(Source).where(Source.id == source_id)
        result = await self.session.execute(query)
        source = result.scalar_one_or_none()
        if not source:
            raise NotFoundException(f"Recurso con id {source_id} no encontrado.")
        return source

    async def get_all_sources(self):
        query = select(Source)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_source(
        self, source_id: int, source_data: SourceUpdate, user_id: int
    ):
        update_data = source_data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("No hay campos para actualizar.")
        query = (
            update(Source)
            .where(Source.id == source_id)
            .values(**update_data, updated_by_id=user_id, updated_at=datetime.now())
        )
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundException(f"Recurso con id {source_id} no encontrado")
        await self.session.commit()
        return await self.get_by_id(source_id)

    async def delete_source(self, source_id: int):
        query = delete(Source).where(Source.id == source_id)
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundException(f"Recurso con id {source_id} no encontrado.")
        await self.session.commit()
        return {"detail": f"Recurso {source_id} eliminado"}

    async def process_resource(self, resource_id: int, user_id: int):
        resource = await self._get_and_validate_resource(resource_id)
        absolute_path = self._build_safe_absolute_path(resource)

        text = extract_text_from_pdf(absolute_path)
        chunks = sentence_chunker(text, max_sentences=10)
        embeddings = generate_embeddings(chunks)

        chunks = await self._store_chunks(resource.id, chunks, embeddings)
        chunk_ids = [chunk.id for chunk in chunks]
        self._store_in_faiss(embeddings, chunk_ids)
        await self._mark_resource_as_processed(resource.id, user_id)

        logger.info(
            f"{len(chunks)} chunks procesados y almacenados para recurso {resource_id}"
        )
        return chunks

    async def _get_and_validate_resource(self, resource_id: int):
        resource: Source = await self.get_by_id(resource_id)

        if not resource:
            raise NotFoundException(
                f"Recurso con ID {resource_id} no encontrado en la base de datos"
            )

        if resource.processed:
            raise AlreadyExistsException(
                f"El recurso '{resource.name}' ya fue procesado."
            )

        return resource

    def _build_safe_absolute_path(self, resource) -> Path:
        filename = f"{resource.name}.{resource.type.value}"
        relative_path = Path(resource.filepath.strip("/\\")).joinpath(filename)
        absolute_path = relative_path.resolve()

        if not absolute_path.exists():
            raise NotFoundException(f"Archivo no encontrado: {absolute_path}")

        return absolute_path

    async def _store_chunks(
        self, resource_id: int, chunks: List[str], embeddings: List[List[float]]
    ) -> List[int]:
        created_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            new_chunk = ChunkCreate(
                resource_id=resource_id, chunk_text=chunk, embedding=embedding, order=i
            )
            created = await self.chunk_service.create_chunk(new_chunk)
            if created:
                created_chunks.append(created)
        return created_chunks

    def _store_in_faiss(self, embeddings: List[List[float]], chunk_ids: List[int]):
        faiss_manager.add_embeddings(embeddings, chunk_ids)

    async def _mark_resource_as_processed(self, resource_id: int, user_id: int):
        update_data = SourceUpdate(processed=True, updated_by_id=user_id)
        await self.update_source(resource_id, update_data)
