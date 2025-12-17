from typing import List, Literal
import httpx
from sentence_transformers import SentenceTransformer
import nltk
import requests
import numpy as np
from openai import OpenAI
from google import genai
from google.genai import types
from sklearn.decomposition import PCA
from app.core.config import settings

# Descargar recursos de NLTK una sola vez
nltk.download("punkt")
nltk.data.path.append("/app/nltk_data")
from nltk.tokenize import sent_tokenize


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
        print(f"Dimensión del embedding: {embedding.shape}")
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


def build_contextual_prompt3(context: str, question: str) -> str:
    return f"""Responde a la siguiente pregunta utilizando **exclusivamente** la información proporcionada en el contexto. 
Si el contexto no contiene datos suficientes para responder con claridad, limita tu respuesta **únicamente** a este mensaje, sin agregar nada más:
"Lo siento 😕, no tengo suficiente información para responder a eso por el momento. ¿Puedo ayudarte con algo más? 😊"

Contexto:
{context}

Pregunta:
{question}

Respuesta:"""


def build_contextual_prompt(context: str, question: str) -> str:
    return f"""
Por favor, utiliza el "Contexto" proporcionado como tu **fuente principal de información** para responder a la siguiente pregunta. Si el contexto no es suficiente para ofrecer una respuesta completa o clara, puedes **complementar la información con tu conocimiento general** para formular una respuesta útil y segura.

Si el contexto es **totalmente insuficiente** o la pregunta está fuera de tu alcance como asistente de salud mental, responde **únicamente** con el siguiente mensaje:

"Lo siento 😕, no tengo suficiente información para responder a eso por el momento. Mi objetivo es darte respuestas precisas y seguras. ¿Hay algo más en lo que pueda ayudarte hoy? 😊"

---

Contexto:
{context}

---

Pregunta:
{question}

---

Respuesta:"""


def build_chat_session_name_prompt(context: str) -> str:
    return f"""Crea un nombre para una sesión de chat que resuma el contexto proporcionado. El nombre debe ser breve, descriptivo y captar la esencia del contenido. No incluyas ningún otro texto o explicación, solo el nombre.

Contexto:
{context}
"""


async def answer_with_gemini(prompt: str, chat_history: List[dict]) -> str:
    
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    current_user_message_content = {
        "role": "user",
        "parts": [{"text": prompt}]
    }
    contents = chat_history + [current_user_message_content]
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="Eres un asistente de salud mental virtual llamado UCALMA. Tu objetivo es brindar apoyo y respuestas útiles, priorizando la precisión y el bienestar del usuario."
        ),
        contents=contents,
    )
    return response.text


async def answer_with_ollama(model: str, prompt: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": f"Eres un asistente de salud mental virtual llamado UCALMA. Tu objetivo es brindar apoyo y respuestas útiles, priorizando la precisión y el bienestar del usuario. \n {prompt}",
                    "stream": False,
                },
            )
            response.raise_for_status()
            json_response = response.json()
            return json_response.get("response", "").strip()
    except httpx.HTTPError as e:
        raise RuntimeError(f"Error al comunicarse con Ollama ({model}): {e}")
