# 🎓 College Admission Chatbot (RAG-Powered)

> An AI-powered chatbot for college admission queries using Retrieval-Augmented Generation (RAG) pipeline.

 
**Domain:** NLP · Information Retrieval · LLMs  
**Stack:** Python · ChromaDB · Sentence Transformers · FastAPI · Streamlit

---

## 🧠 What It Does

Students ask questions like:
- *"What is the last date to apply for B.Tech?"*
- *"What are the eligibility criteria for MBA?"*
- *"How much is the hostel fee?"*

The chatbot retrieves the most relevant chunks from college documents and generates a precise, context-aware answer — no hallucinations, no generic responses.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
[Query Encoder] ──► sentence-transformers
    │
    ▼
[Vector Search] ──► ChromaDB (cosine similarity)
    │
    ▼
[Context Builder] ──► Top-K relevant chunks
    │
    ▼
[LLM Response] ──► OpenAI GPT / local fallback
    │
    ▼
Answer + Source Citations
```

---

## 📁 Project Structure

```
college-admission-chatbot/
├── backend/
│   ├── ingest.py          # Load & chunk documents into ChromaDB
│   ├── rag_pipeline.py    # Core RAG: retrieve + generate
│   └── api.py             # FastAPI server
├── frontend/
│   └── app.py             # Streamlit chat UI
├── data/
│   └── sample_docs/       # Sample admission FAQs (txt/pdf)
├── docs/
│   └── architecture.md
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/college-admission-chatbot.git
cd college-admission-chatbot
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Add your OpenAI API key (optional — works without it using fallback mode)
```

### 3. Ingest Sample Documents

```bash
python backend/ingest.py
```

### 4. Run the Chatbot

**Option A – Streamlit UI (recommended for demo)**
```bash
streamlit run frontend/app.py
```

**Option B – FastAPI Backend**
```bash
uvicorn backend.api:app --reload
# API at http://localhost:8000/docs
```

---

## 🔑 Environment Variables

| Variable | Description | Required |
|---|---|---|
| `OPENAI_API_KEY` | For GPT-3.5/4 responses | No (fallback mode available) |
| `CHROMA_PERSIST_DIR` | Where ChromaDB stores data | No (default: `./chroma_db`) |

---

## 🧪 Demo Mode (No API Key Needed)

The prototype ships with a **built-in fallback mode** — it uses smart keyword matching on retrieved chunks to generate responses without any external API. Perfect for demos and GitHub showcasing.

---

## 📈 RAG Pipeline — How It Works

1. **Ingest** — Admission documents are split into 500-token chunks with 100-token overlap
2. **Embed** — Each chunk is converted to a vector using `sentence-transformers/all-MiniLM-L6-v2` (free, local)
3. **Store** — Vectors are indexed in ChromaDB with metadata (source, category)
4. **Retrieve** — User query is embedded, top-5 similar chunks are fetched
5. **Generate** — LLM (or fallback) constructs a grounded answer from retrieved context

---

## 🛣️ Roadmap

- [x] Core RAG pipeline with ChromaDB
- [x] Streamlit chat interface
- [x] FastAPI REST endpoint
- [x] Demo/fallback mode (no API key)
- [ ] PDF ingestion pipeline
- [ ] Admin dashboard to upload new documents
- [ ] Multi-college support
- [ ] Deployment to Render / HuggingFace Spaces

---

## 📄 License

MIT License — free to use and build upon.
