from app.faiss_index.manager import FaissManager
from app.utils.nlp import get_embedding
from app.models.resource_chunk import ResourceChunk
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.schemas.search import SearchRequest, SearchResponse, SearchResult


def perform_search(request: SearchRequest) -> SearchResponse:
    embedding: list[float] = get_embedding(
        request.query,
        backend=request.backend,
    )
    faiss = FaissManager()
    chunk_ids, similarities = faiss.search(embedding, k=request.top_k)

    db: Session = SessionLocal()
    results = []

    for chunk_id, sim in zip(chunk_ids, similarities):
        chunk = db.query(ResourceChunk).filter_by(id=chunk_id).first()
        if chunk:
            results.append(
                SearchResult(
                    chunk_id=chunk.id, content=chunk.chunk_text, similarity=float(sim)
                )
            )

    return SearchResponse(results=results)


# def perform_smart_search(request: SearchRequest) -> SearchSmartResponse:
#     embedding: list[float] = get_embedding(request.query)
#     faiss = FaissManager()
#     chunk_ids, similarities = faiss.search(embedding, k=request.top_k)
#     print(chunk_ids)

#     db: Session = SessionLocal()
#     chuncks_related = []

#     for chunk_id in chunk_ids:
#         chunk = db.query(ResourceChunk).filter_by(id=chunk_id).first()
#         chuncks_related.append(chunk.chunk_text)
#     context: str = "\n\n".join(chuncks_related)
#     # result = get_smart_embedding(context, request.query)
#     answer = generate_contextual_answer_with_gemma(context, request.query)
#     print("answer gemma!", answer)
#     return SearchSmartResponse(answer=answer)
