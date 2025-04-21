from typing import List
from sentence_transformers import SentenceTransformer
import nltk
import requests
from app.core.config import settings
from openai import OpenAI

nltk.download("punkt_tab")
from nltk.tokenize import sent_tokenize

model = SentenceTransformer("all-MiniLM-L6-v2")

client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")


def chunk_text(text: str, max_length: int = 250) -> List[str]:
    # Simple split by sentence or fixed chunk size
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
    chunks = []

    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i : i + max_sentences])
        chunks.append(chunk.strip())

    return chunks


def paragraph_chunker(text: str) -> List[str]:
    paragraphs = text.split("\n\n")
    print(paragraphs)
    chunks = []
    for paragraph in paragraphs:
        print(len(paragraph))
        if len(paragraph) > 100:
            sentences = sent_tokenize(paragraph)
            chunks.append(" ".join(sentences))
        else:
            chunks.append(paragraph.strip())

    return chunks


def generate_embeddings(chunks: List[str]) -> List[List[float]]:
    return model.encode(chunks).tolist()


def get_embedding(text: str) -> list[float]:
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def get_smart_embedding(context: str, query: str) -> list[float]:

    prompt = f"""Contesta la siguiente pregunta usando únicamente el contexto proporcionado.

    Contexto:
    {context}

    Pregunta:
    {query}

    Respuesta:"""
    print(prompt)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=False,
    )
    print(response)
    print(response.choices[0].message.content)
    return print(response.choices[0].message.content)


def generate_contextual_answer_with_gemma(context: str, query: str) -> str:
    prompt = f"""Contesta la siguiente pregunta usando únicamente el contexto proporcionado.

        Contexto:
        {context}

        Pregunta:
        {query}

        Respuesta:
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma3:latest", "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        answer = result.get("response", "").strip()

        return answer

    except requests.exceptions.RequestException as e:
        print(f"Error al comunicarse con Ollama (gemma): {e}")
        return "Error al generar respuesta"
