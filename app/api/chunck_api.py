
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from deps import get_db
from app.schemas.chunck_schema import ChunkCreate, ChunkResponse
from typing import List


router = APIRouter(prefix="/chunks", tags=["Chunks"])

@router.get("/", response_model=List[ChunkResponse])
def get_all_chunks(db: Session = Depends(get_db)):
    

@router.post("/", response_model=ChunkResponse)
def create_chunk(chunk: ChunkCreate, db: Session = Depends(get_db)):
    db_chunk = ResourceChunk(**chunk.dict())
    db.add(db_chunk)
    db.commit()
    db.refresh(db_chunk)
    return db_chunk

@router.get("/by_resource/{resource_id}", response_model=List[ChunkResponse])
def get_chunks_by_resource(resource_id: int, db: Session = Depends(get_db)):
    chunks = db.query(ResourceChunk).filter(ResourceChunk.resource_id == resource_id).all()
    return chunks

@router.delete("/{chunk_id}")
def delete_chunk(chunk_id: int, db: Session = Depends(get_db)):
    chunk = db.query(ResourceChunk).filter(ResourceChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="ResourceChunk not found")
    db.delete(chunk)
    db.commit()
    return {"message": "ResourceChunk deleted successfully"}

@router.delete("/by_resource/{resource_id}")
def delete_chunks_by_resource(resource_id: int, db: Session = Depends(get_db)):
    chunks = db.query(ResourceChunk).filter(ResourceChunk.resource_id == resource_id).all()
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found for this resource_id")
    for chunk in chunks:
        db.delete(chunk)
    db.commit()
    return {"message": f"Deleted {len(chunks)} chunks for resource_id {resource_id}"}
