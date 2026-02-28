import streamlit as st
import difflib
from src.agents.llm_router import get_available_llms
from src.rag_sql.knowledge_base import answer_kb_question, compare_rag_vs_no_rag
from src.rag_sql.rag_inspector import render_rag_context_inspector

def render_kb_rag_tab():
    st.header("📚 Knowledge-Base Chat")
    
    # Check if knowledge base is available (optional check)
    # KB RAG can work without uploaded tables, so we just show an info message if no tables
    if "uploaded_tables" not in st.session_state or not st.session_state.uploaded_tables:
        st.info("""
        💡 **Tip**: While you can use the Knowledge Base without uploaded data, 
        uploading CSV files will enable schema-aware questions and data-grounded answers.
        
        👈 Go to the **Upload Data** tab to upload your fraud detection dataset.
        """)
    
    # Check if Knowledge Base index exists
    from pathlib import Path
    kb_index_path = Path("data/kb/faiss_index")
    if not kb_index_path.exists():
        st.warning("📚 No Knowledge Base found")
        st.info("""
        **To use the Knowledge Base:**
        1. 👈 Go to the **Upload Data** tab
        2. Click the **"Rebuild Knowledge Base"** button in the sidebar
        
        This will index your documents (from `docs/`) and create the vector store.
        """)
        # We don't stop here because users might want to see the UI, but querying will fail anyway.
        # Actually, let's stop to prevent confusion and errors.
        return

    import random
    
    # Expanded static pool of KB questions
    ALL_KB_SAMPLES = [
        "What criteria distinguish fraud vs flagged-but-not-fraud transactions?",
        "Which multi-hop transaction chains are most common and how do they show up?",
        "Which features should we prioritize for early fraud detection?",
        "Which rule-based signals best complement the ML model?",
        "When and how should we trigger a model retrain given drift?",
        "What are the red flags for high-value transfer sequences?",
        "How should we handle potential false positives in the alert queue?",
        "What is the recommended workflow for investigating a new fraud ring?",
        "Explain the difference between 'layering' and 'integration' in money laundering.",
        "What are the minimal data requirements for the fraud model?",
        "How do we interpret a high 'feature_x' value in local explanations?",
        "What compliance regulations (AML/KYC) are most relevant here?",
        "How can we detect smurfing or structuring patterns?",
        "What is the role of graph analysis in detecting synthetic identities?",
        "Describe the 'velocity' features used in the current model.",
        "How should analysts document their decisions for audit trails?",
        "What are common indicators of account takeover (ATO)?",
        "How does the system handle cross-border transaction anomalies?",
        "What thresholds are currently set for 'high risk' alerts?",
        "How can we differentiate between merchant fraud and cardholder fraud?",
    ]

    # Initialize session state for samples if not present
    if "kb_current_samples" not in st.session_state:
        st.session_state["kb_current_samples"] = random.sample(ALL_KB_SAMPLES, 5)

    st.markdown("Pick a sample or ask your own question:")
    
    # Layout for picker + refresh button
    col_pick, col_refresh = st.columns([8, 1])
    with col_pick:
        kb_picked = st.selectbox(
            "Sample KB questions", 
            st.session_state["kb_current_samples"], 
            index=0, 
            key="kb_sample_picker"
        )
    with col_refresh:
        st.write("") # padding
        st.write("") # padding
        if st.button("🔄", help="Refresh sample questions", key="btn_refresh_kb_samples", use_container_width=True):
            st.session_state["kb_current_samples"] = random.sample(ALL_KB_SAMPLES, 5)
            st.rerun()

    kb_question = st.text_area(
        "Ask the fraud knowledge-base",
        value=kb_picked,
        placeholder="e.g., Why are transfer + cash-out chains considered high risk?",
    )

    # Choose LLM for KB
    col_llm, col_llm_ref = st.columns([4, 1])
    with col_llm:
        kb_llm = st.selectbox(
            "LLM for KB answers",
            st.session_state.get("available_llms", []),
            key="kb_llm_select",
        )
    with col_llm_ref:
        st.write("") # padding
        if st.button("🔄 Scan", key="btn_scan_kb_llm", help="Scan for local LLMs (Ollama/LM Studio)", use_container_width=True):
            with st.spinner("Scanning..."):
                st.session_state["available_llms"] = get_available_llms(include_local=True)
                st.rerun()

    if st.button("📚 Ask KB", key="kb_ask_button", use_container_width=True):
        if not kb_question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner("Querying knowledge-base..."):
                    result = answer_kb_question(
                        kb_question,
                        llm_id=kb_llm,
                        return_context=True,
                        k=4,
                    )
    
                # Store for later debugging (if desired)
                st.session_state["kb_last_result"] = result
    
                st.subheader("🧠 Answer")
                st.markdown(result["answer"])
    
                # RAG context inspector
                render_rag_context_inspector(result)
            except Exception as e:
                st.error(f"Failed to get answer from Knowledge Base: {e}")

    # Optional: show last result if user revisits tab
    elif "kb_last_result" in st.session_state:
        st.info("Showing last KB answer and context.")
        st.subheader("🧠 Answer")
        st.markdown(st.session_state["kb_last_result"]["answer"])
        render_rag_context_inspector(st.session_state["kb_last_result"])

    st.markdown("---")
    st.subheader("🆚 Compare RAG vs No-RAG")

    compare_button = st.button("Run Comparison (RAG vs No-RAG)", use_container_width=True)

    if compare_button:
        if not kb_question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner("Running comparison..."):
                    cmp = compare_rag_vs_no_rag(
                        question=kb_question,
                        llm_id=kb_llm,
                        k=4,
                    )
    
                # SIDE-BY-SIDE VIEW
                col1, col2 = st.columns(2)
    
                with col1:
                    st.markdown("### 📚 RAG Answer (context-grounded)")
                    st.success(cmp["rag_answer"])
    
                with col2:
                    st.markdown("### 🧠 No-RAG Answer (LLM only)")
                    st.warning(cmp["no_rag_answer"])
    
                # Context Inspector
                st.markdown("### 🔎 RAG Context Inspector")
                render_rag_context_inspector({"contexts": cmp["contexts"], "answer": cmp["rag_answer"]})
                
                # Save for diff viewing below
                st.session_state["kb_cmp_last"] = cmp
            
            except Exception as e:
                 st.error(f"Comparison failed: {e}")

    st.markdown("---")
    st.subheader("🔬 Difference Highlighter (RAG vs No-RAG)")

    # Use session saved comparison if available, or local variable 'cmp' if just run
    cmp_to_diff = st.session_state.get("kb_cmp_last")
    if 'cmp' in locals():
        cmp_to_diff = cmp
    
    if cmp_to_diff:
        try:
            diff = difflib.unified_diff(
                cmp_to_diff["no_rag_answer"].splitlines(),
                cmp_to_diff["rag_answer"].splitlines(),
                fromfile="no_rag",
                tofile="rag",
                lineterm=""
            )
    
            diff_text = "\n".join(diff)
    
            if diff_text.strip():
                st.code(diff_text)
            else:
                st.info("The answers are identical or extremely similar.")
        except Exception as e:
            st.warning(f"Could not compute diff: {e}")
    else:
        st.info("Run a RAG vs No-RAG comparison to see highlighted differences.")
