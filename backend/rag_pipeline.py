"""
rag_pipeline.py — Core Retrieval-Augmented Generation pipeline

Handles:
  1. Retrieving top-K relevant chunks from ChromaDB
  2. Constructing a context-aware prompt
  3. Generating a response (via OpenAI or built-in fallback mode)
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "college_admissions"
TOP_K = 4                        # number of chunks to retrieve
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# ── Vector Store Client ───────────────────────────────────────────────────────
def get_collection():
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )


# ── Retrieval ─────────────────────────────────────────────────────────────────
def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """Return top-K relevant chunks for a user query."""
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "category": meta.get("category", ""),
            "relevance": round(1 - dist, 3)   # cosine similarity score
        })
    return chunks


# ── Prompt Builder ────────────────────────────────────────────────────────────
def build_prompt(query: str, chunks: list[dict]) -> str:
    context = "\n\n---\n\n".join(
        f"[Source: {c['source']} | Relevance: {c['relevance']}]\n{c['text']}"
        for c in chunks
    )
    return f"""You are an expert college admission counselor. Answer the student's question
using ONLY the information provided in the context below. If the answer is not
in the context, say "I don't have that information — please contact the admissions
office directly."

Be concise, friendly, and accurate. Include specific numbers, dates, or fees when available.

CONTEXT:
{context}

STUDENT QUESTION: {query}

ANSWER:"""


# ── LLM Response (OpenAI) ─────────────────────────────────────────────────────
def generate_openai(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()


# ── Fallback Mode (No API Key) ────────────────────────────────────────────────
def generate_fallback(query: str, chunks: list[dict]) -> str:
    """
    Smart fallback: extracts the most relevant sentences from retrieved chunks
    without needing any external LLM API. Good for demos.
    """
    if not chunks:
        return "I couldn't find relevant information for your query. Please contact the admissions office."

    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower)) - {
        "what", "is", "the", "are", "how", "much", "when", "where",
        "can", "i", "do", "for", "a", "an", "of", "in", "to", "and"
    }

    # Score each sentence from the top chunks
    scored_sentences = []
    for chunk in chunks[:2]:
        sentences = re.split(r'(?<=[.:\n])\s+', chunk["text"])
        for sent in sentences:
            sent = sent.strip()
            if len(sent) < 20:
                continue
            sent_words = set(re.findall(r'\w+', sent.lower()))
            overlap = len(query_words & sent_words)
            if overlap > 0:
                scored_sentences.append((overlap, sent))

    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    top_sentences = [s for _, s in scored_sentences[:4]]

    if top_sentences:
        answer = " ".join(top_sentences)
        source = chunks[0]["source"].replace(".txt", "").replace("_", " ").title()
        return f"{answer}\n\n📎 Source: {source}"
    else:
        # Just return the most relevant chunk
        best = chunks[0]["text"][:500]
        return f"Here's what I found:\n\n{best}\n\n📎 Source: {chunks[0]['source']}"


# ── Main RAG Entry Point ──────────────────────────────────────────────────────
def answer(query: str) -> dict:
    """
    Full RAG pipeline: retrieve → build prompt → generate answer.
    Returns a dict with answer text + source chunks.
    """
    chunks = retrieve(query)

    if OPENAI_API_KEY:
        try:
            prompt = build_prompt(query, chunks)
            response_text = generate_openai(prompt)
            mode = "openai"
        except Exception as e:
            response_text = generate_fallback(query, chunks)
            mode = f"fallback (openai error: {e})"
    else:
        response_text = generate_fallback(query, chunks)
        mode = "fallback"

    return {
        "answer": response_text,
        "sources": [{"source": c["source"], "relevance": c["relevance"]} for c in chunks],
        "mode": mode,
        "chunks_retrieved": len(chunks)
    }


# ── Quick CLI test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_queries = [
        "What is the last date to apply?",
        "How much is the hostel fee for B.Tech?",
        "What are the eligibility criteria for MBA?",
        "What documents do I need for admission?"
    ]
    for q in test_queries:
        print(f"\n🎓 Q: {q}")
        result = answer(q)
        print(f"💬 A: {result['answer']}")
        print(f"📚 Mode: {result['mode']}")
