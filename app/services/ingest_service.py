import asyncio
from pathlib import Path
from typing import List
from logging import Logger
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.chunck_schema import ChunkCreate
from app.schemas.source_schema import SourceUpdate
from app.services.source_service import SourceService
from app.services.chunck_service import ChunckService
from app.utils.pdf_reader import extract_text_from_pdf
from app.utils.nlp import sentence_chunker, generate_embeddings
from app.faiss_index.manager import FaissManager
from app.core.logging import get_logger
from app.core.exceptions import AlreadyExistsException, NotFoundException

faiss_manager = FaissManager()

logger: Logger = get_logger(__name__)


class IngestService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        self.source_service = SourceService(session)
        self.chunk_service = ChunckService(session)

    async def process_resource(self, resource_id: int):
        resource = await self._get_and_validate_resource(resource_id)
        absolute_path = self._build_safe_absolute_path(resource)

        text = extract_text_from_pdf(absolute_path)
        chunks = sentence_chunker(text, max_sentences=10)
        embeddings = generate_embeddings(chunks)

        chunks = await self._store_chunks(resource.id, chunks, embeddings)
        chunk_ids = [chunk.id for chunk in chunks]
        self._store_in_faiss(embeddings, chunk_ids)
        await self._mark_resource_as_processed(resource.id)

        logger.info(
            f"{len(chunks)} chunks procesados y almacenados para recurso {resource_id}"
        )
        return chunks

    async def _get_and_validate_resource(self, resource_id: int):
        resource = await self.source_service.get_by_id(resource_id)

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

        created_chunks = await asyncio.gather(*tasks)
        return [chunk for chunk in created_chunks if chunk is not None]

    def _store_in_faiss(self, embeddings: List[List[float]], chunk_ids: List[int]):
        faiss_manager.add_embeddings(embeddings, chunk_ids)

    async def _mark_resource_as_processed(self, resource_id: int):
        update_data = SourceUpdate(processed=True)
        await self.source_service.update_source(resource_id, update_data)
