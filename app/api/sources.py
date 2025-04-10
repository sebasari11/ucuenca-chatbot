from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.source import Source, SourceType
from app.schemas.source import PDFSourceCreate, PostgresSourceCreate, SourceResponse

source_router = APIRouter(prefix="/sources", tags=["Sources"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@source_router.get("/", response_model=list[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).all()


@source_router.post("/", response_model=SourceResponse)
def create_source(
    source: PDFSourceCreate | PostgresSourceCreate, db: Session = Depends(get_db)
):
    if source["type"] == "pdf":
        new_source = Source(
            name=source["name"], type=SourceType.pdf, filepath=source["filepath"]
        )
    elif source["type"] == "postgres":
        new_source = Source(
            name=source["name"],
            type=SourceType.postgres,
            host=source["host"],
            port=source["port"],
            user=source["user"],
            password=source["password"],
            database=source["database"],
        )
    else:
        raise HTTPException(status_code=400, detail="Tipo de fuente no soportado")

    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source


@source_router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")
    db.delete(source)
    db.commit()
    return {"detail": "Fuente eliminada"}
