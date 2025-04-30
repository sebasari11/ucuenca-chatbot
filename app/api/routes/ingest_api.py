from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ingest_service import IngestService
from app.schemas.ingest_schema import IngestResponse
from app.core.database import get_session


router = APIRouter(prefix="/ingest", tags=["Ingesta"])


def get_ingest_service(session: AsyncSession = Depends(get_session)) -> IngestService:
    return IngestService(session)


@router.post("/{resource_id}", response_model=IngestResponse)
async def ingest_resource(
    resource_id: int, service: IngestService = Depends(get_ingest_service)
):
    try:
        chunks = await service.process_resource(resource_id)
        return IngestResponse(
            message="Ingesta y procesamiento exitoso",
            resource_id=resource_id,
            chunks=chunks,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"exepcion => {str(e)}")
