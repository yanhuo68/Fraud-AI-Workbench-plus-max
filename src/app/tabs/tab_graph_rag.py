import streamlit as st
from pathlib import Path
import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

from src.rag_sql.graph_rag import query_graph
from src.app.utils import parse_structured_filters, rebuild_graph_base, visualize_graph_base
from src.agents.llm_router import get_available_llms, init_llm

def render_graph_rag_tab():
    st.header("🧭 Graph RAG")
    st.caption("Ask semantic questions over the graph base built from docs/ and uploaded CSV previews with a lightweight GraphRAG pipeline.")
    
    # Friendly info if no tables uploaded yet  
    if "uploaded_tables" not in st.session_state or not st.session_state.uploaded_tables:
        st.info("""
        💡 **Tip**: Graph RAG works with your documentation, but uploading CSV files 
        enables richer graph connections and data-grounded answers.
        
        👈 Go to the **Upload Data** tab to upload your fraud detection dataset.
        """)
        
    # Check if Graph Knowledge Base exists
    graph_corpus_path = Path("data/graph/graph_corpus.txt")
    if not graph_corpus_path.exists():
        st.warning("🧭 No Graph Knowledge Base found")
        st.info("""
        **To use Graph RAG:**
        1. 👈 Go to the **Upload Data** tab
        2. Click the **"Rebuild Graph Base"** button in the sidebar
        
        
        This will process your documents and tables to build the knowledge graph.
        """)
        return

    import random

    sample_graph_questions = [
        "Which uploaded files mention fraud or risk rules?",
        "Summarize key tables and their purposes from the graph base.",
        "Which documents talk about model training or evaluation?",
        "What columns look important for fraud detection in the uploaded data?",
        "List any references to threshold tuning or cost tradeoffs.",
        "How are high-risk transactions defined in the documentation?",
        "What are the main entities related to 'Merchant' in the graph?",
        "Show connections between 'User' and 'Device' entities.",
        "Which rules trigger an automatic account suspension?",
        "Find documents discussing 'compliance' or 'AML'.",
        "What is the relationship between 'Transaction' and 'Location'?",
        "List all identified fraud patterns mentioned in the text.",
        "Who are the key stakeholders for fraud alerts according to the docs?",
        "What distinct data sources feed into the fraud model?",
        "How is 'User Velocity' calculated or described?",
        "Are there any mentioned known false positive scenarios?",
        "What does the graph say about 'Identity Theft'?",
        "Summarize the 'Chargeback' handling process.",
        "Which features are considered deprecated or legacy?",
        "What is the retention policy for fraud data?",
    ]

    if "graph_current_samples" not in st.session_state:
        st.session_state["graph_current_samples"] = random.sample(sample_graph_questions, 5)

    st.markdown("Pick a sample or enter your own question:")

    col_pick, col_refresh = st.columns([8, 1])
    with col_pick:
        picked_graph_q = st.selectbox(
            "Sample graph questions", 
            st.session_state["graph_current_samples"], 
            index=0, 
            key="graph_sample_picker"
        )
    with col_refresh:
        st.write("") # padding
        st.write("") # padding
        if st.button("🔄", help="Refresh sample questions", key="btn_refresh_graph_samples", use_container_width=True):
             st.session_state["graph_current_samples"] = random.sample(sample_graph_questions, 5)
             st.rerun()

    graph_question = st.text_area(
        "Ask the graph base",
        value=picked_graph_q,
        placeholder="e.g., What do the docs say about fraud features and label definitions?",
    )

    col_llm, col_llm_ref = st.columns([4, 1])
    with col_llm:
        graph_llm = st.selectbox(
            "LLM for Graph answers",
            st.session_state.get("available_llms", []),
            key="graph_llm_select",
        )
    with col_llm_ref:
        st.write("") # padding
        if st.button("🔄 Scan", key="btn_scan_graph_llm", help="Scan for local LLMs (Ollama/LM Studio)", use_container_width=True):
            with st.spinner("Scanning..."):
                st.session_state["available_llms"] = get_available_llms(include_local=True)
                st.rerun()

    grounding_table = None
    if st.session_state.get("uploaded_tables"):
        grounding_table = st.selectbox(
            "Table to ground numeric answers",
            list(st.session_state.uploaded_tables.keys()),
            key="graph_ground_table",
        )

    # Graph Visualization Section
    st.markdown("---")
    st.subheader("📊 Knowledge Graph Visualization")
    
    with st.expander("ℹ️ About the Knowledge Graph", expanded=False):
        st.markdown("""
**What is this graph?**  
This visualization shows the structure of the knowledge graph built from your documents and data.  

**Nodes** represent:
- 🔷 **Entities**: Key concepts, tables, columns, fraud rules
- 📄 **Documents**: Source files from your knowledge base

**Edges** represent:
- **Relationships**: Connections between entities (e.g., "transactions" → "fraud_flag" column)
- **References**: Which documents mention which entities

**Use this to:**
- Understand what knowledge is indexed
- Identify central concepts (high-degree nodes)
- Discover related entities for better questions
        """)
    
    if st.button("🎨 Visualize Knowledge Graph", key="btn_visualize_graph", use_container_width=True):
        visualize_graph_base(st, grounding_table=grounding_table)

    corpus_path = Path("data/graph/graph_corpus.txt")
    manifest_path = Path("data/graph/graph_manifest.json")

    col_left, col_right = st.columns(2)

    if col_left.button("🧠 Graph ask", use_container_width=True):
        counts_container = col_right.container()  # render counts to the right for side-by-side
        counts_container.empty()
        if not graph_question.strip():
            st.warning("Please enter a question.")
        elif not corpus_path.exists():
            st.error("Graph corpus not found. Rebuild the graph from the sidebar first.")
        else:
            # Ensure graph store/index exists; if missing, build it
            try:
                graph_store_path = Path("data/graph/graph_store.json")
                tfidf_path = Path("data/graph/graph_tfidf.joblib")
                if not graph_store_path.exists() or not tfidf_path.exists():
                    rebuild_graph_base(log_handler=lambda msg: st.warning(msg))

                retrieval = query_graph(graph_question, top_k=8, out_dir=Path("data/graph"))
                context_text = retrieval["context"]
            except Exception as e:
                st.error(f"Graph query failed: {e}")
                context_text = ""

            # If we have an uploaded dataset, try to compute fraud counts directly (with simple question-based filters)
            data_counts_block = ""
            if grounding_table and "table_dataframes" in st.session_state and grounding_table in st.session_state.table_dataframes:
                df_src = st.session_state.table_dataframes[grounding_table]
            elif "uploaded_df" in st.session_state:
                df_src = st.session_state.uploaded_df
            else:
                df_src = None

            if df_src is not None:
                # Basic filters from question (e.g., payment method)
                df_filtered = df_src.copy()
                filters = parse_structured_filters(graph_question)
                if not filters:
                    # heuristic: debit card
                    q_lower = graph_question.lower()
                    if "debit card" in q_lower:
                        filters = [("payment", "debit")]
                # Schema-based grounding: map synonyms using schema markdown
                schema_cols = []
                if st.session_state.get("uploaded_tables"):
                    try:
                        schema_path = Path(list(st.session_state.uploaded_tables.values())[0])
                        if schema_path.exists():
                            for line in schema_path.read_text().splitlines():
                                if line.startswith("|") and not line.startswith("|-"):
                                    parts = [p.strip() for p in line.strip("|").split("|")]
                                    if len(parts) >= 2 and parts[0].lower() != "column":
                                        schema_cols.append(parts[0])
                    except Exception:
                        schema_cols = []
                synonym_map = {
                    "debit card": "payment_method",
                    "credit card": "payment_method",
                    "card": "payment_method",
                    "amount": "amount",
                    "payment": "payment_method",
                    "payment method": "payment_method",
                }
                grounded_filters = []
                for col_hint, val in filters:
                    mapped = synonym_map.get(col_hint.lower(), col_hint)
                    chosen = None
                    for col in schema_cols:
                        if mapped.lower().replace(" ", "") in col.lower().replace(" ", ""):
                            chosen = col
                            break
                    grounded_filters.append((chosen or col_hint, val))

                for col_hint, val in grounded_filters:
                    for col in df_filtered.columns:
                        if col_hint.lower().replace(" ", "") in col.lower().replace(" ", ""):
                            df_filtered = df_filtered[df_filtered[col].astype(str).str.lower().str.contains(val.lower())]
                            break

                fraud_cols = [c for c in df_filtered.columns if "fraud" in c.lower() or "label" in c.lower()]
                if fraud_cols:
                    label_col = fraud_cols[0]
                    series = df_filtered[label_col]
                    try:
                        mapped = series.map({"yes": 1, "true": 1, "y": 1, "fraud": 1, "fraudulent": 1,
                                             "no": 0, "false": 0, "n": 0, "legit": 0, "legitimate": 0}).fillna(series)
                    except Exception:
                        mapped = series
                    try:
                        mapped_num = pd.to_numeric(mapped, errors="coerce")
                        counts = mapped_num.value_counts(dropna=True).rename_axis(label_col).reset_index(name="count")
                        total = counts["count"].sum()
                        counts["ratio"] = counts["count"] / total if total else 0
                        counts_container.markdown(f"**Dataset fraud counts (column `{label_col}`)**")
                        counts_container.dataframe(counts)
                        counts_container.markdown(
                            """
**How to read this table**
- `label_col`: value of the fraud/label column (1=fraud/positive, 0=non-fraud/negative; other values if present).
- `count`: number of rows in the filtered data slice with that label value.
- `ratio`: count divided by the total filtered rows (share of each label value).
"""
                        )
                        fraud_count = int(counts.loc[counts[label_col] == 1, "count"].sum())
                        data_counts_block = f"Data-derived fraud count from `{label_col}` on filtered rows: {fraud_count} / {total} rows."
                    except Exception:
                        counts_container.empty()
                else:
                    counts_container.info("No fraud/label column detected to compute counts for this question. Showing filtered sample below.")

            if context_text:
                llm = init_llm(graph_llm)
                prompt = f"""
You are a graph-based QA assistant. The user asked:
{graph_question}

Here is graph-derived context (snippets + connected entities):
{context_text}

Data summary (if available):
{data_counts_block or 'n/a'}

- Ground your answer in this context.
- If context is weak or missing, say so and suggest what to check next.
- Be concise and actionable for fraud analytics.
"""
                with st.spinner("Querying graph base..."):
                    response = llm.invoke(prompt)
                col_left.subheader("🧠 Answer")
                col_left.markdown(response.content if hasattr(response, "content") else str(response))

                col_left.markdown("**Context used**")
                col_left.markdown(f"<pre>{context_text}</pre>", unsafe_allow_html=True)

                # Paths (why) if available
                paths = retrieval.get("paths", [])
                if paths:
                    col_left.markdown("**Why these snippets (entity → snippet)**")
                    for p in paths[:10]:
                        col_left.markdown(f"- {p}")
                # Show retrieved snippets with scores
                top_snippets = retrieval.get("top_snippets", [])
                if top_snippets:
                    col_left.markdown("**Top retrieved snippets (score)**")
                    for sn in top_snippets:
                        col_left.markdown(f"- ({sn.get('score', 0):.4f}) [{sn.get('source','')}] {sn.get('text','')}")
                    confidence = max(sn.get("score", 0) for sn in top_snippets)
                    if confidence < 0.1:
                        col_left.warning("Low-confidence context (scores below 0.1); answer may be weak.")
                    else:
                        col_left.info(f"Confidence (max snippet score): {confidence:.4f}")
                    col_left.markdown(
                        """
**How to read these snippets**
- Each line: `(similarity score) [source] snippet text`.
- Higher scores mean closer match to your question; lower scores (< 0.1) indicate weak/tenuous matches.
- Sources reflect the originating file/section; use them to verify grounding.
- If top scores are low, consider rephrasing or adding more specifics to your question.
"""
                    )

            if manifest_path.exists():
                try:
                    manifest = json.loads(manifest_path.read_text())
                    col_right.markdown("**Graph entries (from manifest)**")
                    col_right.json(manifest.get("entries", []))
                except Exception as e:
                    col_right.info(f"Could not read manifest: {e}")

            # Show filtered data slice side-by-side
            if "uploaded_df" in st.session_state:
                try:
                    col_right.markdown("**Filtered data slice**")
                    col_right.dataframe(df_filtered.head(50))
                    col_right.markdown(
                        """
**Filtered slice legend**
- Rows shown are the first 50 after applying detected filters from your question.
- Use this to confirm which rows/values were used to compute the counts above.
"""
                    )
                except Exception:
                    pass

            # Applied filters log
            if df_src is not None:
                applied_filters = grounded_filters if 'grounded_filters' in locals() else filters if 'filters' in locals() else []
                if applied_filters:
                    col_right.markdown("**Applied filters**")
                    for fcol, fval in applied_filters:
                        col_right.markdown(f"- {fcol}: contains '{fval}'")

            # Log Q/A for regression
            try:
                log_path = Path("logs/graph_rag.log")
                log_path.parent.mkdir(parents=True, exist_ok=True)
                answer_text = response.content if context_text else "no answer"
                log_path.write_text(
                    log_path.read_text() + f"\n\nQ: {graph_question}\nFilters: {applied_filters}\nContext: {context_text[:1000]}\nA: {answer_text[:1000]}\n",
                    encoding="utf-8"
                )
            except Exception:
                pass
