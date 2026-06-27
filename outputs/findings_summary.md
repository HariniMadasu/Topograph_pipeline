# TopoGraph: Findings Summary

## 1. Dataset structure

- 41 knowledge entries loaded (ek_0000-ek_0040).
- Quality metrics: avg_derivability=0.443, avg_condition_richness=0.771, avg_abstraction_quality=0.284.
- Cross-reference file contains 85 total directed edges, but only **14** fall inside our 41-node sample (71 point outside it, toward the fuller ek_0041-ek_0253 topology we don't have content for).

## 2. Standard graph analytics

- The declared cross-reference subgraph is a **DAG** with density 0.0085.
- **17 of 41 nodes (41%) are completely isolated** within this sample - they only connect to entries outside ek_0000-ek_0040.
- The remaining nodes split into **27 weakly-connected components**, the largest being only size 3.
- **Zero cycles exist** in the declared-edge graph (it's a pure forest) - so beta_1 computed directly from cross-references is trivially 0. This is itself a finding: curators link entries as linear chains, never as feedback loops.

### Category transitions (what feeds into what)
- signal_interpretation -> chain_pattern: 3
- tactical_priority -> chain_pattern: 2
- chain_pattern -> bypass_technique: 2
- signal_interpretation -> bypass_technique: 1
- tactical_priority -> pitfall: 1
- bypass_technique -> pitfall: 1
- bypass_technique -> signal_interpretation: 1
- chain_pattern -> chain_pattern: 1
- tactical_priority -> signal_interpretation: 1
- bypass_technique -> chain_pattern: 1

### Longest declared chains
- ek_0002 (Tiered URL decode rejection flags leave ) -> ek_0003 (location.pathname double-slash protocol-)
- ek_0012 (Prioritize compound-state pages when tes) -> ek_0014 (Plaintext tag destroys page rendering ma)
- ek_0013 (HTML blacklist bypass via deprecated and) -> ek_0014 (Plaintext tag destroys page rendering ma)
- ek_0016 (Encoder/decoder asymmetry as vulnerabili) -> ek_0017 (Multiplier overflow to zero silently con)
- ek_0018 (Audit protocol spec mandatory limits as ) -> ek_0019 (Server-side data fetch + content-type mi)

## 3. TDA on the semantic (TF-IDF) distance space

Because the declared-edge graph can't have loops by construction, we built a second, continuous metric space from entry text (title + core knowledge + abstracted pattern + pitfalls) and ran persistent homology on it. This is where TDA adds value the raw graph cannot, but the honest result is mixed - two different findings at two different strengths:

- **beta_0 (fragmentation) is the strong signal**: components merge gradually across almost the full distance range (0 to ~0.87), meaning entries form a continuum of loosely related technique families rather than a few tight, obvious clusters.
- **beta_1 (loops) is present but weak**: 6 candidate loops were found, but the longest only persists for 0.070 distance units (most just ~0.02-0.07) against the diagonal - these are marginal, not the kind of strongly-persistent loop you'd confidently call a structural feature. Read this as 'a little redundancy among related techniques' rather than 'major hidden cyclic structure'. We report it as a transparent negative-ish finding rather than oversell it - real TDA results on small, sparse-vocabulary text corpora often look like this.
- **5 'missing link' candidates**: entry pairs that are semantically very close but have NO declared cross-reference edge at all. These are concrete, checkable suggestions for curators to review:

  - ek_0032 <-> ek_0033 (distance=0.476): "Fragment-routed AJAX + unanchored regex domai" <-> "Satisfying unanchored domain regex via query "
  - ek_0000 <-> ek_0001 (distance=0.498): "curl Proxy-Authorization leak on proxy-to-dir" <-> "Proxy-to-direct redirect as credential harves"
  - ek_0005 <-> ek_0006 (distance=0.507): "CLI argument parsing as incidental CRLF defen" <-> "Protocol injection testing requires library-l"
  - ek_0010 <-> ek_0012 (distance=0.521): "Error/edge-case pages bypass input validation" <-> "Prioritize compound-state pages when testing "
  - ek_0032 <-> ek_0034 (distance=0.537): "Fragment-routed AJAX + unanchored regex domai" <-> "Fragment-based AJAX routing signals potential"