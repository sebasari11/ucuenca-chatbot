from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger
from sqlalchemy import delete, select, update
from app.schemas.source_schema import SourceCreate, SourceUpdate
from app.models.source import Source, SourceType
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.exceptions import NotFoundException

logger = get_logger(__name__)


class SourceService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

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

    async def update_source(self, source_id: int, source_data: SourceUpdate):
        logger.debug(f"Actualizando el Recurso con id: {source_id}")
        update_data = source_data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("No hay campos para actualizar.")
        query = update(Source).where(Source.id == source_id).values(**update_data)
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
