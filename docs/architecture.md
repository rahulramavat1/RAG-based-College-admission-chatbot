# Architecture — College Admission Chatbot (RAG)

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│              Streamlit Chat UI / FastAPI REST                   │
└────────────────────────────┬────────────────────────────────────┘
                             │ user query
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG PIPELINE                               │
│                                                                 │
│  1. ENCODE QUERY                                                │
│     sentence-transformers/all-MiniLM-L6-v2                      │
│     Query text → 384-dim vector                                 │
│                        │                                        │
│                        ▼                                        │
│  2. VECTOR SEARCH                                               │
│     ChromaDB (cosine similarity, HNSW index)                    │
│     Returns top-K most relevant document chunks                 │
│                        │                                        │
│                        ▼                                        │
│  3. CONTEXT CONSTRUCTION                                        │
│     Combine retrieved chunks with source metadata               │
│     Build grounded prompt for LLM                               │
│                        │                                        │
│                        ▼                                        │
│  4. RESPONSE GENERATION                                         │
│     OpenAI GPT-3.5-turbo (if API key set)                       │
│     OR smart fallback extractor (no API key needed)             │
│                        │                                        │
│                        ▼                                        │
│     Answer + Source Citations                                   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    Response to User
```

---

## Data Flow — Document Ingestion (one-time setup)

```
PDF / TXT Files
     │
     ▼
Text Extraction (pdfplumber / plain text)
     │
     ▼
Chunking (500 char chunks, 100 char overlap)
     │
     ▼
Embedding (all-MiniLM-L6-v2 → 384-dim vectors)
     │
     ▼
ChromaDB (persistent local vector store)
```

---

## Component Details

### Embedding Model
- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Why:** Free, runs locally, no API key needed, 384 dimensions, fast
- **Upgrade path:** OpenAI `text-embedding-3-small` (1536 dims, higher quality)

### Vector Database
- **Dev:** ChromaDB (local, persistent, Python-native)
- **Prod upgrade:** Pinecone or Weaviate for cloud scale

### LLM
- **Primary:** OpenAI GPT-3.5-turbo (`OPENAI_API_KEY` required)
- **Fallback:** Built-in keyword extractor (zero cost, works offline)
- **Upgrade path:** GPT-4, Claude, or Llama 2 (local)

### Chunking Strategy
- Chunk size: ~400 characters (~100 tokens)
- Overlap: 80 characters — ensures context isn't lost at boundaries
- Metadata stored: source file, category, chunk index

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health + info |
| GET | `/health` | Quick health check |
| POST | `/ask` | Main chatbot endpoint |
| POST | `/retrieve` | Debug: raw chunk retrieval |

### POST `/ask` — Request
```json
{
  "question": "What is the last date to apply?",
  "top_k": 4
}
```

### POST `/ask` — Response
```json
{
  "answer": "The last date for online application is August 31, 2026...",
  "sources": [
    { "source": "admission_faq.txt", "relevance": 0.87 }
  ],
  "mode": "fallback",
  "timestamp": "2026-04-17T10:30:00"
}
```

---

## File Structure

```
college-admission-chatbot/
│
├── backend/
│   ├── __init__.py
│   ├── ingest.py          ← Document chunking + ChromaDB indexing
│   ├── rag_pipeline.py    ← Retrieve + Generate (core logic)
│   └── api.py             ← FastAPI REST server
│
├── frontend/
│   └── app.py             ← Streamlit chat UI
│
├── data/
│   └── sample_docs/
│       └── admission_faq.txt   ← Knowledge base (add more files here)
│
├── docs/
│   └── architecture.md    ← This file
│
├── chroma_db/             ← Auto-generated after ingest.py (gitignored)
├── .env.example
├── .env                   ← Your secrets (gitignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Extending the Knowledge Base

To add more documents:
1. Drop any `.txt` file into `data/sample_docs/`
2. Re-run `python backend/ingest.py`
3. The chatbot immediately has access to the new content

For PDF support, install `pdfplumber` and update `ingest.py`:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = "\n".join(page.extract_text() for page in pdf.pages)
```
