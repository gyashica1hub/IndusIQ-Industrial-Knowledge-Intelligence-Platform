"""
RAG Chat Module
-----------------
Retrieves relevant chunks from the vector store and asks Groq to answer
using ONLY that context, with explicit source citations (doc name + page).
This is the "Expert Knowledge Copilot" piece of the challenge.
"""

import os
from groq import Groq
from app import vector_store

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

SYSTEM_PROMPT = """You are an Industrial Knowledge Copilot for plant engineers and maintenance
technicians. Answer ONLY using the provided context chunks. If the context doesn't
contain the answer, say so clearly instead of guessing -- wrong answers in an
industrial setting can be dangerous.

Always structure your answer as:
1. A direct, concise answer (2-4 sentences max, technician-friendly language)
2. A "Sources" note referencing which document(s) and page(s) you used

Do not invent equipment tags, values, or regulations that are not in the context."""


def answer_question(question: str, n_results: int = 5) -> dict:
    hits = vector_store.query(question, n_results=n_results)

    if not hits:
        return {
            "answer": "No relevant documents found in the knowledge base yet. Please upload documents first.",
            "sources": [],
        }

    context = "\n\n".join(
        f"[Source: {h['doc_name']}, Page {h['page_number']}]\n{h['text']}"
        for h in hits
    )

    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=500,
    )

    answer_text = response.choices[0].message.content.strip()

    sources = [
        {
            "doc_name": h["doc_name"],
            "page_number": h["page_number"],
            "relevance_score": h["relevance_score"],
        }
        for h in hits
    ]

    return {"answer": answer_text, "sources": sources}
