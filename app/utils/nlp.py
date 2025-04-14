from typing import List
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def chunk_text(text: str, max_length: int = 500) -> List[str]:
    # Simple split by sentence or fixed chunk size
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def generate_embeddings(chunks: List[str]) -> List[List[float]]:
    return model.encode(chunks).tolist()
