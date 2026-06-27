import os
import sys
from collections import Counter

import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from flask import Flask, render_template

# ==========================================================
# PATH CONFIGURATION
# ==========================================================

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(BASE_DIR, "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# ==========================================================
# IMPORT PROJECT MODULES
# ==========================================================

from data_loader import (
    load_experiential_knowledge,
    load_quality_metrics,
    load_cross_references
)

from graph_builder import (
    build_knowledge_graph,
    graph_summary
)

from graph_analytics import (
    fragmentation_report,
    centrality_report
)

from tda_analysis import (
    build_text_corpus,
    semantic_distance_matrix,
    compute_persistence,
    betti_curve
)

# ==========================================================
# FLASK APP
# ==========================================================

app = Flask(__name__)

# ==========================================================
# NETWORK GRAPH
# ==========================================================

def generate_network_graph(G):

    pos = nx.spring_layout(G, seed=42, k=0.9)

    edge_x = []
    edge_y = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        hoverinfo="none",
        line=dict(width=1, color="#999999")
    )

    node_x = []
    node_y = []
    node_text = []
    node_colors = []
    node_sizes = []

    for node in G.nodes():

        x, y = pos[node]

        node_x.append(x)
        node_y.append(y)

        degree = G.degree(node)

        node_sizes.append(18 + degree * 2)
        node_colors.append(degree)

        node_text.append(
            f"<b>{node}</b><br>"
            f"Title: {G.nodes[node]['title']}<br>"
            f"Category: {G.nodes[node]['category']}<br>"
            f"Degree: {degree}<br>"
            f"Confidence: {G.nodes[node]['confidence']}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        text=node_text,

        marker=dict(
            size=node_sizes,
            color=node_colors,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(
                title="Degree",
                thickness=12
            ),
            line=dict(
                width=2,
                color="black"
            )
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace])

    fig.update_layout(
        title="Knowledge Graph Network",
        height=650,
        margin=dict(l=5, r=5, t=40, b=5),
        showlegend=False,
        hovermode="closest",

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),

        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        )
    )

    return fig.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    )

# ==========================================================
# CENTRALITY GRAPH (FIXED MULTI-LINE LABELS & FILL SPACE)
# ==========================================================

def generate_centrality_chart(rows, G):

    labels = []
    for r in rows:
        node_id = r["id"]
        category = G.nodes[node_id]['category']
        wrapped_category = category.replace("_", "<br>")
        labels.append(f"<span style='font-size:8px;'><b>&nbsp;{node_id}&nbsp;</b><br>{wrapped_category}</span>")

    out_degree = [r["out_degree"] for r in rows]
    in_degree = [r["in_degree"] for r in rows]

    fig = go.Figure()

    fig.add_trace(go.Bar(x=labels, y=out_degree, name="Out Degree", marker_color="#E07A5F"))
    fig.add_trace(go.Bar(x=labels, y=in_degree, name="In Degree", marker_color="#3D405B"))

    fig.update_layout(
        # FIX: y=0.88 moves the title down so it sits cleanly with breathing room above it
        title=dict(
            text="Top Entries by Connectivity",
            x=0.03,
            xanchor="left",
            y=0.88
        ),
        barmode="group",
        autosize=True,
        bargap=0.4, 
        
        # Kept the padding stable
        margin=dict(l=50, r=20, t=80, b=120),

        xaxis=dict(
            type="category",
            tickangle=0,            
            automargin=True,        
            tickfont=dict(size=8)   
        ),

        yaxis_title="Degree",

        legend=dict(
            orientation="v",         
            y=0.95,                  
            x=0.98,                  
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255, 255, 255, 0.8)", 
            bordercolor="rgba(0, 0, 0, 0.1)",
            borderwidth=1
        )
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)
# ==========================================================
# CATEGORY DISTRIBUTION GRAPH (FILL SPACE)
# ==========================================================

def generate_category_chart(G):

    categories = [G.nodes[n]["category"] for n in G.nodes()]
    counts = Counter(categories)

    fig = px.bar(
        x=list(counts.keys()),
        y=list(counts.values()),
        labels={
            "x": "Category",
            "y": "Count"
        },
        title="Knowledge Category Distribution"
    )

    fig.update_layout(
        height=260,
        margin=dict(l=5, r=5, t=60, b=40),

        title=dict(
            text="Knowledge Category Distribution",
            x=0.02,
            xanchor="left",
            y=0.9
        ),

        xaxis=dict(
            tickangle=-20
        )
    )

    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={"displayModeBar": "hover"}
    )
