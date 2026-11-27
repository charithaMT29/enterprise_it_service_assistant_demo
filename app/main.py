
from typing import Literal
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .agent import run_agent


app = FastAPI(
    title="Northstar IT Service & Asset Operations Assistant",
    version="1.0.0",
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


# Validates individual conversation messages.
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1200)


# Validates incoming chat requests.
class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1200)

    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=8
    )


# Health check endpoint.
@app.get("/health")
def health():
    return {
        "status": "ok",
        "application": "Northstar IT Service & Asset Operations Assistant",
    }


# Main chat endpoint.
@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    try:
        # Convert validated messages into dictionaries.
        history = [
            item.dict()
            for item in request.history
        ]

        return run_agent(request.message, history)

    except Exception:
        raise HTTPException(
            status_code=502,
            detail=(
                "The assistant encountered an error. "
                "Please check that Ollama is running."
            ),
        )


# Serves the frontend.
@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


# Serves CSS, JavaScript and other static files.
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)
