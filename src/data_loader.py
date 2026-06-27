"""
data_loader.py
----------------
Loads the three hackathon-provided dataset files:
  - experiential_knowledge_41.json  (41 knowledge entries, ek_0000-ek_0040)
  - quality_metrics.json            (per-entry quality checklist + aggregate scores)
  - cross_references.json           (directed edges: complementary pairs / suggested chains)

Note: experiential_knowledge_41.json ships with a trailing comma before the
closing bracket of the "knowledge" list, which breaks strict json.load(). We
use a lenient loader that strips trailing commas before parsing so the
pipeline is robust to this without silently losing data.
"""

import json
import re
from pathlib import Path


def _load_json_lenient(path):
    """Load JSON, tolerating a trailing comma before a closing ] or }."""
    text = Path(path).read_text()
    cleaned = re.sub(r",(\s*[\]}])", r"\1", text)
    return json.loads(cleaned)


def load_experiential_knowledge(path):
    """Returns the list of 41 knowledge-entry dicts (ek_0000..ek_0040)."""
    data = _load_json_lenient(path)
    entries = data["knowledge"]
    assert len(entries) == len({e["id"] for e in entries}), "duplicate ek ids found"
    return entries


def load_quality_metrics(path):
    """Returns (aggregate_scores: dict, per_entry_checks: dict[id -> dict])."""
    data = _load_json_lenient(path)
    aggregate = data["layer0"]
    checklist = data["quality_checklist"]
    per_entry = {item["id"]: item for item in checklist["items"]}
    return aggregate, per_entry, checklist["check_pass_rates"]


def load_cross_references(path):
    """Returns (edges: list of (source_id, target_id) tuples, raw_data: dict)."""
    data = _load_json_lenient(path)
    edges = []
    for pair in data["complementary_pairs"]:
        src = pair["a"]["id"]
        dst = pair["b"]["id"]
        edges.append((src, dst))
    return edges, data


if __name__ == "__main__":
    ek = load_experiential_knowledge("data/experiential_knowledge_41.json")
    agg, per_entry, pass_rates = load_quality_metrics("data/quality_metrics.json")
    edges, raw = load_cross_references("data/cross_references.json")
    print(f"Knowledge entries: {len(ek)}")
    print(f"Quality-assessed entries: {len(per_entry)}")
    print(f"Cross-reference edges (full topology, up to ek_0253): {len(edges)}")
    node_ids = {e['id'] for e in ek}
    sub_edges = [(a, b) for a, b in edges if a in node_ids and b in node_ids]
    print(f"Edges within the 41-node subgraph: {len(sub_edges)}")
