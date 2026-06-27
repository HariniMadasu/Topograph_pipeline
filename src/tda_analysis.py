"""
tda_analysis.py
----------------
Phase 1 (Diagnosis): Quality-Filtered TDA on explicit cross-reference edges.
Phase 2 (Healing): Semantic NLP TDA on textual data to find missing links.
"""

import numpy as np
import gudhi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances

# ==========================================
# PHASE 1: QUALITY-FILTERED TDA (The Diagnosis)
# ==========================================
def build_quality_filtered_complex(ek_entries, per_entry_quality, ref_edges):
    """Builds a Simplicial Complex using explicit edges, filtered by the 0-8 Quality Pass Count."""
    st = gudhi.SimplexTree()
    node_to_idx = {}
    idx_to_node = {}
    
    # Insert Nodes (0-simplices)
    for idx, entry in enumerate(ek_entries):
        node_id = entry["id"]
        node_to_idx[node_id] = idx
        idx_to_node[idx] = node_id
        
        # Invert score: Pass count 8 enters at filtration 0.0 (perfect quality)
        pass_count = per_entry_quality.get(node_id, {}).get("pass_count", 0)
        filtration_val = 8.0 - float(pass_count)
        st.insert([idx], filtration=filtration_val)
        
    # Insert Edges (1-simplices)
    for u, v in ref_edges:
        if u in node_to_idx and v in node_to_idx:
            st.insert([node_to_idx[u], node_to_idx[v]])
            
    st.make_filtration_non_decreasing()
    persistence = st.persistence()
    return st, persistence, idx_to_node

# ==========================================
# PHASE 2: SEMANTIC NLP TDA (The Cure)
# ==========================================
def build_text_corpus(ek_entries):
    corpus = []
    for e in ek_entries:
        parts = [
            e.get("title", ""),
            e.get("knowledge", ""),
            e.get("abstracted_pattern", {}).get("narrative", ""),
            " ".join(e.get("pitfalls", [])),
            " ".join(e.get("abstracted_pattern", {}).get("generalizes_to", [])),
        ]
        corpus.append(" ".join(parts))
    return corpus

def semantic_distance_matrix(corpus):
    vectorizer = TfidfVectorizer(stop_words="english", max_features=2000)
    tfidf = vectorizer.fit_transform(corpus)
    dist = cosine_distances(tfidf)
    np.fill_diagonal(dist, 0.0)
    return dist, vectorizer, tfidf

def compute_persistence(distance_matrix, max_edge_length=1.0, max_dimension=2):
    rips = gudhi.RipsComplex(distance_matrix=distance_matrix, max_edge_length=max_edge_length)
    simplex_tree = rips.create_simplex_tree(max_dimension=max_dimension)
    persistence = simplex_tree.persistence()
    return simplex_tree, persistence

def betti_curve(simplex_tree, max_dim=1, n_steps=60, max_eps=1.0):
    eps_values = np.linspace(0.0, max_eps, n_steps)
    betti_over_time = {d: [] for d in range(max_dim + 1)}
    for eps in eps_values:
        bettis = simplex_tree.persistent_betti_numbers(eps, eps)
        for d in range(max_dim + 1):
            b = bettis[d] if d < len(bettis) else 0
            betti_over_time[d].append((eps, b))
    return betti_over_time

def find_missing_link_candidates(distance_matrix, node_ids, existing_edges, top_k=5, max_distance=0.55):
    existing_pairs = set(frozenset((a, b)) for a, b in existing_edges)
    n = len(node_ids)
    candidates = []
    
    for i in range(n):
        for j in range(i + 1, n):
            pair_key = frozenset((node_ids[i], node_ids[j]))
            if pair_key in existing_pairs:
                continue
            d = distance_matrix[i, j]
            if d <= max_distance:
                candidates.append((node_ids[i], node_ids[j], d))
                
    candidates.sort(key=lambda x: x[2])
    return candidates[:top_k]