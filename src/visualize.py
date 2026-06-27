"""
visualize.py
----------------
All plots are saved as PNG files into the outputs/ directory.
"""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

CATEGORY_COLORS = {
    "chain_pattern": "#E07A5F",
    "signal_interpretation": "#3D405B",
    "tactical_priority": "#81B29A",
    "bypass_technique": "#F2CC8F",
    "pitfall": "#9B5DE5",
}


def plot_network(G, out_path):
    fig, ax = plt.subplots(figsize=(11, 9))
    pos = nx.spring_layout(G, seed=42, k=0.9)
    colors = [CATEGORY_COLORS.get(G.nodes[n]["category"], "#999999") for n in G.nodes()]
    sizes = [250 + 150 * G.degree(n) for n in G.nodes()]

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#888888", arrows=True,
                            arrowsize=12, alpha=0.7, connectionstyle="arc3,rad=0.05")
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colors, node_size=sizes,
                            edgecolors="white", linewidths=0.8)
    labels = {n: n.replace("ek_", "") for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax, font_size=7, font_color="black")

    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=c,
                           markersize=10, label=cat) for cat, c in CATEGORY_COLORS.items()]
    ax.legend(handles=handles, loc="upper left", fontsize=9, frameon=True)
    ax.set_title("Knowledge Graph: declared cross-reference structure (41 entries)\n"
                  "17 isolated nodes + 27 weakly-connected components - a sparse forest, no cycles",
                  fontsize=11)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_persistence_diagram(persistence, out_path, max_dim=2):
    fig, ax = plt.subplots(figsize=(7, 6))
    dim_colors = {0: "#3D405B", 1: "#E07A5F", 2: "#81B29A"}
    finite_max = 0.0
    for d, (b, death) in persistence:
        if death != float("inf"):
            finite_max = max(finite_max, death)
    plot_max = max(finite_max * 1.1, 0.1)

    for d in range(max_dim + 1):
        births = [b for dd, (b, death) in persistence if dd == d]
        deaths = [death if death != float("inf") else plot_max for dd, (b, death) in persistence if dd == d]
        if births:
            ax.scatter(births, deaths, s=28, color=dim_colors.get(d, "gray"),
                       label=f"$H_{d}$", alpha=0.75, edgecolors="white", linewidths=0.4)

    ax.plot([0, plot_max], [0, plot_max], color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Birth (semantic distance)")
    ax.set_ylabel("Death (semantic distance)")
    ax.set_title("Persistence diagram - semantic TF-IDF distance space")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_betti_curves(betti_over_time, out_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = {0: "#3D405B", 1: "#E07A5F", 2: "#81B29A"}
    for dim, series in betti_over_time.items():
        xs = [p[0] for p in series]
        ys = [p[1] for p in series]
        ax.plot(xs, ys, label=f"$\\beta_{dim}$", color=colors.get(dim, "gray"), linewidth=2)
    ax.set_xlabel("Filtration scale (epsilon, semantic distance)")
    ax.set_ylabel("Betti number")
    ax.set_title("Betti curves across the semantic filtration\n"
                  "($\\beta_0$ = fragments merging, $\\beta_1$ = loops opening/closing)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_centrality(rows, out_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = [f"{r['id']}\n{r['category']}" for r in rows]
    out_deg = [r["out_degree"] for r in rows]
    in_deg = [r["in_degree"] for r in rows]
    x = np.arange(len(rows))
    width = 0.35
    ax.bar(x - width / 2, out_deg, width, label="out-degree", color="#E07A5F")
    ax.bar(x + width / 2, in_deg, width, label="in-degree", color="#3D405B")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7, rotation=0)
    ax.set_ylabel("Degree")
    ax.set_title("Top entries by declared-chain connectivity")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_category_distribution(ek_entries, out_path):
    from collections import Counter
    counts = Counter(e["category"] for e in ek_entries)
    fig, ax = plt.subplots(figsize=(7, 5))
    cats = list(counts.keys())
    vals = [counts[c] for c in cats]
    colors = [CATEGORY_COLORS.get(c, "#999") for c in cats]
    ax.bar(cats, vals, color=colors)
    ax.set_ylabel("Count")
    ax.set_title("Knowledge entry category distribution (n=41)")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
