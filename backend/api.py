"""
api.py — FastAPI REST backend for the College Admission Chatbot

Run:  uvicorn backend.api:app --reload
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.rag_pipeline import answer, retrieve

app = FastAPI(
    title="College Admission Chatbot API",
    description="RAG-powered chatbot for college admission queries",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ── Models ────────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    top_k: int = 4


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    mode: str
    timestamp: str


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "College Admission Chatbot API is running 🎓",
        "endpoints": ["/ask", "/retrieve", "/health", "/docs"]
    }


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/ask", response_model=QueryResponse)
def ask_question(req: QueryRequest):
    """Main endpoint: ask any admission-related question."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = answer(req.question)
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            mode=result["mode"],
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@app.post("/retrieve")
def retrieve_chunks(req: QueryRequest):
    """Debug endpoint: see raw retrieved chunks before LLM generation."""
    try:
        chunks = retrieve(req.question, top_k=req.top_k)
        return {"query": req.question, "chunks": chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
