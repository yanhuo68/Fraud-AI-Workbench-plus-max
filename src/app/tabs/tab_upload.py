import streamlit as st
import pandas as pd
from pathlib import Path
import json
from src.app.utils import rebuild_graph_base
from src.rag_sql.data_ingestion import ingest_uploaded_csv_dynamic

def render_upload_tab():
    st.header("📁 Upload Dataset (Dynamic Table Mode)")

    # ========== DEMO FILES SECTION ==========
    st.subheader("🎯 Quick Start: Load Demo Dataset")
    
    # Scan for demo CSV files in data/raw/
    demo_dir = Path("data/raw")
    demo_files = []
    if demo_dir.exists():
        demo_files = sorted([f for f in demo_dir.glob("*.csv")])
    
    if demo_files:
        col_demo, col_btn = st.columns([3, 1])
        with col_demo:
            demo_options = ["(Select a demo file)"] + [f.name for f in demo_files]
            selected_demo = st.selectbox(
                "Choose a demo dataset",
                demo_options,
                help="Select a sample dataset to quickly explore features"
            )
        
        with col_btn:
            st.write("")  # Spacer for alignment
            st.write("")  # Spacer for alignment
            load_demo = st.button("📥 Load Demo", disabled=(selected_demo == demo_options[0]), use_container_width=True)
        
        if load_demo and selected_demo != demo_options[0]:
            # Find the selected demo file
            demo_path = demo_dir / selected_demo
            if demo_path.exists():
                with st.spinner(f"Loading {selected_demo}..."):
                    try:
                        df = pd.read_csv(demo_path)
                        st.session_state.uploaded_df = df
                        
                        # Save to uploads dir
                        uploads_dir = Path("data/uploads")
                        uploads_dir.mkdir(parents=True, exist_ok=True)
                        df.to_csv(uploads_dir / selected_demo, index=False)
                        
                        st.success(f"✅ Demo dataset '{selected_demo}' loaded successfully!")
                        st.dataframe(df.head())
                        
                        # Import into database
                        with st.spinner("Importing into database..."):
                            table_name = ingest_uploaded_csv_dynamic(df, selected_demo)
                        
                        # Register table in session
                        if "uploaded_tables" not in st.session_state:
                            st.session_state.uploaded_tables = {}
                        st.session_state.uploaded_tables[table_name] = f"docs/schema_{table_name}.md"
                        
                        st.success(f"Imported as table: `{table_name}`")
                        st.json(st.session_state.uploaded_tables)
                        
                    except Exception as e:
                        st.error(f"Failed to load demo file: {e}")
            else:
                st.error(f"Demo file not found: {selected_demo}")
    else:
        st.info("No demo files found in data/raw/. Add CSV files there to enable quick loading.")
    
    st.markdown("---")
    st.subheader("📤 Or Upload Your Own CSV")
    
    uploaded_files = st.file_uploader("Upload CSV file(s)", type=["csv"], accept_multiple_files=True)

    # Auto-build graph base once per session if missing so visualization appears without manual click
    graph_manifest = Path("data/graph/graph_manifest.json")
    if (not graph_manifest.exists()) and (not st.session_state.get("graph_autobuilt")):
        rebuild_graph_base(log_handler=lambda msg: st.sidebar.error(msg))
        st.session_state["graph_autobuilt"] = True

    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                # Try to read the CSV
                try:
                    df = pd.read_csv(uploaded_file)
                except pd.errors.EmptyDataError:
                    st.error(f"❌ File '{uploaded_file.name}' is empty.")
                    continue
                except pd.errors.ParserError as e:
                    st.error(f"❌ Error parsing '{uploaded_file.name}': {str(e)}")
                    continue
                except Exception as e:
                    st.error(f"❌ Error reading '{uploaded_file.name}': {str(e)}")
                    continue
                
                st.session_state.uploaded_df = df  # retain last one for ML dashboard default

                # Save raw upload
                try:
                    uploads_dir = Path("data/uploads")
                    uploads_dir.mkdir(parents=True, exist_ok=True)
                    with open(uploads_dir / uploaded_file.name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                except PermissionError:
                    st.error(f"❌ Permission denied saving '{uploaded_file.name}'")
                    continue
                except Exception as e:
                    st.warning(f"⚠️ Could not save '{uploaded_file.name}' to disk: {str(e)}")

                st.success(f"✅ '{uploaded_file.name}' uploaded successfully!")
                with st.expander(f"Preview: {uploaded_file.name}", expanded=False):
                    st.dataframe(df.head())

                filename = uploaded_file.name

                # Import into database
                try:
                    with st.spinner(f"Importing {filename} into database..."):
                        table_name = ingest_uploaded_csv_dynamic(df, filename)

                    # Register table in session
                    if "uploaded_tables" not in st.session_state:
                        st.session_state.uploaded_tables = {}
                    st.session_state.uploaded_tables[table_name] = f"docs/schema_{table_name}.md"

                    st.info(f"Imported table: `{table_name}`")
                    
                except Exception as e:
                    st.error(f"❌ Database import failed for {filename}: {str(e)}")
                    # Keep dataframe in session even if DB import fails
                    # We might need a session store for multiple dfs if we want to be fancy, 
                    # but current architecture mainly uses 'uploaded_df' for single-table analysis 
                    # and 'table_dataframes' loaded from DB for multi-table.
                    # We should try to add it to 'table_dataframes' if DB fail? 
                    # ingest_uploaded_csv_dynamic actually loads it into DB. 
                    # If that fails, we can't easily use it in SQL RAG.
                    pass
                    
            except Exception as e:
                st.error(f"❌ Unexpected error processing '{uploaded_file.name}': {str(e)}")

        if "uploaded_tables" in st.session_state:
            st.write("### 📋 Uploaded Tables Registry")
            st.json(st.session_state.uploaded_tables)

    st.markdown("---")
    st.subheader("🗄️ Load Demo SQL Schema")
    
    # Scan for demo SQL files in data/raw/use_case/
    demo_sql_dir = Path("data/raw/use_case")
    demo_sql_files = []
    if demo_sql_dir.exists():
        demo_sql_files = sorted([f for f in demo_sql_dir.glob("*.sql")])
    
    if demo_sql_files:
        st.write("**📦 Quick Load: Relational Database Schema**")
        col_sql1, col_sql2 = st.columns([3, 1])
        
        with col_sql1:
            # Multi-select for SQL files
            selected_sql_files = st.multiselect(
                "Select SQL files to execute",
                [f.name for f in demo_sql_files],
                help="Choose one or more SQL files to create relational tables"
            )
        
        with col_sql2:
            st.write("")  # Spacer
            st.write("")  # Spacer
            load_sql_demo = st.button(
                "⚙️ Execute Demo SQL",
                disabled=(len(selected_sql_files) == 0),
                use_container_width=True
            )
        
        # Show file descriptions
        if selected_sql_files:
            with st.expander("📋 Selected Files Preview", expanded=False):
                for fname in selected_sql_files:
                    file_path = demo_sql_dir / fname
                    if file_path.exists():
                        st.markdown(f"**{fname}**")
                        # Read first few lines to find comments/description
                        content = file_path.read_text(encoding="utf-8")
                        lines = content.splitlines()[:5]
                        comments = [l for l in lines if l.strip().startswith("--")]
                        if comments:
                            st.code("\n".join(comments), language="sql")
                        else:
                            st.caption("No description found in file header.")
        
        if load_sql_demo:
            import sqlite3
            db_path = Path("data/db/fraud.db")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            results = []
            
            with st.spinner("Executing SQL scripts..."):
                with sqlite3.connect(db_path) as con:
                    for fname in selected_sql_files:
                        file_path = demo_sql_dir / fname
                        try:
                            script = file_path.read_text(encoding="utf-8")
                            con.executescript(script)
                            results.append(f"✅ {fname}: Executed successfully")
                        except Exception as e:
                            results.append(f"❌ {fname}: {e}")
            
            st.write("Execution results:")
            for r in results:
                st.write(r)
            
            # Refresh loaded tables so other tabs see new data
            from src.app.utils import _load_existing_db_tables
            _load_existing_db_tables()

    st.markdown("---")
    st.subheader("🛠️ Upload & Execute SQL Script")
    
    uploaded_sql = st.file_uploader("Upload .sql file", type=["sql"])
    if uploaded_sql:
        if st.button("▶️ Execute Uploaded SQL", use_container_width=True):
            import sqlite3
            db_path = Path("data/db/fraud.db")
            try:
                script_content = uploaded_sql.read().decode("utf-8")
                with sqlite3.connect(db_path) as con:
                    con.executescript(script_content)
                st.success(f"✅ Executed `{uploaded_sql.name}` successfully!")
                
                # Refresh metadata
                from src.app.utils import _load_existing_db_tables
                _load_existing_db_tables()
                
            except Exception as e:
                st.error(f"❌ Execution failed: {e}")

    st.divider()
    
    # Container for Demo Guidelines
    with st.container():
        st.subheader("🎯 Load Demo Guidelines")
        
        # Scan for demo .md files in data/raw/
        demo_docs_dir = Path("data/raw")
        demo_md_files = []
        if demo_docs_dir.exists():
            demo_md_files = sorted([f.name for f in demo_docs_dir.glob("*.md")])
        
        if demo_md_files:
            col_md, col_btn_md = st.columns([3, 1])
            with col_md:
                selected_demo_mds = st.multiselect(
                    "Select demo guidelines to load",
                    demo_md_files,
                    help="Choose risk/fraud guidelines to populate the Knowledge Base"
                )
            
            with col_btn_md:
                st.write("") # spacer
                st.write("") # spacer
                load_md_demo = st.button("📥 Load Selected Guidelines", disabled=(len(selected_demo_mds) == 0), use_container_width=True)
            
            if load_md_demo:
                processed_demos = []
                docs_target_dir = Path("docs")
                docs_target_dir.mkdir(parents=True, exist_ok=True)
                
                for fname in selected_demo_mds:
                    src_path = demo_docs_dir / fname
                    dest_path = docs_target_dir / fname
                    try:
                        # Copy file
                        dest_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")
                        processed_demos.append(fname)
                    except Exception as e:
                        st.error(f"❌ Failed to copy {fname}: {e}")
                
                if processed_demos:
                    st.success(f"✅ Loaded {len(processed_demos)} demo guideline(s) into `docs/`.")
                    
                    # Auto-rebuild graph and vector store with st.status
                    with st.status("🔄 Updating Knowledge Base...", expanded=True) as status:
                        try:
                            # 1. Rebuild Graph
                            st.write("Constructing Knowledge Graph nodes...")
                            rebuild_graph_base(log_handler=lambda msg: st.write(f"Graph: {msg}"))
                            st.session_state["graph_autobuilt"] = True
                            st.write("✅ Graph Base updated.")
                            
                            # 2. Rebuild Vector Store (KB)
                            st.write("Indexing Vector Store (FAISS)...")
                            import subprocess
                            import sys
                            
                            cmd = [sys.executable, "src/rag_sql/build_kb_index.py", "--docs-dir", "docs", "--out-dir", "data/kb"]
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            
                            if result.returncode != 0:
                                st.warning(f"⚠️ Vector store rebuild had issues: {result.stderr}")
                                status.update(label="⚠️ Knowledge Base update completed with warnings", state="error")
                            else:
                                st.write("✅ Vector Store updated.")
                                status.update(label="✅ Knowledge Base successfully updated!", state="complete")
                            
                            for pf in processed_demos:
                                 st.caption(f"Indexed: {pf}")
                                 
                        except Exception as e:
                            st.error(f"❌ Rebuild failed: {str(e)}")
                            status.update(label="❌ Update failed", state="error")

    st.divider()
    
    # Container for Upload Risk Guidelines
    with st.container():
        st.subheader("📂 Upload Risk Guidelines")
        st.caption("Upload markdown (.md) policies or risk guidelines. These will be added to the Knowledge Base and indexed immediately.")
    
        uploaded_guidelines = st.file_uploader("Upload Guideline Markdown", type=["md"], accept_multiple_files=True, key="guideline_uploader")
        
        if uploaded_guidelines:
            # Initialize session state for tracking if not present
            if "processed_guidelines" not in st.session_state:
                st.session_state.processed_guidelines = set()
                
            # Identify new files
            new_files = [f for f in uploaded_guidelines if f.name not in st.session_state.processed_guidelines]
            
            if new_files:
                processed_now = []
                for guide_file in new_files:
                    try:
                        # Save to docs/
                        docs_dir = Path("docs")
                        docs_dir.mkdir(parents=True, exist_ok=True)
                        save_path = docs_dir / guide_file.name
                        
                        with open(save_path, "wb") as f:
                            f.write(guide_file.getbuffer())
                        
                        # Mark as processed
                        st.session_state.processed_guidelines.add(guide_file.name)
                        processed_now.append(guide_file.name)
                    except Exception as e:
                        st.error(f"❌ Failed to save {guide_file.name}: {e}")
    
                if processed_now:
                    st.success(f"✅ Successfully uploaded {len(processed_now)} new document(s) to `docs/` folder.")
                    
                    # Auto-rebuild graph and vector store with st.status
                    with st.status("🔄 Updating Knowledge Base...", expanded=True) as status:
                        try:
                            # 1. Rebuild Graph
                            st.write("Constructing Knowledge Graph nodes...")
                            rebuild_graph_base(log_handler=lambda msg: st.write(f"Graph: {msg}"))
                            st.session_state["graph_autobuilt"] = True
                            st.write("✅ Graph Base updated.")
                            
                            # 2. Rebuild Vector Store (KB)
                            st.write("Indexing Vector Store (FAISS)...")
                            import subprocess
                            import sys
                            
                            # Use current python executable
                            cmd = [sys.executable, "src/rag_sql/build_kb_index.py", "--docs-dir", "docs", "--out-dir", "data/kb"]
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            
                            if result.returncode != 0:
                                st.warning(f"⚠️ Vector store rebuild had issues: {result.stderr}")
                                status.update(label="⚠️ Knowledge Base update completed with warnings", state="error")
                            else:
                                st.write("✅ Vector Store updated.")
                                status.update(label="✅ Knowledge Base successfully updated!", state="complete")
                            
                            # specific professional feedback
                            for pf in processed_now:
                                 st.caption(f"Indexed: {pf}")
                                 
                        except Exception as e:
                            st.error(f"❌ Rebuild failed: {str(e)}")
                            status.update(label="❌ Update failed", state="error")
            else:
                # All uploaded files are already processed
                st.info(f"✅ {len(uploaded_guidelines)} guideline(s) currently uploaded and indexed.")

    st.divider()
    
    # Container for Graph Visualization
    with st.container():
        st.subheader("📊 Graph Base Visualization")
        
        # Check if triggered from sidebar or auto-show
        show_graph = st.session_state.get("show_segmented_graph", False)
        
        # Also show if graph manifest exists, just to be discoverable
        graph_manifest = Path("data/graph/graph_manifest.json")
        
        if show_graph or graph_manifest.exists():
            if st.button("Generate/Refresh Graph Visualization", use_container_width=True):
                st.session_state.show_segmented_graph = True
            
            if st.session_state.get("show_segmented_graph"):
                from src.app.utils import visualize_segmented_graph
                visualize_segmented_graph(st)
        else:
            st.info("Graph Visualization will appear here after Documents are processed.")
