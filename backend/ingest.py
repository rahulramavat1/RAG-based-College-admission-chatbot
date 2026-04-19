"""
ingest.py — Load documents from data/sample_docs/ and store embeddings in FAISS.
Run this once before starting the chatbot:
    python backend/ingest.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./faiss_index")
DATA_DIR         = os.path.join(os.path.dirname(__file__), "..", "data", "sample_docs")
CHUNK_SIZE       = 500   # characters
CHUNK_OVERLAP    = 100   # characters
MODEL_NAME       = "all-MiniLM-L6-v2"

def ingest():
    print("=" * 55)
    print("  College Admission Chatbot — Document Ingestion (FAISS)")
    print("=" * 55)

    # 1. Load documents
    print(f"\n[1/4] Loading documents from: {DATA_DIR}")
    if not os.path.exists(DATA_DIR):
        print(f"  ERROR: Data directory not found: {DATA_DIR}")
        sys.exit(1)
        
    loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
    docs_txt = loader.load()
    
    loader_md = DirectoryLoader(DATA_DIR, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
    docs_md = loader_md.load()
    
    docs = docs_txt + docs_md
    
    if not docs:
        print("  ERROR: No documents found. Add .txt or .md files to data/sample_docs/")
        sys.exit(1)
        
    print(f"  Found {len(docs)} document(s).")
    
    for doc in docs:
        # Standardize source path for frontend usage
        doc.metadata["source"] = Path(doc.metadata.get("source", "unknown")).name

    # 2. Chunk
    print(f"\n[2/4] Chunking (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}) …")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    print(f"  Total chunks: {len(chunks)}")

    # 3. Embedding
    print(f"\n[3/4] Initialize Embeddings ({MODEL_NAME}) …")
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

    # 4. Connect to FAISS and Store
    print(f"\n[4/4] Generating embeddings and storing in FAISS …")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    vectorstore.save_local(FAISS_INDEX_PATH)

    print(f"\n[DONE] Ingestion complete! {len(chunks)} chunks indexed.")
    print(f"    FAISS index stored at: {os.path.abspath(FAISS_INDEX_PATH)}")
    print("=" * 55)

if __name__ == "__main__":
    ingest()
