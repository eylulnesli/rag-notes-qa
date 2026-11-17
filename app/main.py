import time
from contextlib import asynccontextmanager
import anthropic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .config import MODEL, TOP_K
from .ingest import load_chunks
from .llm import PROMPTS, answer
from .retrieval import Retriever

state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    chunks = load_chunks()
    if not chunks:
        raise RuntimeError("No PDFs found in docs/. Put your course notes there.")
    state["retriever"] = Retriever(chunks)
    yield


app = FastAPI(title="Course Notes RAG API", version="1.0", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str = Field(min_length=3)
    variant: str = "grounded_cited"
    top_k: int = Field(TOP_K, ge=1, le=10)


@app.get("/health")
def health():
    r = state["retriever"]
    return {"status": "ok", "chunks": len(r.chunks), "backend": r.backend, "model": MODEL}


@app.get("/variants")
def variants():
    return PROMPTS


@app.post("/ask")
def ask(req: AskRequest):
    if req.variant not in PROMPTS:
        raise HTTPException(422, f"Unknown variant. Options: {list(PROMPTS)}")
    passages = state["retriever"].search(req.question, req.top_k)
    t0 = time.time()
    try:
        text = answer(req.question, passages, req.variant)
    except RuntimeError as e:  # missing API key
        raise HTTPException(503, str(e))
    except anthropic.APIError as e:
        raise HTTPException(502, f"Model API error: {e}")
    return {
        "answer": text, "variant": req.variant, "model": MODEL,
        "latency_ms": int((time.time() - t0) * 1000),
        "sources": [{"file": p["source"], "page": p["page"], "score": p["score"], "snippet": p["text"][:200]} for p in passages],
    }
