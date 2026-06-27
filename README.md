# TopoGraph: Topological Knowledge Graph Analytics

A working pipeline for the **Knowledge Graph Analytics and Discovery** hackathon track,
built on the three provided dataset files (`experiential_knowledge_41.json`,
`quality_metrics.json`, `cross_references.json`).

## What it does

1. **Loads** the dataset (handles a malformed trailing comma in
   `experiential_knowledge_41.json` automatically).
2. **Builds a directed knowledge graph** — 41 nodes, edges from declared
   `suggested_chain` cross-references.
3. **Standard graph analytics** — centrality, longest chains, category
   bridging, fragmentation / connected components.
4. **Topological Data Analysis** — since the declared-edge graph is
   *provably a pure forest with zero cycles* (verified, not assumed), we
   build a second, continuous metric space from each entry's text
   (TF-IDF + cosine distance) and run persistent homology on that space
   with `gudhi`. This is where TDA contributes something graph algorithms
   structurally cannot: β₀/β₁ Betti curves, a persistence diagram, and a
   list of "missing link" candidates — entry pairs that are semantically
   close but have no declared cross-reference edge.
5. **Visualizes** everything and writes a findings report.

## Run it

```bash
pip install networkx gudhi matplotlib numpy scipy scikit-learn
python3 main.py
```

Outputs land in `outputs/`:
- `01_network_graph.png` — the declared cross-reference graph, colored by category
- `02_centrality.png` — top entries by in/out-degree
- `03_category_distribution.png` — category counts
- `04_persistence_diagram.png` — H₀/H₁ persistence diagram (semantic space)
- `05_betti_curves.png` — β₀/β₁ over the filtration
- `findings_summary.md` — full write-up of results, ready to paste into a
  hackathon report/slide deck

## Key findings (already run on the real data — see findings_summary.md)

- Of 85 total cross-reference edges, only 14 fall inside the 41-entry
  sample; 17 of 41 nodes (41%) are completely isolated within the sample.
- The declared-edge graph is a DAG with **zero cycles** — so β₁ from raw
  cross-references alone is trivially 0. This is itself a reportable
  finding, not a limitation to hide.
- Running persistent homology on a TF-IDF semantic space instead reveals
  strong β₀ fragmentation (technique families merge gradually, not in a
  few obvious clusters) and weak/marginal β₁ loop structure — reported
  honestly rather than oversold.
- 5 concrete "missing link" candidates are surfaced: pairs of entries that
  are textually very similar but have no curator-assigned cross-reference.

## File structure

```
data_loader.py      # robust JSON loading for all 3 files
graph_builder.py     # builds the networkx DiGraph + structural summary
graph_analytics.py   # centrality, longest chains, category bridges, fragmentation
tda_analysis.py      # TF-IDF distance matrix, persistent homology, missing-link detection
visualize.py         # all matplotlib figure generation
main.py              # orchestrates the full pipeline, writes findings_summary.md
data/                # the 3 provided JSON files
outputs/             # generated figures + findings_summary.md
```

## Extending this for the demo

- Swap the `RipsComplex` for a `WitnessComplex` if the node count grows
  past a few hundred (full topology extends to ek_0253).
- Combine the semantic distance with a *graph-aware* distance (e.g.
  shortest-path on declared edges, capped) into a weighted fusion metric —
  currently the two analyses are kept separate and cross-checked, which is
  more honest but a fused metric could be a nice "v2" extension to mention
  in a presentation.
- A live demo could let judges type a new candidate entry's text and see
  which existing cluster it would attach to and at what semantic distance.
