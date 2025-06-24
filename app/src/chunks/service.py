from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete, select
from app.core.logging import get_logger
from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.faiss_index.manager import FaissManager
from app.src.chunks.models import ResourceChunk
from app.src.chunks.schemas import ChunkBase as ChunkCreate
from app.src.resources.models import Resource
from sqlalchemy.orm import aliased


logger = get_logger(__name__)


class ChunkService:

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        self.resourceAlias = aliased(Resource)

    async def create_chunk(self, chunk: ChunkCreate) -> ResourceChunk:
        new_chunk = ResourceChunk(**chunk.model_dump())
        try:
            self.session.add(new_chunk)
            await self.session.commit()
            await self.session.refresh(new_chunk)
            return new_chunk
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistsException(f"ResourceChunk already exists.")

    async def get_all_chunks(self):
        query = select(ResourceChunk)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_chunks_by_resource_id(self, resource_id: UUID):
        query = (
            select(ResourceChunk)
            .where(ResourceChunk.resource_id == self.resourceAlias.id)
            .where(self.resourceAlias.external_id == resource_id)
        )
        result = await self.session.execute(query)
        chunks = list(result.scalars().all())
        for chunk in chunks:
            chunk.resource_external_id = chunk.resource.external_id
        return chunks

    async def get_chunk_by_id(self, chunk_id: int):
        query = select(ResourceChunk).where(ResourceChunk.id == chunk_id)
        result = await self.session.execute(query)
        chunk = result.scalars().first()
        if not chunk:
            raise NotFoundException(f"Chunk con id {chunk_id} no encontrado.")
        return chunk
    
    async def get_active_chunk_by_id(self, chunk_id: int):
        query = (
            select(ResourceChunk)
            .join(Resource)
            .where(
                ResourceChunk.id == chunk_id,
                Resource.active.is_(True)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_chunk(self, chunk_id: int):
        query = delete(ResourceChunk).where(ResourceChunk.id == chunk_id)
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundException(f"Chunk con id {chunk_id} no encontrado.")
        await self.session.commit()
        return {"detail": "Chunck eliminado"}

    async def delete_chunks_by_resource_id(self, resource_id: UUID):
        query = (
            delete(ResourceChunk)
            .where(ResourceChunk.resource_id == self.resourceAlias.id)
            .where(self.resourceAlias.external_id == resource_id)
        )
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundException(
                detail=f"No se encontrar chunks para el resource_id {resource_id} especificado.",
            )
        await self.session.commit()
        return {
            "message": f"Se eliminaron {result.rowcount} chunks para el siguiente resource_id {resource_id}."
        }
        
    async def rebuild_faiss_index(db: AsyncSession, dim: int = 384):
        faiss = FaissManager()
        faiss.reset_index(dim=dim)

        query = (
            select(ResourceChunk)
            .join(Resource)
            .where(Resource.active.is_(True) and Resource.processed.is_(True))
        )

        result = await db.execute(query)
        chunks = result.scalars().all()

        if not chunks:
            logger.warning("No hay chunks activos para indexar.")
            return

        embeddings = [chunk.embedding for chunk in chunks]
        chunk_ids = [chunk.id for chunk in chunks]

        faiss.add_embeddings(embeddings, chunk_ids)

        logger.info(f"✅ Se reconstruyó el índice FAISS con {len(chunk_ids)} chunks activos.")
