"""
graph_analytics.py
----------------
Standard graph analytics on the declared cross-reference DAG: centrality,
longest attack chains, and category-to-category bridging patterns.
"""

import networkx as nx
from collections import Counter


def centrality_report(G, top_k=10):
    """Returns a list of (node_id, title, category, in_degree, out_degree,
    betweenness) sorted by out-degree then betweenness, for the top_k most
    structurally important nodes."""
    betweenness = nx.betweenness_centrality(G)
    rows = []
    for n in G.nodes():
        rows.append(
            {
                "id": n,
                "title": G.nodes[n]["title"],
                "category": G.nodes[n]["category"],
                "in_degree": G.in_degree(n),
                "out_degree": G.out_degree(n),
                "betweenness": round(betweenness[n], 4),
            }
        )
    rows.sort(key=lambda r: (r["out_degree"], r["betweenness"]), reverse=True)
    return rows[:top_k]


def longest_chains(G, top_k=5):
    """Finds the longest directed paths in the DAG - the most-developed
    'attack chains' in the curated graph. Returns list of node-id lists."""
    if not nx.is_directed_acyclic_graph(G):
        return []
    chains = []
    sources = [n for n in G.nodes() if G.in_degree(n) == 0 and G.out_degree(n) > 0]
    for s in sources:
        for t in [n for n in G.nodes() if G.out_degree(n) == 0]:
            for path in nx.all_simple_paths(G, s, t):
                if len(path) > 1:
                    chains.append(path)
    chains.sort(key=len, reverse=True)
    # de-dupe identical paths
    seen = set()
    unique_chains = []
    for c in chains:
        key = tuple(c)
        if key not in seen:
            seen.add(key)
            unique_chains.append(c)
    return unique_chains[:top_k]


def category_bridge_matrix(G):
    """Counts directed category -> category transitions across all edges.
    Reveals which knowledge categories typically feed into which others
    (e.g. signal_interpretation -> bypass_technique -> chain_pattern)."""
    counts = Counter()
    for u, v in G.edges():
        cat_u = G.nodes[u]["category"]
        cat_v = G.nodes[v]["category"]
        counts[(cat_u, cat_v)] += 1
    return counts


def fragmentation_report(G):
    """Summarizes how fragmented the declared cross-reference graph is -
    relevant because beta_0 in TDA terms IS the connected-component count."""
    components = list(nx.weakly_connected_components(G))
    isolated = [n for n in G.nodes() if G.degree(n) == 0]
    sizes = sorted([len(c) for c in components], reverse=True)
    return {
        "n_components": len(components),
        "n_isolated_nodes": len(isolated),
        "isolated_node_ids": isolated,
        "component_sizes": sizes,
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from data_loader import load_experiential_knowledge, load_quality_metrics, load_cross_references
    from graph_builder import build_knowledge_graph

    ek = load_experiential_knowledge("data/experiential_knowledge_41.json")
    _, per_entry, _ = load_quality_metrics("data/quality_metrics.json")
    edges, _ = load_cross_references("data/cross_references.json")
    G = build_knowledge_graph(ek, per_entry, edges)

    print("=== Top nodes by out-degree / betweenness ===")
    for r in centrality_report(G, top_k=5):
        print(r)

    print("\n=== Longest declared chains ===")
    for c in longest_chains(G, top_k=5):
        print(" -> ".join(c))

    print("\n=== Category bridge matrix ===")
    for (a, b), n in category_bridge_matrix(G).most_common():
        print(f"  {a} -> {b}: {n}")

    print("\n=== Fragmentation report ===")
    print(fragmentation_report(G))