# ==========================================================
# PERSISTENCE DIAGRAM (FIXED DOUBLE ZERO COLLISION)
# ==========================================================

def generate_persistence_diagram(persistence):

    fig = go.Figure()

    colors = {0: "blue", 1: "red", 2: "green"}
    finite_max = 0

    for d, (birth, death) in persistence:
        if death != float("inf"):
            finite_max = max(finite_max, death)

    plot_max = max(finite_max * 1.1, 0.1)

    for dim in [0, 1, 2]:
        births = []
        deaths = []

        for d, (b, death) in persistence:
            if d == dim:
                births.append(b)
                if death == float("inf"):
                    deaths.append(plot_max)
                else:
                    deaths.append(death)

        fig.add_trace(
            go.Scatter(
                x=births,
                y=deaths,
                mode="markers",
                name=f"H{dim}",
                marker=dict(size=8, color=colors[dim])
            )
        )

    fig.add_shape(
        type="line", x0=0, y0=0, x1=plot_max, y1=plot_max,
        line=dict(dash="dash")
    )

    fig.update_layout(
        title="Persistence Diagram",
        autosize=True,
        margin=dict(l=50, r=20, t=50, b=50),
        xaxis_title="Birth",
        yaxis_title="Death",
        xaxis=dict(automargin=True),
        # Explicit ticks missing the 0 index value prevents corner zero overlapping
        yaxis=dict(
        automargin=True,
        tickvals=[0.2, 0.4, 0.6, 0.8, 1.0]
        )
    )

    return fig.to_html(
        full_html=False,
        include_plotlyjs=False
    )

# ==========================================================
# BETTI CURVES (FIXED DOUBLE ZERO COLLISION)
# ==========================================================

def generate_betti_curves(betti_data):

    fig = go.Figure()
    colors = {0: "blue", 1: "red", 2: "green"}

    for dim, series in betti_data.items():
        x = [p[0] for p in series]
        y = [p[1] for p in series]

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name=f"β{dim}",
                line=dict(width=3, color=colors.get(dim, "black"))
            )
        )

    fig.update_layout(
        title="Betti Curves",
        autosize=True,
        margin=dict(l=50, r=20, t=50, b=50),
        xaxis_title="Filtration Scale",
        yaxis_title="Betti Number",
        xaxis=dict(automargin=True),
        # Clrears out the zero value from rendering on the vertical boundary
        yaxis=dict(
            automargin=True,
            tickvals=[10, 20, 30, 40]
        )
    )

    return fig.to_html(
        full_html=False,
        include_plotlyjs=False
    )

# ==========================================================
# DASHBOARD ROUTE
# ==========================================================

@app.route("/")
def index():

    DATA_DIR = os.path.join(BASE_DIR, "data")

    ek = load_experiential_knowledge(
        os.path.join(DATA_DIR, "experiential_knowledge_41.json")
    )
    _, quality_data, _ = load_quality_metrics(
        os.path.join(DATA_DIR, "quality_metrics.json")
    )
    ref_edges, _ = load_cross_references(
        os.path.join(DATA_DIR, "cross_references.json")
    )

    G = build_knowledge_graph(ek, quality_data, ref_edges)

    summary = graph_summary(G)
    frag = fragmentation_report(G)
    central_nodes = centrality_report(G, top_k=10)

    corpus = build_text_corpus(ek)
    distance_matrix, _, _ = semantic_distance_matrix(corpus)

    simplex_tree, persistence = compute_persistence(
        distance_matrix, max_edge_length=1.0, max_dimension=2
    )

    betti_data = betti_curve(
        simplex_tree, max_dim=2, n_steps=60, max_eps=1.0
    )

    dashboard_data = {
        "n_nodes": summary["n_nodes"],
        "n_edges": summary["n_edges"],
        "components": frag["n_components"],
        "isolated": frag["n_isolated_nodes"],
        "density": round(summary["density"], 3),
        "dag": "Yes" if summary["is_dag"] else "No"
    }

    return render_template(
        "index.html",
        data=dashboard_data,
        network_graph=generate_network_graph(G),
        # Passed the Graph object down to query structural categories directly
        centrality_graph=generate_centrality_chart(central_nodes, G),
        category_graph=generate_category_chart(G),
        persistence_graph=generate_persistence_diagram(persistence),
        betti_graph=generate_betti_curves(betti_data)
    )


if __name__ == "__main__":
    print("\nStarting TopoGraph Dashboard...")
    app.run(debug=True, port=5000)
