from typing import List, Literal
from sentence_transformers import SentenceTransformer
import nltk
import requests
import numpy as np
from openai import OpenAI
from sklearn.decomposition import PCA
from app.core.config import settings

from nltk.tokenize import sent_tokenize

# Descargar recursos de NLTK una sola vez
nltk.download("punkt")

# Modelos
sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


# CHUNKERS
def chunk_text(text: str, max_length: int = 250) -> List[str]:
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def smart_chunk_text(text: str, max_length: int = 250) -> List[str]:
    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text.strip())
            break
        split_at = text.rfind(" ", 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at].strip())
        text = text[split_at:].lstrip()
    return chunks


def sentence_chunker(text: str, max_sentences: int = 5) -> List[str]:
    sentences = sent_tokenize(text)
    return [
        " ".join(sentences[i : i + max_sentences]).strip()
        for i in range(0, len(sentences), max_sentences)
    ]


def paragraph_chunker(text: str) -> List[str]:
    paragraphs = text.split("\n\n")
    chunks = []

    for paragraph in paragraphs:
        cleaned = paragraph.strip()
        if len(cleaned) > 100:
            sentences = sent_tokenize(cleaned)
            chunks.append(" ".join(sentences))
        elif cleaned:
            chunks.append(cleaned)

    return chunks


# EMBEDDINGS
def generate_embeddings(chunks: List[str]) -> List[List[float]]:
    return sentence_model.encode(chunks).tolist()


def reduce_embedding_dimension(
    embedding: list[float], target_dim: int = 384
) -> list[float]:
    # Asumiendo que el embedding tiene 768 dimensiones y lo quieres reducir a 384
    pca = PCA(n_components=target_dim)
    reduced_embedding = pca.fit_transform([embedding])  # Reduce la dimensión
    return reduced_embedding[0].tolist()


def get_embedding(
    question: str,
    backend: Literal["sentence", "ollama"] = "sentence",
    ollama_model: str = "nomic-embed-text",
    ollama_url: str = "http://localhost:11434/api/embeddings",
) -> List[float]:
    """
    Genera un embedding a partir de texto utilizando SentenceTransformer o Ollama.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("El texto debe ser una cadena no vacía.")

    if backend == "sentence":
        embedding = sentence_model.encode(question, convert_to_numpy=True)
        print(f"Dimensión del embedding: {embedding.shape}")  # Verifica la dimensión
        return embedding.tolist()

    if backend == "ollama":
        try:
            response = requests.post(
                ollama_url,
                json={"model": ollama_model, "prompt": question},
                timeout=10,
            )
            data = response.json()
            embedding = data.get("embedding")
            if isinstance(embedding, list):
                reduced_embedding = reduce_embedding_dimension(
                    embedding, target_dim=384
                )
                return [float(val) for val in reduced_embedding]
            else:
                raise ValueError("Embedding de Ollama no está en el formato adecuado.")
        except requests.RequestException as e:
            raise RuntimeError(f"Error al obtener embedding con Ollama: {e}")

    raise ValueError("Backend inválido. Usa 'sentence' o 'ollama'.")


# RESPUESTAS INTELIGENTES
def get_smart_embedding(context: str, query: str) -> str:
    prompt = f"""Contesta la siguiente pregunta usando únicamente el contexto proporcionado.

        Contexto:
        {context}

        Pregunta:
        {query}

        Respuesta:"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error en DeepSeek: {e}"


# PROMPTS
def build_contextual_prompt2(context: str, question: str) -> str:
    return f""" Considera el siguiente contexto para responder la pregunta formulada. Si la pregunta no puede ser respondida con la información del contexto, responde unicamente: 'Lo siento, no tengo suficiente información para responder a eso, Lo siento 😕, no tengo suficiente información para responder a eso.¿Puedo ayudarte con algo más? 😊'
    sin añadir nada adicional
Contexto:
{context}

Pregunta:
{question}

Respuesta:"""


def build_contextual_prompt(context: str, question: str) -> str:
    return f"""Responde a la siguiente pregunta utilizando **exclusivamente** la información proporcionada en el contexto. 
Si el contexto no contiene datos suficientes para responder con claridad, limita tu respuesta **únicamente** a este mensaje, sin agregar nada más:
"Lo siento 😕, no tengo suficiente información para responder a eso por el momento. ¿Puedo ayudarte con algo más? 😊"

Contexto:
{context}

Pregunta:
{question}

Respuesta:"""


def build_chat_session_name_prompt(context: str) -> str:
    return f"""Crea un nombre para una sesión de chat que resuma el contexto proporcionado. El nombre debe ser breve, descriptivo y captar la esencia del contenido. No incluyas ningún otro texto o explicación, solo el nombre.

Contexto:
{context}
"""
