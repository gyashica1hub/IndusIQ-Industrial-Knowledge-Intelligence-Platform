"""
Vector Store Module
--------------------
Wraps ChromaDB with a local sentence-transformers embedding function so the
prototype runs fully offline (no embedding API cost/latency), while the
generation step still uses Groq for speed.
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "industrial_docs"

_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=_embedding_fn,
)


def add_chunks(chunks: List[Dict]):
    """Add a list of chunk records (from ingestion.py) into the vector store."""
    if not chunks:
        return
    _collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["chunk_text"] for c in chunks],
        metadatas=[{
            "doc_name": c["doc_name"],
            "doc_type": c["doc_type"],
            "page_number": c["page_number"],
        } for c in chunks],
    )


def query(question: str, n_results: int = 5) -> List[Dict]:
    """Retrieve the top-k most relevant chunks for a question."""
    results = _collection.query(query_texts=[question], n_results=n_results)
    hits = []
    if not results["documents"]:
        return hits
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        hits.append({
            "text": doc,
            "doc_name": meta["doc_name"],
            "doc_type": meta["doc_type"],
            "page_number": meta["page_number"],
            "relevance_score": round(1 - dist, 3),
        })
    return hits


def list_documents() -> List[str]:
    all_meta = _collection.get()["metadatas"]
    return sorted(list({m["doc_name"] for m in all_meta})) if all_meta else []


def reset_store():
    global _collection
    _client.delete_collection(COLLECTION_NAME)
    _collection = _client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=_embedding_fn
    )
