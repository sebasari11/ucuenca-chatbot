import os
from app.database import SessionLocal
from app.models.source import Source
from app.models.resource_chunk import ResourceChunk
from app.utils.pdf_reader import extract_text_from_pdf
from app.utils.nlp import chunk_text, generate_embeddings


def process_resource(resource_id: int):
    db = SessionLocal()
    resource = db.query(Source).filter(Source.id == resource_id).first()

    if not resource:
        raise FileNotFoundError("Recurso no encontrado en la base de datos")

    relative_path = os.path.join(
        resource.filepath.strip("\\/"), f"{resource.name}.{resource.type.value}"
    )
    absolute_path = os.path.abspath(relative_path)

    if not os.path.exists(absolute_path):
        raise FileNotFoundError(f"Archivo no encontrado en la ruta: {absolute_path}")

    text = extract_text_from_pdf(absolute_path)
    chunks = chunk_text(text)
    embeddings = generate_embeddings(chunks)

    # TODO: Guardar en FAISS u otro motor de búsqueda (por ahora, solo imprimir)
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        db_chunk = ResourceChunk(
            resource_id=resource.id, chunk_text=chunk, embedding=embedding, order=i
        )
        db.add(db_chunk)

    db.commit()
    db.close()
    print(
        f"[INFO] {len(chunks)} chunks procesados y almacenados para recurso {resource_id}"
    )
