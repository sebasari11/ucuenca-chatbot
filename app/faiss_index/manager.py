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
    
    def reset_index(self, dim: int = 384):
        self.generate_index(dim)
        self.id_map = {}
        self.save()
    
    def delete_index(self, dim: int = 384):
        """
        Elimina los archivos físicos del índice FAISS y reinicia la instancia en memoria.
        
        Args:
            dim: Dimensión del nuevo índice vacío (default: 384)
        
        Returns:
            dict: Información sobre los archivos eliminados
        """
        deleted_files = []
        
        # Eliminar archivo del índice si existe
        if os.path.exists(INDEX_PATH):
            try:
                os.remove(INDEX_PATH)
                deleted_files.append(INDEX_PATH)
                logger.info(f"Archivo de índice eliminado: {INDEX_PATH}")
            except OSError as e:
                logger.error(f"Error al eliminar el archivo de índice: {str(e)}")
                raise
        
        # Eliminar archivo del mapa de IDs si existe
        if os.path.exists(ID_MAP_PATH):
            try:
                os.remove(ID_MAP_PATH)
                deleted_files.append(ID_MAP_PATH)
                logger.info(f"Archivo de mapa de IDs eliminado: {ID_MAP_PATH}")
            except OSError as e:
                logger.error(f"Error al eliminar el archivo de mapa de IDs: {str(e)}")
                raise
        
        # Reiniciar el índice en memoria
        self.reset_index(dim=dim)
        logger.info(f"Índice FAISS reiniciado en memoria con dimensión {dim}")
        
        return {
            "deleted_files": deleted_files,
            "message": "Índice FAISS eliminado y reiniciado correctamente",
            "new_index_dimension": dim
        }