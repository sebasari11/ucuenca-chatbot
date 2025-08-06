from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_session
from app.api.deps import get_current_user
from app.src.users.models import User
from app.src.chunks.schemas import ChunkBase, ChunkResponse
from app.src.chunks.service import ChunkService


router = APIRouter(prefix="/chunks", tags=["Chunks"])


def get_chunk_service(db: AsyncSession = Depends(get_session)) -> ChunkService:
    return ChunkService(db)


@router.post("/", response_model=ChunkResponse)
async def create_chunk(
    chunk: ChunkBase,
    service: ChunkService = Depends(get_chunk_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_chunk(chunk)


@router.get("/", response_model=List[ChunkResponse])
async def get_all_chunks(
    service: ChunkService = Depends(get_chunk_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_all_chunks()


@router.get("/by_resource/{resource_id}", response_model=List[ChunkResponse])
async def get_chunks_by_resource_id(
    resource_id: UUID,
    service: ChunkService = Depends(get_chunk_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_chunks_by_resource_id(resource_id)


@router.delete("/{chunk_id}")
async def delete_chunk(
    chunk_id: int,
    service: ChunkService = Depends(get_chunk_service),
    current_user: User = Depends(get_current_user),
):

    return await service.delete_chunk(chunk_id)


@router.delete("/by_resource/{resource_id}")
async def delete_chunks_by_resource(
    resource_id: UUID,
    service: ChunkService = Depends(get_chunk_service),
    current_user: User = Depends(get_current_user),
):

    return await service.delete_chunks_by_resource_id(resource_id)
