from app.schemas.source_schema import SourceCreate, SourceUpdate
from app.models.source import Source, SourceType
from sqlalchemy.orm import Session
from fastapi import HTTPException


def create_pdf_source(source: SourceCreate):
    return Source(name=source.name, type=SourceType.pdf, filepath=source.filepath)


def create_postgres_source(source: SourceCreate):
    return Source(
        name=source.name,
        type=SourceType.postgres,
        host=source.host,
        port=source.port,
        user=source.user,
        password=source.password,
        database=source.database,
    )


def create_source(source: SourceCreate, db: Session):
    if source.type == "pdf":
        new_source: Source = create_pdf_source(source)
    elif source.type == "postgres":
        new_source: Source = create_postgres_source(source)
    else:
        raise HTTPException(status_code=400, detail="Tipo de fuente no soportado")

    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source


def update_source(source_id: int, update_data: SourceUpdate, db: Session):
    source = db.query(Source).filter(Source.id == source_id).first()
    print(f" Source => {source} \n!!!!!")

    if not source:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        print(f"{field} => {value}")
        setattr(source, field, value)

    db.commit()
    db.refresh(source)
    return source


def get_all_sources(db: Session):
    return db.query(Source).all()


def delete_source(source_id: int, db: Session):
    source = db.query(Source).get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")
    db.delete(source)
    db.commit()
    return {"detail": "Fuente eliminada"}
