"""
ingest.py — Load admission documents into ChromaDB vector store

Run this once to build your knowledge base:
    python backend/ingest.py
"""

import os
import sys
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data" / "sample_docs"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "college_admissions"
CHUNK_SIZE = 400        # characters per chunk
CHUNK_OVERLAP = 80      # overlap between chunks


def load_text_files(directory: Path) -> list[dict]:
    """Load all .txt files from the data directory."""
    documents = []
    for txt_file in directory.glob("*.txt"):
        text = txt_file.read_text(encoding="utf-8")
        documents.append({
            "text": text,
            "source": txt_file.name,
            "category": txt_file.stem.replace("_", " ").title()
        })
    print(f"✅ Loaded {len(documents)} document(s) from {directory}")
    return documents


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def build_vector_store(documents: list[dict]) -> chromadb.Collection:
    """Chunk documents and store embeddings in ChromaDB."""
    # Use free local sentence-transformers model
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Drop existing collection if re-ingesting
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"🗑️  Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )

    all_chunks, all_ids, all_metas = [], [], []
    chunk_id = 0

    for doc in documents:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_ids.append(f"chunk_{chunk_id}")
            all_metas.append({
                "source": doc["source"],
                "category": doc["category"],
                "chunk_index": i
            })
            chunk_id += 1

    # Add in batches
    batch_size = 50
    for i in range(0, len(all_chunks), batch_size):
        collection.add(
            documents=all_chunks[i:i + batch_size],
            ids=all_ids[i:i + batch_size],
            metadatas=all_metas[i:i + batch_size]
        )

    print(f"✅ Indexed {len(all_chunks)} chunks into ChromaDB at '{CHROMA_DIR}'")
    return collection


def main():
    print("\n🚀 Starting document ingestion...\n")
    documents = load_text_files(DATA_DIR)
    if not documents:
        print("❌ No documents found. Add .txt files to data/sample_docs/")
        sys.exit(1)
    collection = build_vector_store(documents)
    print(f"\n✅ Done! Collection has {collection.count()} chunks ready for retrieval.\n")


if __name__ == "__main__":
    main()
