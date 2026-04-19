"""
rag_pipeline.py — Core RAG pipeline using LangChain, FAISS, and Groq (LLaMA-3).
Supports ChatGroq API and a built-in keyword-fallback mode.
"""

import os
import re
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_index")
MODEL_NAME       = "all-MiniLM-L6-v2"
GROQ_MODEL       = "llama-3.3-70b-versatile"
TOP_K            = 5

# ── Singleton FAISS index ─────────────────────────────────────────────
_vectorstore = None

def _get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        if not os.path.exists(FAISS_INDEX_PATH):
            raise Exception(f"FAISS index not found at '{FAISS_INDEX_PATH}'. Run ingest.py first.")
        # allow_dangerous_deserialization=True is safe for locally generated indices
        _vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    return _vectorstore

# ── Retrieval ────────────────────────────────────────────────────────────────
def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """Return raw retrieved chunks for a query (useful for debugging)."""
    vs = _get_vectorstore()
    
    docs_and_scores = vs.similarity_search_with_score(query, k=top_k)
    chunks = []
    
    # FAISS returns L2 distances. For cosine similarity, it requires L2 normalization beforehand. 
    # To keep it simple, we just pass the distance as "score". 
    # Note: Smaller score implies higher similarity in L2. We will invert it for a mock "similarity" looking score.
    for d, dist in docs_and_scores:
        chunks.append({
            "text": d.page_content,
            "source": d.metadata.get("source", "unknown"),
            "score": round(1 / (1 + float(dist)), 4)
        })
    return chunks

# ── Generation: Keyword Fallback ─────────────────────────────────────────────
def _generate_fallback(query: str, context_chunks: list[dict]) -> str:
    """
    Smart keyword-matching fallback.
    Finds the most relevant chunk and extracts the most relevant sentences.
    """
    if not context_chunks:
        return (
            "I'm sorry, I couldn't find relevant information for your question. "
            "Please contact the admissions office directly."
        )

    best = context_chunks[0]
    text = best["text"]

    query_words = set(re.sub(r"[^a-z0-9 ]", "", query.lower()).split())
    sentences   = re.split(r"(?<=[.?!])\s+", text)

    def score_sentence(s):
        words = set(re.sub(r"[^a-z0-9 ]", "", s.lower()).split())
        return len(query_words & words)

    scored = sorted(sentences, key=score_sentence, reverse=True)
    top_sentences = [s.strip() for s in scored[:3] if s.strip()]
    answer        = " ".join(top_sentences)

    if not answer:
        answer = text[:400]

    return answer

# ── Public API ───────────────────────────────────────────────────────────────
def answer_query(query: str) -> dict:
    """
    Main entry point. Returns:
        {
          "answer":   str,
          "sources":  list[str],
          "chunks":   list[dict],
          "mode":     "groq" | "fallback"
        }
    """
    try:
        chunks = retrieve(query)
    except Exception as e:
        print(f"Error retrieving from FAISS: {e}")
        return {
            "answer": f"Retrieval error. Have you run ingestion? Error: {e}",
            "sources": [],
            "chunks": [],
            "mode": "error"
        }

    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
    mode = "groq" if groq_api_key and not groq_api_key.startswith("gsk_your") else "fallback"

    try:
        if mode == "groq":
            vs = _get_vectorstore()
            retriever = vs.as_retriever(search_kwargs={"k": TOP_K})
            llm = ChatGroq(temperature=0.2, model_name=GROQ_MODEL, groq_api_key=groq_api_key)

            system_prompt = (
                "You are a helpful college admissions assistant. "
                "Answer the student's question using ONLY the information provided in the context below. "
                "If the answer is not in the context, say 'I don't have information about that. "
                "Please contact the admissions office directly.' "
                "Be concise, clear, and friendly.\n\n"
                "Context:\n{context}"
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
            ])

            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

            response = rag_chain.invoke({"input": query})
            answer = response["answer"].strip()
        else:
            answer = _generate_fallback(query, chunks)
    except Exception as e:
        print(f"LLM Generation Error: {e}")
        answer = _generate_fallback(query, chunks)
        mode   = "fallback"

    sources = list({c["source"] for c in chunks})

    return {
        "answer":  answer,
        "sources": sources,
        "chunks":  chunks,
        "mode":    mode,
    }
