from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from deps import get_db
from app.schemas.source_schema import SourceCreate, SourceResponse, SourceUpdate
from app.services.source_service import (
    create_source,
    update_source,
    get_all_sources,
    delete_source,
)

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.post("/", response_model=SourceResponse)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    return create_source(source, db)


@router.get("/", response_model=list[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    return get_all_sources(db)


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: int, source_update: SourceUpdate, db: Session = Depends(get_db)
):
    updated_source = update_source(source_id, source_update, db)
    return {"message": "Fuente actualizada correctamente", "source": updated_source}


@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    return delete_source(source_id, db)
