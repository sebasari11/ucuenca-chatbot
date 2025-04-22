from app.schemas.ask import AskRequest, AskResponse
from app.services.search_service import perform_search
from app.schemas.search import SearchRequest
import requests
from app.utils.nlp import build_contextual_prompt


def answer_question(request: AskRequest) -> AskResponse:
    search_response = perform_search(
        SearchRequest(query=request.query, top_k=request.top_k, backend="sentence")
    )
    context_chunks = [r.content for r in search_response.results]

    context = "\n".join(context_chunks)

    prompt: str = build_contextual_prompt(context, request.query)

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": request.model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
        return AskResponse(answer=answer, context_chunks=context_chunks)
    except requests.RequestException as e:
        return f"Error al comunicarse con Ollama ({request.model}): {e}"
