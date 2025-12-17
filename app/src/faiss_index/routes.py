from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_admin_user
from app.src.users.models import User
from app.faiss_index.manager import FaissManager
from app.src.faiss_index.schemas import (
    FaissIndexDeleteResponse,
    FaissIndexCreateRequest,
    FaissIndexResetResponse,
)
from app.core.logging import get_logger

router = APIRouter(prefix="/faiss-index", tags=["FAISS Index"])

logger = get_logger(__name__)


def get_faiss_manager() -> FaissManager:
    """Dependency para obtener una instancia de FaissManager"""
    return FaissManager()


@router.delete(
    "/",
    response_model=FaissIndexDeleteResponse,
    summary="Eliminar índice FAISS",
    description="Elimina los archivos físicos del índice FAISS y reinicia la instancia en memoria. Requiere permisos de administrador."
)
async def delete_faiss_index(
    current_user: User = Depends(get_current_admin_user),
    faiss_manager: FaissManager = Depends(get_faiss_manager),
):
    """
    Endpoint DELETE para eliminar de forma segura el índice FAISS.
    
    Este endpoint:
    - Elimina los archivos físicos del índice (resource.index e id_map.pkl)
    - Reinicia la instancia en memoria del índice con un índice vacío
    - Requiere autenticación y permisos de administrador
    
    Args:
        current_user: Usuario autenticado (debe ser admin)
        faiss_manager: Instancia del manager de FAISS
    
    Returns:
        FaissIndexDeleteResponse: Información sobre la operación realizada
    
    Raises:
        HTTPException: Si ocurre un error durante la eliminación
    """
    try:
        logger.info(f"Usuario {current_user.username} solicitó eliminar el índice FAISS")
        
        result = faiss_manager.delete_index(dim=384)
        
        logger.info(f"Índice FAISS eliminado exitosamente por {current_user.username}")
        
        return FaissIndexDeleteResponse(
            message=result["message"],
            deleted_files=result["deleted_files"],
            new_index_dimension=result["new_index_dimension"]
        )
    
    except OSError as e:
        logger.error(f"Error al eliminar archivos del índice FAISS: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar los archivos del índice: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error inesperado al eliminar el índice FAISS: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al eliminar el índice: {str(e)}"
        )


@router.post(
    "/reset",
    response_model=FaissIndexResetResponse,
    summary="Resetear índice FAISS",
    description="Resetea el índice FAISS existente, eliminando todos los vectores y creando un nuevo índice vacío. Requiere permisos de administrador."
)
async def reset_faiss_index(
    request: FaissIndexCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    faiss_manager: FaissManager = Depends(get_faiss_manager),
):
    """
    Endpoint POST para resetear el índice FAISS.
    
    Este endpoint:
    - Resetea el índice FAISS existente, eliminando todos los vectores almacenados
    - Crea un nuevo índice vacío con la dimensión especificada
    - Guarda el índice vacío en disco
    - Requiere autenticación y permisos de administrador
    
    Args:
        request: Request body con la dimensión del índice (opcional, default: 384)
        current_user: Usuario autenticado (debe ser admin)
        faiss_manager: Instancia del manager de FAISS
    
    Returns:
        FaissIndexResetResponse: Información sobre la operación realizada
    
    Raises:
        HTTPException: Si ocurre un error durante el reseteo
    """
    try:
        logger.info(
            f"Usuario {current_user.username} solicitó resetear el índice FAISS "
            f"con dimensión {request.dimension}"
        )
        
        faiss_manager.reset_index(dim=request.dimension)
        
        logger.info(
            f"Índice FAISS reseteado exitosamente por {current_user.username} "
            f"con dimensión {request.dimension}"
        )
        
        return FaissIndexResetResponse(
            message="Índice FAISS reseteado correctamente",
            index_dimension=request.dimension,
            index_created=True
        )
    
    except Exception as e:
        logger.error(f"Error inesperado al resetear el índice FAISS: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al resetear el índice: {str(e)}"
        )


@router.post(
    "/create",
    response_model=FaissIndexResetResponse,
    summary="Crear índice FAISS",
    description="Crea un nuevo índice FAISS vacío. Si ya existe un índice, lo sobrescribe. Requiere permisos de administrador."
)
async def create_faiss_index(
    request: FaissIndexCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    faiss_manager: FaissManager = Depends(get_faiss_manager),
):
    """
    Endpoint POST para crear un nuevo índice FAISS.
    
    Este endpoint:
    - Crea un nuevo índice FAISS vacío con la dimensión especificada
    - Si ya existe un índice, lo sobrescribe con uno nuevo vacío
    - Guarda el índice en disco
    - Requiere autenticación y permisos de administrador
    
    Args:
        request: Request body con la dimensión del índice (opcional, default: 384)
        current_user: Usuario autenticado (debe ser admin)
        faiss_manager: Instancia del manager de FAISS
    
    Returns:
        FaissIndexResetResponse: Información sobre la operación realizada
    
    Raises:
        HTTPException: Si ocurre un error durante la creación
    """
    try:
        logger.info(
            f"Usuario {current_user.username} solicitó crear un nuevo índice FAISS "
            f"con dimensión {request.dimension}"
        )
        
        faiss_manager.reset_index(dim=request.dimension)
        
        logger.info(
            f"Índice FAISS creado exitosamente por {current_user.username} "
            f"con dimensión {request.dimension}"
        )
        
        return FaissIndexResetResponse(
            message="Índice FAISS creado correctamente",
            index_dimension=request.dimension,
            index_created=True
        )
    
    except Exception as e:
        logger.error(f"Error inesperado al crear el índice FAISS: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al crear el índice: {str(e)}"
        )

