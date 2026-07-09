# Industrial Knowledge Intelligence — Prototype

Unified Asset & Operations Brain: ingest heterogeneous industrial documents,
build a knowledge graph, and answer engineer/technician questions with
cited, grounded answers (RAG).

## What's built (scoped for hackathon time)

| Problem statement piece | Status |
|---|---|
| Universal Document Ingestion & Knowledge Graph Agent | Built (PDF + tables → entities → graph) |
| Expert Knowledge Copilot (RAG, citations) | Built |
| Maintenance Intelligence & RCA Agent | Talk track only — see "What to say" below |
| Quality & Regulatory Compliance Intelligence | Partially built — regulations are extracted & graphed; formal gap-detection is a stretch goal |
| Lessons Learned & Failure Intelligence Engine | Talk track only |

Don't try to build all 5 sub-agents — no team does in a hackathon. Judges (per
the rubric: Innovation 25%, Business Impact 25%, Technical 20%, Scalability 15%,
UX 15%) reward a **working, well-demoed core** over five half-broken features.

## Architecture

```
PDF upload ──▶ ingestion.py (pdfplumber: text + tables, page-aware chunks)
                    │
                    ├──▶ vector_store.py (ChromaDB + local sentence-transformer embeddings)
                    │         │
                    └──▶ entity_extraction.py (Groq LLM → equipment/personnel/regs/params JSON)
                              │
                              ▼
                    knowledge_graph.py (networkx: doc ↔ entity edges)

User question ──▶ rag_chat.py (retrieve top-k chunks from Chroma → Groq answers
                   with citations, refuses to answer outside context)

React frontend ──▶ FastAPI (/upload, /chat, /graph, /documents, /entity/{label})
```

**Why these choices (say this in your pitch):**
- Local embeddings (sentence-transformers) = no API cost/latency for the ingestion
  step, only Groq calls for reasoning — cheaper and faster at scale.
- Page-level chunking with citations = answers always traceable to source page,
  which matters for safety-critical industrial use (the "no individual can
  connect all the dots" problem in the brief).
- Graph is entity-centric, not just document-centric — so a query about
  "Pump-101" surfaces every document that ever mentioned it, not just keyword hits.

## Setup

### Backend
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your GROQ_API_KEY (get one free at console.groq.com)
python data/generate_samples.py   # generates 3 dummy PDFs for the demo
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# open http://localhost:5173
```

## Demo script (for judges)

1. **Upload tab** — upload all 3 sample PDFs from `backend/data/sample_docs/`
   (maintenance log, inspection report, SOP). Point out the entity extraction
   summary that appears after each upload.
2. **Knowledge Graph tab** — show that `Pump-101`, `Anita Sharma`, and
   `OISD-118` each appear as single nodes connected to *multiple* documents —
   this is the "knowledge fragmentation solved" visual proof.
3. **Expert Copilot tab** — ask:
   - "What caused the Pump-101 vibration issue and how was it fixed?"
     (answer pulls from the maintenance log, cites page + doc)
   - "Are there any open compliance gaps right now?"
     (answer should surface the Boiler-3 certification renewal gap from the
     inspection report — this is your compliance-intelligence proof point)
   - "Summarize everything related to Compressor-7."
     (cross-document synthesis)

## What to say for the unbuilt pieces (Maintenance RCA agent, Lessons Learned engine)

Frame them as the **roadmap**, not a gap:
> "The knowledge graph and RAG layer we've built are the foundation every one
> of the other four agents needs — you can't do RCA or lessons-learned
> pattern detection without first having entities and relationships unified
> across documents. What we're demoing today is that foundation working
> end-to-end; RCA and failure-pattern-mining are the next layer we'd build on
> top of this graph, using the same entity nodes."

This is a legitimate technical argument, not just an excuse — say it with
confidence.

## Known limitations (be upfront if asked)

- PDF only in this prototype (P&ID image/CAD parsing would need computer
  vision — OCR pipeline is a natural next step, mentioned in "Suggested
  Technologies").
- Entity extraction accuracy depends on Groq's small model (`llama-3.1-8b-instant`)
  — good enough for a demo, a production system would fine-tune or use a
  larger model for higher precision.
- Knowledge graph is in-memory (resets on backend restart) — fine for a demo,
  would move to a persistent graph DB (Neo4j) for production.
