"""
Knowledge Graph Module
-------------------------
Builds a lightweight in-memory graph (networkx) linking documents to the
entities extracted from them. Equipment mentioned across multiple documents
becomes a hub node -- this is what lets the copilot answer cross-document
questions like "show me everything related to Pump-101".
"""

import networkx as nx
from typing import Dict, List

_graph = nx.Graph()


def add_document_entities(doc_name: str, page_number: int, entities: Dict):
    """Adds a document node and links it to every entity found on that page."""
    doc_node = f"doc::{doc_name}"
    _graph.add_node(doc_node, type="document", label=doc_name)

    for category in ["equipment", "personnel", "regulations", "process_parameters"]:
        for item in entities.get(category, []):
            if not item:
                continue
            entity_node = f"{category}::{item}"
            _graph.add_node(entity_node, type=category, label=item)
            _graph.add_edge(doc_node, entity_node, page=page_number)


def get_graph_json() -> Dict:
    """Returns the graph in a format easy to render in React (e.g. react-force-graph)."""
    nodes = [
        {"id": n, "label": data.get("label", n), "type": data.get("type", "unknown")}
        for n, data in _graph.nodes(data=True)
    ]
    links = [
        {"source": u, "target": v, "page": data.get("page")}
        for u, v, data in _graph.edges(data=True)
    ]
    return {"nodes": nodes, "links": links}


def get_related_entities(entity_label: str) -> List[Dict]:
    """Find everything connected to a given entity (e.g. an equipment tag)."""
    matches = [n for n, d in _graph.nodes(data=True) if d.get("label") == entity_label]
    related = []
    for m in matches:
        for neighbor in _graph.neighbors(m):
            data = _graph.nodes[neighbor]
            related.append({"label": data.get("label"), "type": data.get("type")})
    return related


def reset_graph():
    global _graph
    _graph = nx.Graph()
