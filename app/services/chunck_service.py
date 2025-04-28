from sqlalchemy.orm import Session
from app.models.resource_chunk import ResourceChunk 
from typing import List



def get_all_chunks(db: Session) => List[ResourceChunk]:
    chunks: List[ResourceChunk] = db.query(ResourceChunk).all()
    return chunks