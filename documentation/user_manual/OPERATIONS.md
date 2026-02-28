## Operations Log (latest updates)

### Highlights
- Added Graph RAG upgrades: hybrid TF‑IDF + optional embeddings, structured filter parsing, schema grounding, fraud-count tables per query, side-by-side context + data slices, confidence/snippet scores, guardrails/logging.
- Sidebar tooling: Rebuild KB, Clean DB, Rebuild Graph (now scans docs/, data/uploads/, DB tables; writes manifest/corpus and graph store), ML pipeline image, agent workflow mermaid/JPG preview with legend.
- Upload tab: saves CSVs to `data/uploads/`, ingests to DB, auto-loads existing DB tables, multi-SQL file executor (creates tables/inserts), graph base viz.
- ML Dashboard: supports selecting existing tables, label coercion, feature selection, SMOTE, thresholds, split sliders, cost-based threshold, persistence/load, data checks, logging, dataset download.
- SQL RAG: uses uploaded tables + schemas, improved caching, fraud risk scoring, training dataset generation, scrollable SQL improvements, sample questions.
- Graph RAG tab: selectable grounding table, applied filters display, filtered data slice shown, regression log, sample questions.
- Model Comparison: selectable table, scalar metrics only, ROC, PDF export; avoids Arrow errors.
- ERD tab: multi-select tables, generates mermaid + PNG preview/download; PK/FK inferred via SQLite PRAGMAs.
- Agent workflow: sidebar mermaid/JPG preview (from session or `langgraph_agent_map_diagram.mermaid`), legend for abbreviations, files saved under `data/generated/`.

### Known fixed issues
- Resolved repeated `Path` NameError in ERD generation by using `pathlib.Path` and robust PNG path resolution; added fallback generation in UI.
- SQL/Graph tabs no longer stop when no upload; they warn instead. Model Comparison handles non-`isFraud` labels.
- ERD PNG double-suffix handled by candidate lookup.

### Files/paths to note
- Graph: `data/graph/graph_manifest.json`, `graph_corpus.txt`, `graph_store.json`, `graph_tfidf.joblib`.
- ML artifacts: `data/ml`, `data/ml/models`, `data/generated/agent_workflow*.jpg`, `data/generated/langgraph_agent_map_diagram.mermaid`.
- ERD: `data/erd/erd_selected.mmd`, `erd_selected.png`.
- Logs: `logs/graph_rag.log`, `logs/rebuild_kb.log`.

### Testing
- `python -m py_compile app/dashboard.py ml/compare_models.py rag_sql/erd_generator.py` (passes).

