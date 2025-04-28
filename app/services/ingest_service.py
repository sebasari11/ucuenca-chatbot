import os
from app.core.database import SessionLocal
from app.models.source import Source
from app.models.resource_chunk import ResourceChunk
from app.schemas.source_schema import SourceUpdate
from app.utils.pdf_reader import extract_text_from_pdf
from app.utils.nlp import paragraph_chunker, sentence_chunker, generate_embeddings
from app.services.source_service import update_source
from app.faiss_index.manager import FaissManager

faiss_manager = FaissManager()


def process_resource(resource_id: int):
    db = SessionLocal()
    resource = db.query(Source).filter(Source.id == resource_id).first()

    if not resource:
        raise FileNotFoundError("Recurso no encontrado en la base de datos")

    if resource.processed:
        raise ValueError(f"El recurso {resource.name} ya fue procesado.")

    relative_path = os.path.join(
        resource.filepath.strip("\\/"), f"{resource.name}.{resource.type.value}"
    )
    absolute_path = os.path.abspath(relative_path)

    if not os.path.exists(absolute_path):
        raise FileNotFoundError(f"Archivo no encontrado en la ruta: {absolute_path}")

    text = extract_text_from_pdf(absolute_path)
    chunks = sentence_chunker(text, 10)
    embeddings = generate_embeddings(chunks)

    chunk_ids = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        db_chunk = ResourceChunk(
            resource_id=resource.id, chunk_text=chunk, embedding=embedding, order=i
        )
        db.add(db_chunk)
        db.flush()
        chunk_ids.append(db_chunk.id)

    faiss_manager.add_embeddings(embeddings, chunk_ids)
    source_update: SourceUpdate = SourceUpdate(processed=True)
    update_source(resource.id, source_update, db)
    db.commit()
    db.close()

    print(
        f"[INFO] {len(chunks)} chunks procesados y almacenados para recurso {resource_id}"
    )
