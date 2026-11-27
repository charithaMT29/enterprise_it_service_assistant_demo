from pathlib import Path
import re
from .ollama_client import embed

GUIDE_FILE = Path(__file__).resolve().parent.parent / "data" / "it_operations_guide.md"

def load_guide_chunks():
    """Load the IT operations guide and split it by section headings."""

    text = GUIDE_FILE.read_text(encoding="utf-8")
    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

    chunks = []

    for section in sections:
        section = section.strip()

        if section.startswith("## "):
            title = section.splitlines()[0].replace("## ", "").strip()

            chunks.append({
                "title": title,
                "text": section,
            })

    return chunks

def cosine_similarity(a, b):
    """Calculate cosine similarity between two embedding vectors."""

    dot = sum(x * y for x, y in zip(a, b))

    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5

    if not norm_a or not norm_b:
        return 0.0

    return dot / (norm_a * norm_b)

def retrieve_knowledge(question, top_k=3):
    """Embed the question, rank guide sections and return relevant results."""

    chunks = load_guide_chunks()
    query_vector = embed(question)

    scored = []

    for chunk in chunks:
        vector = embed(chunk["text"])
        score = cosine_similarity(query_vector, vector)

        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)

    selected = [
        {
            "score": round(score, 4),
            "title": chunk["title"],
            "text": chunk["text"],
        }
        for score, chunk in scored[:top_k]
        if score > 0.15
    ]

    return selected