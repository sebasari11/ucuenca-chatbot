from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.api.deps import get_current_user
from app.models.source import Source
from app.models.user import User
from app.schemas.source_schema import (
    SourceCreate,
    SourceResponse,
    SourceUpdate,
    SourceUpdateResponse,
    SourceProcessResponse,
)
from app.services.source_service import SourceService

router = APIRouter(prefix="/sources", tags=["Sources"])


def get_source_service(session: AsyncSession = Depends(get_session)) -> SourceService:
    return SourceService(session)


@router.post("/", response_model=SourceResponse)
async def create_source(
    source: SourceCreate,
    service: SourceService = Depends(get_source_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_source(source)


@router.post("/process_resource/{resource_id}", response_model=SourceProcessResponse)
async def ingest_resource(
    resource_id: int,
    service: SourceService = Depends(get_source_service),
    current_user: User = Depends(get_current_user),
):
    try:
        chunks = await service.process_resource(resource_id, current_user.id)
        return SourceProcessResponse(
            message="Ingesta y procesamiento exitoso",
            resource_id=resource_id,
            chunks=chunks,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"exepcion => {str(e)}")


@router.get("/", response_model=list[SourceResponse])
async def list_sources(
    service: SourceService = Depends(get_source_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_all_sources()


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source_by_id(
    source_id: int,
    service: SourceService = Depends(get_source_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_by_id(source_id)


@router.put("/{source_id}", response_model=SourceUpdateResponse)
async def update_source(
    source_id: int,
    source_update: SourceUpdate,
    service: SourceService = Depends(get_source_service),
    current_user: User = Depends(get_current_user),
):
    updated_source: Source = await service.update_source(
        source_id, source_update, current_user.id
    )
    return {"message": "Fuente actualizada correctamente", "source": updated_source}


@router.delete("/{source_id}", response_model=dict)
async def delete_source(
    source_id: int,
    service: SourceService = Depends(get_source_service),
    current_user: User = Depends(get_current_user),
):
    return await service.delete_source(source_id)
