"""
api.py — FastAPI REST server for the College Admission Chatbot.
Run with: uvicorn backend.api:app --reload
Docs at:  http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys, os

# Allow importing from project root
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.rag_pipeline import answer_query, retrieve

app = FastAPI(
    title="College Admission Chatbot API",
    description="RAG-powered chatbot for college admission queries.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class ChunkResult(BaseModel):
    text:   str
    source: str
    score:  float


class QueryResponse(BaseModel):
    answer:   str
    sources:  list[str]
    chunks:   list[ChunkResult]
    mode:     str


# ── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "College Admission Chatbot API is running. Visit /docs for Swagger UI."}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        result = answer_query(req.question)
        return QueryResponse(
            answer  = result["answer"],
            sources = result["sources"],
            chunks  = [ChunkResult(**c) for c in result["chunks"]],
            mode    = result["mode"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/retrieve")
def retrieve_endpoint(q: str, top_k: int = 5):
    """Return raw retrieved chunks for a query (useful for debugging)."""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        chunks = retrieve(q, top_k=top_k)
        return {"query": q, "chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
