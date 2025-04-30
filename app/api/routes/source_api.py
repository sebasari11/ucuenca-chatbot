from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.source_schema import (
    SourceCreate,
    SourceResponse,
    SourceUpdate,
    SourceUpdateResponse,
)
from app.services.source_service import SourceService

router = APIRouter(prefix="/sources", tags=["Sources"])


def get_source_service(session: AsyncSession = Depends(get_session)) -> SourceService:
    return SourceService(session)


@router.post("/", response_model=SourceResponse)
async def create_source(
    source: SourceCreate, service: SourceService = Depends(get_source_service)
):
    return await service.create_source(source)


@router.get("/", response_model=list[SourceResponse])
async def list_sources(service: SourceService = Depends(get_source_service)):
    return await service.get_all_sources()


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source_by_id(
    source_id: int, service: SourceService = Depends(get_source_service)
):
    return await service.get_by_id(source_id)


@router.put("/{source_id}", response_model=SourceUpdateResponse)
async def update_source(
    source_id: int,
    source_update: SourceUpdate,
    service: SourceService = Depends(get_source_service),
):
    updated_source = await service.update_source(source_id, source_update)
    return {"message": "Fuente actualizada correctamente", "source": updated_source}


@router.delete("/{source_id}", response_model=dict)
async def delete_source(
    source_id: int, service: SourceService = Depends(get_source_service)
):
    return await service.delete_source(source_id)
