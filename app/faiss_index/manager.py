import faiss
import numpy as np
import os
import pickle
from app.core.logging import get_logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INDEX_PATH = os.path.join(BASE_DIR, "resource.index")
ID_MAP_PATH = os.path.join(BASE_DIR, "id_map.pkl")

logger = get_logger(__name__)


class FaissManager:
    def __init__(self):
        self.id_map = {}
        self.index = None
        self.load()

    def generate_index(self, dim):
        logger.info("Creando nuevo índice FAISS")
        self.index = faiss.IndexFlatL2(dim)

    def add_embeddings(self, embeddings: list[list[float]], chunk_ids: list[int]):
        vectors = np.array(embeddings).astype("float32")
        if vectors.ndim != 2:
            raise ValueError(
                f"Los vectores deben tener forma (n, d). Recibido: {vectors.shape}"
            )

        if self.index is None:
            self.generate_index(vectors.shape[1])
        else:
            if vectors.shape[1] != self.index.d:
                raise ValueError(
                    f"Dimensión del índice FAISS ({self.index.d}) no coincide con la de los vectores ({vectors.shape[1]})"
                )
        self.index.add(vectors)

        for i, chunk_id in enumerate(chunk_ids):
            self.id_map[self.index.ntotal - len(chunk_ids) + i] = chunk_id
        self.save()

    def search(self, query_vector: list[float], k: int = 5):
        vector = np.array([query_vector]).astype("float32")
        distances, indices = self.index.search(vector, k)

        matched_ids = [self.id_map.get(i) for i in indices[0] if i in self.id_map]
        return matched_ids, distances[0]

    def save(self):
        os.makedirs(os.path.dirname(ID_MAP_PATH), exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)
        with open(ID_MAP_PATH, "wb") as f:
            pickle.dump(self.id_map, f)

    def load(self):
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            logger.info("Índice FAISS cargado desde el disco")
        if os.path.exists(ID_MAP_PATH):
            with open(ID_MAP_PATH, "rb") as f:
                self.id_map = pickle.load(f)
                logger.info("Mapa de IDs cargado desde el disco")
