from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete, select
from app.core.logging import get_logger
from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.resource_chunk import ResourceChunk
from app.schemas.chunck_schema import ChunkCreate


logger = get_logger(__name__)


class ChunckService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

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

    async def get_chunks_by_resource(self, resource_id: int):
        query = select(ResourceChunk).where(ResourceChunk.resource_id == resource_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete_chunck(self, chunk_id: int):
        query = delete(ResourceChunk).where(ResourceChunk.id == chunk_id)
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundException(f"Chunk con id {chunk_id} no encontrado.")
        await self.session.commit()
        return {"detail": "Chunck eliminado"}

    async def delete_chunck_by_resource_id(self, resource_id: int):
        query = delete(ResourceChunk).where(ResourceChunk.resource_id == resource_id)
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundException(
                detail=f"No se encontrar chunks para el resource_id {resource_id} especificado.",
            )
        await self.session.commit()
        return {
            "message": f"Se eliminaron {result.rowcount} chunks para el siguiente resource_id {resource_id}."
        }
