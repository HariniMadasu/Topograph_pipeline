"""
graph_builder.py
----------------
Builds a NetworkX DiGraph from the three loaded datasets:
  - Nodes = the 41 knowledge entries, attributed with category, confidence,
    shelf_life, knowledge_type, and quality pass_count (0-8).
  - Edges = directed "suggested_chain" links from cross_references.json,
    restricted to pairs where BOTH endpoints are inside the 41-node sample
    (the full topology referenced in the README extends to ek_0253, but we
    only have content for ek_0000-ek_0040).
"""

import networkx as nx

CONFIDENCE_ORDINAL = {"low": 0, "medium": 1, "high": 2}


def build_knowledge_graph(ek_entries, quality_per_entry, ref_edges):
    G = nx.DiGraph()

    for entry in ek_entries:
        node_id = entry["id"]
        quality = quality_per_entry.get(node_id, {})
        G.add_node(
            node_id,
            title=entry["title"],
            category=entry["category"],
            knowledge_type=entry.get("knowledge_type", "unknown"),
            confidence=entry.get("confidence", "unknown"),
            confidence_score=CONFIDENCE_ORDINAL.get(entry.get("confidence"), 1),
            shelf_life=entry.get("shelf_life", "unknown"),
            chain_potential=bool(entry.get("chain_potential")),
            pass_count=quality.get("pass_count", None),
        )

    node_ids = set(G.nodes())
    n_total_edges = len(ref_edges)
    n_kept = 0
    for src, dst in ref_edges:
        if src in node_ids and dst in node_ids:
            G.add_edge(src, dst, relationship="suggested_chain")
            n_kept += 1

    G.graph["n_edges_outside_sample"] = n_total_edges - n_kept
    return G


def graph_summary(G):
    """Quick structural summary dict, useful for the README / report."""
    undirected = G.to_undirected()
    summary = {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "n_isolated_nodes": sum(1 for n in G.nodes() if G.degree(n) == 0),
        "n_weakly_connected_components": nx.number_weakly_connected_components(G),
        "is_dag": nx.is_directed_acyclic_graph(G),
        "density": nx.density(G),
        "edges_referencing_outside_sample": G.graph.get("n_edges_outside_sample", None),
    }
    return summary


if __name__ == "__main__":
    from data_loader import (
        load_experiential_knowledge,
        load_quality_metrics,
        load_cross_references,
    )

    ek = load_experiential_knowledge("data/experiential_knowledge_41.json")
    _, per_entry, _ = load_quality_metrics("data/quality_metrics.json")
    edges, _ = load_cross_references("data/cross_references.json")

    G = build_knowledge_graph(ek, per_entry, edges)
    import json
    print(json.dumps(graph_summary(G), indent=2))
