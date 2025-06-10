from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.api.deps import get_current_user
from app.src.resources.models import Resource
from app.src.users.models import User
from app.src.resources.schemas import (
    ResourceCreate,
    ResourceResponse,
    ResourceResponseBase,
    ResourceUpdate,
    ResourceUpdateResponse,
    ResourceProcessResponse,
)
from app.src.resources.service import ResourceService
from uuid import UUID

router = APIRouter(prefix="/resources", tags=["Resources"])


def get_resource_service(
    session: AsyncSession = Depends(get_session),
) -> ResourceService:
    return ResourceService(session)


@router.post("/", response_model=ResourceResponseBase)
async def create_resource(
    resource: ResourceCreate,
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_resource(resource)


@router.post("/process/{resource_id}", response_model=ResourceProcessResponse)
async def process_resource(
    resource_id: UUID,
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_user),
):
    try:
        chunks = await service.process_resource(resource_id, current_user.id)
        return ResourceProcessResponse(
            message="Ingesta y procesamiento exitoso",
            resource_id=resource_id,
            chunks=chunks,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"exepcion => {str(e)}")


@router.get("/", response_model=list[ResourceResponseBase])
async def list_resources(
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_all_resources()


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource_by_id(
    resource_id: UUID,
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_by_external_id(resource_id)


@router.put("/{resource_id}", response_model=ResourceUpdateResponse)
async def update_resource(
    resource_id: UUID,
    resource_update: ResourceUpdate,
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_user),
):
    updated_resource: Resource = await service.update_resource(
        resource_id, resource_update, current_user.id
    )
    return {"message": "Fuente actualizada correctamente", "resource": updated_resource}


@router.delete("/{source_id}", response_model=dict)
async def delete_resource(
    resource_id: UUID,
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_user),
):
    return await service.delete_resource(resource_id)
