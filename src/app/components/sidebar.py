import streamlit as st
from pathlib import Path
import subprocess
from datetime import datetime
from src.app.utils import rebuild_graph_base, visualize_graph_base
from src.agents.graph_visualizer import get_graph_mermaid

def render_sidebar():
    # ------------------------------
    #  Sidebar Utilities
    # ------------------------------
    st.sidebar.title("Configuration")
    with st.sidebar.expander("🔑 API Keys", expanded=False):
        st.text_input("OpenAI API Key", type="password", key="sidebar_openai_key", help="Overrides host OPENAI_API_KEY")
        st.text_input("DeepSeek API Key", type="password", key="sidebar_deepseek_key", help="Overrides host DEEPSEEK_API_KEY")
        st.text_input("Google API Key", type="password", key="sidebar_google_key", help="Overrides host GOOGLE_API_KEY")
        st.text_input("Anthropic API Key", type="password", key="sidebar_anthropic_key", help="Overrides host ANTHROPIC_API_KEY")
        st.caption("""
        ℹ️ **How API keys work:**
        - Keys entered above are **session-based** (temporary).
        - If you don't enter a key here, the system automatically checks **system environment variables** (persistent).
        - Priority: System env vars → .env file → sidebar input (as fallback).
        """)

    st.sidebar.title("Tools")

    if st.sidebar.button("🎥 Start Demo", use_container_width=True):
        st.session_state.demo_active = True
        st.session_state.demo_step = 0
        st.rerun()

    if st.sidebar.button("🔄 Rebuild KB Index", use_container_width=True):
        log_file = Path("logs/rebuild_kb.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with st.spinner("Rebuilding knowledge-base index..."):
            result = subprocess.run(
                ["python", "src/rag_sql/build_kb_index.py", "--docs-dir", "docs", "--out-dir", "data/kb"],
                capture_output=True,
                text=True
            )
            # Persist stdout/stderr to log file to keep UI clean
            timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
            with log_file.open("a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] Rebuild KB Index\n")
                f.write(result.stdout or "")
                if result.stderr:
                    f.write("\n[stderr]\n")
                    f.write(result.stderr)

            if result.returncode == 0:
                st.sidebar.success("FAISS index rebuilt. Details logged to logs/rebuild_kb.log")
            else:
                st.sidebar.error(f"Rebuild failed (see logs/rebuild_kb.log). Return code: {result.returncode}")

    if st.sidebar.button("🧹 Clean DB", use_container_width=True):
        db_paths = [Path("data/db/fraud.db")]
        removed = []
        errors = []

        for p in db_paths:
            try:
                if p.exists():
                    p.unlink()
                    removed.append(str(p))
            except Exception as e:
                errors.append(f"{p}: {e}")

        # Clear cached session tables to avoid stale state after DB cleanup
        for key in ["uploaded_tables", "table_dataframes", "table_pkfk"]:
            if key in st.session_state:
                del st.session_state[key]

        if errors:
            st.sidebar.error("DB clean completed with errors: " + "; ".join(errors))
        else:
            msg = "Removed: " + ", ".join(removed) if removed else "No DB files found to remove."
            st.sidebar.success(msg)

    if st.sidebar.button("🧹 Clean KB", use_container_width=True):
        # Paths to clean
        kb_dir = Path("data/kb")
        graph_dir = Path("data/graph")
        
        cleaned_items = []
        errors = []
        
        # 1. Clean Vector Store (KB)
        if kb_dir.exists():
            try:
                # Remove all files in kb_dir
                for item in kb_dir.glob("*"):
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        import shutil
                        shutil.rmtree(item)
                cleaned_items.append("Vector Store (data/kb)")
            except Exception as e:
                errors.append(f"KB Clean Error: {e}")
                
        # 2. Clean Graph Store
        if graph_dir.exists():
            try:
                # Remove all files in graph_dir
                for item in graph_dir.glob("*"):
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        import shutil
                        shutil.rmtree(item)
                cleaned_items.append("Graph Store (data/graph)")
            except Exception as e:
                errors.append(f"Graph Clean Error: {e}")
        
        # 3. Clear Session State
        keys_to_clear = [
            "kb_current_samples", 
            "graph_current_samples", 
            "kb_last_result", 
            "graph_store", 
            "kb_cmp_last"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
                
        if errors:
            st.sidebar.error("Clean KB completed with errors: " + "; ".join(errors))
        else:
            if cleaned_items:
                st.sidebar.success(f"Cleaned: {', '.join(cleaned_items)}")
                # Rerun to update UI state immediately
                st.rerun()
            else:
                st.sidebar.info("KB/Graph directories were already empty.")

    if st.sidebar.button("🕸️ Rebuild Graph", use_container_width=True):
        with st.spinner("Rebuilding graph base..."):
            rebuild_graph_base(log_handler=lambda msg: st.sidebar.error(msg))
        st.sidebar.success("Graph base rebuilt from docs/ and data/uploads/ into data/graph/.")

    if st.sidebar.button("🎨 Visualize Graph", use_container_width=True):
        st.session_state.show_segmented_graph = True
        st.sidebar.success("View the graph in the 'Upload Data' tab (bottom).")

    ml_workflow_img = Path("docs/ml_pipeline.jpg")
    if ml_workflow_img.exists():
        st.sidebar.image(str(ml_workflow_img), caption="ML Pipeline Workflow", width="stretch")
    else:
        st.sidebar.info("Add docs/ml_pipeline.jpg to display the ML pipeline workflow here.")

    # ------------------------------
    #  Fraud Guidelines (New Section)
    # ------------------------------
    st.sidebar.markdown("---")
    with st.sidebar.expander("🛡️ Fraud Guidelines", expanded=False):
        # Category Selector
        guide_category = st.selectbox(
            "Select Category", 
            ["Fraud Detection", "Fraud Risk", "All Guidelines"],
            key="fraud_guide_category"
        )
        
        # Scan docs/ for markdown files
        docs_dir = Path("docs")
        if not docs_dir.exists():
            st.sidebar.info("Docs folder not found.")
        else:
            all_md_files = sorted([f.name for f in docs_dir.glob("*.md")])
            
            # Filter Logic
            filtered_files = []
            if guide_category == "Fraud Risk":
                # Filter for "risk" in name
                filtered_files = [f for f in all_md_files if "risk" in f.lower()]
            elif guide_category == "Fraud Detection":
                # Filter for "fraud" but maybe exclude explicit "risk" ones if we want strict separation, 
                # or just look for "fraud" generically. 
                # Request said: category 2: fraud detection and fraud risk. 
                # Let's simple filter: current docs have names like 'fraud_risk_...'
                # So 'Fraud Detection' can be general 'fraud' excluding 'risk' maybe? 
                # Or just anything with 'fraud' that isn't explicitly just 'risk'. 
                # Let's try: Detection = has "fraud" AND NOT "risk", to differentiate.
                # Risk = has "risk"
                filtered_files = [f for f in all_md_files if "fraud" in f.lower() and "risk" not in f.lower()]
                # If list is empty, maybe fallback to just 'fraud' in general
                if not filtered_files: 
                     filtered_files = [f for f in all_md_files if "fraud" in f.lower()]
            else:
                # All
                filtered_files = all_md_files
            
            # Display list
            if not filtered_files:
                st.sidebar.info(f"No documents found for {guide_category}.")
            else:
                guide_opts = ["(Select a guideline)"] + filtered_files
                selected_guide = st.selectbox("Select Document", guide_opts, key="fraud_guide_select")
                
                if selected_guide != "(Select a guideline)":
                    if st.sidebar.button("📖 View Guideline", key="btn_view_fraud_guide", use_container_width=True):
                        st.session_state.help_active = True
                        st.session_state.help_file_path = str(docs_dir / selected_guide)
                        st.rerun()
    st.sidebar.markdown("---")
    with st.sidebar.expander("📚 Help & Documentation", expanded=False):
        # Scan for documentation folders
        doc_root = Path("documentation")
        if not doc_root.exists():
            st.sidebar.info("Documentation folder not found.")
        else:
            # List subdirectories that contain .md files
            doc_folders = sorted([
                d.name for d in doc_root.iterdir() 
                if d.is_dir() and not d.name.startswith(".") and list(d.glob("*.md"))
            ])
            
            if not doc_folders:
                st.sidebar.info("No documentation folders found.")
            else:
                selected_folder = st.selectbox("Select Category", doc_folders, key="help_folder_select")
                
                # List md files in selected folder
                folder_path = doc_root / selected_folder
                md_files = sorted([f.name for f in folder_path.glob("*.md")])
                
                # Add a "None" option to allow deselecting
                md_files_opts = ["(Select a file to view)"] + md_files
                
                selected_file = st.selectbox("Select Document", md_files_opts, key="help_file_select")
                
                if selected_file != "(Select a file to view)":
                    if st.button("📖 View Document", use_container_width=True):
                        st.session_state.help_active = True
                        st.session_state.help_file_path = str(folder_path / selected_file)
                        st.rerun()

    # Close Help Button (Only if active)
    if st.session_state.get("help_active"):
        if st.sidebar.button("❌ Close Help / Return to App", use_container_width=True):
            st.session_state.help_active = False
            st.rerun()
