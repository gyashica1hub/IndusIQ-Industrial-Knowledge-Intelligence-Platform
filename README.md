<div align="center">

# IndusIQ
### Industrial Knowledge Intelligence Platform

**A Unified Asset & Operations Brain for Industrial Enterprises**

Ingests heterogeneous industrial documents — maintenance logs, inspection reports, SOPs, and engineering records — into a queryable knowledge graph, and answers operational questions with cited, grounded AI responses.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![Groq](https://img.shields.io/badge/LLM-Groq-orange.svg)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](#license)

</div>

---

## Overview

Industrial enterprises routinely operate 7–12 disconnected document systems per plant — P&IDs in one place, maintenance records in another, inspection reports in a third, and regulatory submissions scattered across email archives. This fragmentation is not just an inefficiency; it is a safety, quality, and operational-continuity risk, particularly as experienced personnel retire and take undocumented institutional knowledge with them.

**IndusIQ** addresses this by building a unified, continuously-updated knowledge layer over an organization's industrial document corpus. It combines document ingestion, automated entity extraction, knowledge graph construction, and retrieval-augmented generation (RAG) into a single platform that lets any technician or engineer query the collective intelligence of the plant — from any device, at the point of need.

## Core Capabilities

| Module | Description |
|---|---|
| **Document Ingestion Pipeline** | Parses PDFs (text and embedded tables), performs page-aware chunking, and indexes content into a vector store for retrieval. |
| **Entity Extraction Engine** | Uses an LLM to identify equipment tags, personnel, regulatory references, and process parameters from unstructured text. |
| **Knowledge Graph** | Links documents to extracted entities, surfacing cross-document relationships — e.g., every document referencing a given piece of equipment. |
| **Expert Knowledge Copilot** | A retrieval-augmented chat interface that answers operational and compliance questions with direct source citations (document + page). |

## Architecture

```
PDF Upload
    │
    ▼
Ingestion Layer  ──▶  Text & table extraction, page-aware chunking
    │
    ├──▶  Vector Store  ──▶  ChromaDB + local sentence-transformer embeddings
    │
    └──▶  Entity Extraction  ──▶  Groq LLM → structured entity JSON
                │
                ▼
         Knowledge Graph  ──▶  NetworkX (document ↔ entity relationships)

User Query
    │
    ▼
RAG Chat Layer  ──▶  Top-k retrieval from vector store → Groq generation
    │                  with mandatory source citation
    ▼
React Frontend  ──▶  FastAPI (/upload · /chat · /graph · /documents · /entity/{label})
```

**Design rationale:**
- **Local embeddings, cloud generation** — sentence-transformer embeddings run locally with no per-query API cost or latency; Groq is reserved for the reasoning step, keeping the pipeline fast and cost-efficient at scale.
- **Page-level citation by default** — every answer is traceable to its source document and page number, which is a hard requirement for decision-making in safety-critical industrial contexts.
- **Entity-centric graph, not document-centric** — a query about a specific equipment tag surfaces every document that has ever referenced it, rather than relying on keyword search alone.

## Tech Stack

- **Backend:** FastAPI, ChromaDB, NetworkX, sentence-transformers, Groq API
- **Frontend:** React, Vite, react-force-graph
- **LLM:** Groq (`llama-3.1-8b-instant`)

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Groq API key](https://console.groq.com)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp .env.example .env
# Add your GROQ_API_KEY to .env

python data/generate_samples.py  # generates sample documents for demo
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser. The backend must be running concurrently on port `8000`.

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/upload` | `POST` | Ingest a PDF document into the knowledge base |
| `/chat` | `POST` | Ask a question, receive a cited RAG-generated answer |
| `/graph` | `GET` | Retrieve the current knowledge graph as JSON |
| `/documents` | `GET` | List all ingested documents |
| `/entity/{label}` | `GET` | Retrieve all entities/documents related to a given entity |
| `/reset` | `POST` | Clear the knowledge base |

## Roadmap

The knowledge graph and RAG layer built here form the foundation for a broader set of capabilities:

- **Maintenance Intelligence & RCA Agent** — fusing work order history, equipment failure records, and real-time operating conditions for predictive maintenance and root-cause analysis.
- **Quality & Regulatory Compliance Intelligence** — automated compliance-gap detection against regulatory frameworks, with auto-generated audit evidence packages.
- **Lessons Learned & Failure Intelligence Engine** — cross-referencing incident reports and audit findings to surface systemic patterns before they recur.
- **Computer vision-based P&ID parsing** — extending ingestion beyond text-based PDFs to engineering drawings and scanned documents.
- **Persistent graph storage** (e.g., Neo4j) for production-scale deployments.

## Known Limitations

- Current prototype supports PDF ingestion only; P&ID and scanned-drawing parsing would require a computer vision pipeline.
- Entity extraction accuracy is bounded by the underlying LLM (`llama-3.1-8b-instant`); a production deployment would benefit from a larger or fine-tuned model.
- The knowledge graph is held in memory and resets on backend restart; production use would require persistent graph storage.

## License

This project is released under the MIT License.

---

<div align="center">

**Authors**

Yashica Gupta · Dhruv Raj Ghai

</div>
