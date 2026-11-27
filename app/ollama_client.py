import requests
from functools import lru_cache

from .config import OLLAMA_BASE_URL, CHAT_MODEL, EMBED_MODEL

class OllamaError(RuntimeError):
    pass

def chat(messages, tools=None):
    payload = {
        "model": CHAT_MODEL,
        "messages": messages,
        "stream": False
    }

    if tools:
        payload["tools"] = tools

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        data = response.json()

        if "message" not in data:
            raise OllamaError(
                "Ollama response did not contain a message."
            )

        return data["message"]

    except requests.RequestException as exc:
        raise OllamaError(
            "Could not contact Ollama. Check that Ollama is running "
            "and the model is downloaded."
        ) from exc


@lru_cache(maxsize=128)
def embed(text):
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={
                "model": EMBED_MODEL,
                "input": text
            },
            timeout=90
        )

        response.raise_for_status()
        data = response.json()

        embeddings = data.get("embeddings", [])

        if not embeddings:
            raise OllamaError(
                "Embedding model returned no vector."
            )

        return embeddings[0]

    except requests.RequestException as exc:
        raise OllamaError(
            "Could not create embeddings. Check that the embedding "
            "model is downloaded."
        ) from exc
