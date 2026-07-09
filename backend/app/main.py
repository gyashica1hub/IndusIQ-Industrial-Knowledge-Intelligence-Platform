"""
FastAPI Backend — Industrial Knowledge Intelligence Platform
----------------------------------------------------------------
Endpoints:
  POST /upload         -> ingest a PDF (parse, chunk, embed, extract entities, build graph)
  POST /chat           -> ask a question, get RAG answer + citations
  GET  /graph          -> get knowledge graph for visualization
  GET  /documents      -> list ingested documents
  GET  /entity/{label} -> get everything related to one entity (e.g. an equipment tag)
  POST /reset          -> clear the knowledge base (useful for demos)
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import ingestion, vector_store, entity_extraction, knowledge_graph, rag_chat

app = FastAPI(title="Industrial Knowledge Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class ChatRequest(BaseModel):
    question: str


@app.post("/upload")
async def upload_document(file: UploadFile = File(...), doc_type: str = "general"):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported in this prototype.")

    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 1. Ingest + chunk
    chunks = ingestion.ingest_file(str(save_path), doc_type=doc_type)
    if not chunks:
        raise HTTPException(422, "Could not extract any text from this PDF.")

    # 2. Embed + store for retrieval
    vector_store.add_chunks(chunks)

    # 3. Extract entities per page and build knowledge graph
    #    (grouped by page to limit LLM calls -- one call per unique page)
    seen_pages = {}
    for c in chunks:
        key = (c["doc_name"], c["page_number"])
        seen_pages.setdefault(key, []).append(c["chunk_text"])

    entity_summary = {"equipment": set(), "personnel": set(), "regulations": set()}
    for (doc_name, page_number), texts in seen_pages.items():
        combined_text = " ".join(texts)
        entities = entity_extraction.extract_entities(combined_text)
        knowledge_graph.add_document_entities(doc_name, page_number, entities)
        for key in entity_summary:
            entity_summary[key].update(entities.get(key, []))

    return {
        "status": "success",
        "doc_name": file.filename,
        "chunks_indexed": len(chunks),
        "pages_processed": len(seen_pages),
        "entities_found": {k: sorted(v) for k, v in entity_summary.items()},
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty.")
    result = rag_chat.answer_question(req.question)
    return result


@app.get("/graph")
async def get_graph():
    return knowledge_graph.get_graph_json()


@app.get("/documents")
async def get_documents():
    return {"documents": vector_store.list_documents()}


@app.get("/entity/{label}")
async def get_entity(label: str):
    related = knowledge_graph.get_related_entities(label)
    return {"entity": label, "related": related}


@app.post("/reset")
async def reset():
    vector_store.reset_store()
    knowledge_graph.reset_graph()
    for f in UPLOAD_DIR.glob("*"):
        f.unlink()
    return {"status": "reset complete"}


@app.get("/")
async def root():
    return {"message": "Industrial Knowledge Intelligence API is running"}
