from pydantic import BaseModel, Field
from typing import List, Optional


class FaissIndexDeleteResponse(BaseModel):
    """Respuesta del endpoint DELETE para eliminar el índice FAISS"""
    message: str
    deleted_files: List[str]
    new_index_dimension: int


class FaissIndexCreateRequest(BaseModel):
    """Request para crear o resetear el índice FAISS"""
    dimension: Optional[int] = Field(
        default=384,
        ge=1,
        le=4096,
        description="Dimensión de los vectores del índice (default: 384)"
    )


class FaissIndexResetResponse(BaseModel):
    """Respuesta del endpoint POST para crear/resetear el índice FAISS"""
    message: str
    index_dimension: int
    index_created: bool

