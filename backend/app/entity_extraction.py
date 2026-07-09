"""
Entity Extraction Module
--------------------------
Uses Groq LLM to pull structured entities (equipment, dates, personnel,
regulatory references, process parameters) out of raw document chunks so
they can be linked into a knowledge graph.
"""

import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

EXTRACTION_PROMPT = """You are an industrial document analyst. Extract structured entities
from the text below. Return ONLY valid JSON, no preamble, no markdown fences.

Schema:
{{
  "equipment": ["list of equipment tags/names, e.g. Pump-101, Boiler-3"],
  "personnel": ["list of people or roles mentioned"],
  "dates": ["list of dates or time references mentioned"],
  "regulations": ["list of regulatory/standard references, e.g. OISD, Factory Act, ISO"],
  "process_parameters": ["list of parameters with values, e.g. 'pressure: 12 bar'"]
}}

If a category has nothing found, return an empty list for it.

Text:
\"\"\"{text}\"\"\"
"""


def extract_entities(text: str) -> dict:
    """Calls Groq to extract entities from a chunk of text. Returns a dict."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": EXTRACTION_PROMPT.format(text=text[:3000])}
            ],
            temperature=0,
            max_tokens=600,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        # Fail soft: empty entities rather than crashing the ingestion pipeline
        return {
            "equipment": [], "personnel": [], "dates": [],
            "regulations": [], "process_parameters": [],
            "_error": str(e),
        }
