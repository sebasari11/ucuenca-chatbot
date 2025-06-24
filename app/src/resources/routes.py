from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.api.deps import get_current_admin_user
from app.src.resources.models import Resource
from app.src.users.models import User
from app.src.resources.schemas import (
    ResourceCreate,
    ResourcePDFUrl,
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
    current_user: User = Depends(get_current_admin_user),
):
    return await service.create_resource(resource)


@router.post("/process/{resource_id}", response_model=ResourceProcessResponse)
async def process_resource(
    resource_id: UUID,
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_admin_user),
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

# @router.post("/process-url-pdf")
# async def process_url_pdf(
#     payload: ResourcePDFUrl,
#     current_user: User = Depends(get_current_admin_user)
# ):
#     try:
#         response = requests.get(payload.url)
#         response.raise_for_status()

#         if "application/pdf" not in response.headers.get("Content-Type", ""):
#             raise HTTPException(status_code=400, detail="La URL no apunta a un archivo PDF válido.")

#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#             tmp_file.write(response.content)
#             tmp_path = tmp_file.name

#         # Usa tu nueva función modular
#         chunks, embeddings = process_pdf_file(tmp_path)

#         # Opcional: almacenar en FAISS, aunque no se asocie a un recurso
#         chunk_ids = list(range(len(chunks)))  # IDs simulados si no hay persistencia
#         store_in_faiss(embeddings, chunk_ids)

#         return {
#             "message": "PDF desde URL procesado correctamente",
#             "num_chunks": len(chunks),
#             "preview": chunks[:3],  # para ver algunos chunks
#         }

#     except requests.RequestException as e:
#         raise HTTPException(status_code=400, detail=f"Error al descargar el PDF: {str(e)}")

@router.get("/", response_model=list[ResourceResponseBase])
async def list_resources(
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_admin_user),
):
    return await service.get_all_resources()


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource_by_id(
    resource_id: UUID,
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_admin_user),
):
    return await service.get_by_external_id(resource_id)


@router.put("/{resource_id}", response_model=ResourceUpdateResponse)
async def update_resource(
    resource_id: UUID,
    resource_update: ResourceUpdate,
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_admin_user),
):
    updated_resource: Resource = await service.update_resource(
        resource_id, resource_update, current_user.id
    )
    return {"message": "Fuente actualizada correctamente", "resource": updated_resource}


@router.delete("/{source_id}", response_model=dict)
async def delete_resource(
    resource_id: UUID,
    service: ResourceService = Depends(get_resource_service),
    current_user: User = Depends(get_current_admin_user),
):
    return await service.delete_resource(resource_id)
