from fastapi import APIRouter, HTTPException
from app.services.ingest_service import process_resource
from app.schemas.ingest import IngestResponse

router = APIRouter(prefix="/ingest", tags=["Ingesta"])


@router.post("/{resource_id}", response_model=IngestResponse)
def ingest_resource(resource_id: int):
    try:
        process_resource(resource_id)
        return IngestResponse(
            message="Ingesta y procesamiento exitoso", resource_id=resource_id
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"Archivo no encontrado => {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"exepcion => {str(e)}")
