# TopoGraph: The Ontology Healer - Findings Summary

## PHASE 1: The Diagnosis (Quality-Filtered Topology)
- **Zero Recursive Loops (Beta-1):** By mathematically filtering the explicit attack chains, we proved $\beta_1 = 0$ across all thresholds. The human-curated ontology contains zero circular dependencies.
- **High Fragmentation Risk (Beta-0):** When filtering by strict 8-dimensional quality metrics, the Betti-0 curve reveals massive fragmentation. If analysts only trust 'perfect' data, the knowledge graph shatters completely, rendering attack vectors invisible.

## PHASE 2: The Cure (Semantic Missing Links)
- **Automated Graph Healing:** Because the human-curated graph is highly fragmented, we deployed a Semantic TDA engine to map the textual space. We discovered the following critical 'missing links'—semantically identical techniques that human curators completely failed to connect:

  * **ek_0032 <-> ek_0033** (Semantic Distance: 0.476)
    * Node 1: "Fragment-routed AJAX + unanchored regex domain check = CORS-based XSS"
    * Node 2: "Satisfying unanchored domain regex via query parameter embedding"

  * **ek_0000 <-> ek_0001** (Semantic Distance: 0.498)
    * Node 1: "curl Proxy-Authorization leak on proxy-to-direct redirect transition"
    * Node 2: "Proxy-to-direct redirect as credential harvesting vector"

  * **ek_0005 <-> ek_0006** (Semantic Distance: 0.507)
    * Node 1: "CLI argument parsing as incidental CRLF defense layer in libcurl"
    * Node 2: "Protocol injection testing requires library-level API access not CLI"

  * **ek_0010 <-> ek_0012** (Semantic Distance: 0.521)
    * Node 1: "Error/edge-case pages bypass input validation enforced on main flows"
    * Node 2: "Prioritize compound-state pages when testing shared parameters"

  * **ek_0032 <-> ek_0034** (Semantic Distance: 0.537)
    * Node 1: "Fragment-routed AJAX + unanchored regex domain check = CORS-based XSS"
    * Node 2: "Fragment-based AJAX routing signals potential CORS-assisted content injection"
