import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import re
import json
import networkx as nx
import matplotlib.pyplot as plt

def parse_structured_filters(question: str):
    """
    Extract structured filters from a natural language question.
    """
    filters = []
    patterns = [
        r"([A-Za-z0-9_ ]+)\s*=\s*['\"]?([A-Za-z0-9 _.-]+)['\"]?",
        r"using\s+([A-Za-z0-9_ ]+)\s+(?:as|=)\s+([A-Za-z0-9 _.-]+)",
    ]
    for pat in patterns:
        for m in re.finditer(pat, question, flags=re.IGNORECASE):
            col = m.group(1).strip()
            val = m.group(2).strip()
            if col and val:
                filters.append((col, val))
    return filters

def rebuild_graph_base(log_handler=None):
    """Build graph manifest/corpus from docs/ and data/uploads/. Returns manifest path."""
    def log_err(msg):
        if log_handler:
            log_handler(msg)

    graph_dir = Path("data/graph")
    graph_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    corpus_parts = []
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    docs_dir = Path("docs")
    for md_file in sorted(docs_dir.glob("*.md")):
        try:
            text = md_file.read_text(encoding="utf-8")
            entries.append(
                {
                    "type": "markdown",
                    "path": str(md_file),
                    "content": text[:200],  # snippet
                    "mod_time": ts,
                }
            )
            corpus_parts.append(f"--- FILE: {md_file.name} ---\n{text}\n")
        except Exception as e:
            log_err(f"Error reading {md_file}: {e}")

    # Also include data uploads schemas if available
    uploads_dir = Path("data/uploads")
    # In a real app, we might scan schemas or CSV head
    # For now, let's look for schema_*.md in docs which we generate on upload
    
    manifest_path = graph_dir / "manifest.json"
    manifest = {
        "timestamp": ts,
        "files": entries,
        "corpus_path": "data/graph/corpus.txt"
    }
    manifest_path.write_text(json_dumps(manifest), encoding="utf-8")

    corpus_path = graph_dir / "corpus.txt"
    with open(corpus_path, "w", encoding="utf-8") as f:
        f.write("\n".join(corpus_parts))
    
    return str(manifest_path)

# Helper for JSON dumping with indentation - used in rebuild_graph_base
def json_dumps(obj):
    import json
    return json.dumps(obj, indent=2)

def _write_schema_md(table_name: str, df: pd.DataFrame):
    """Write a simple schema markdown file for a dataframe."""
    schema_path = Path(f"docs/schema_{table_name}.md")
    # minimal schema
    dtypes = df.dtypes.to_dict()
    schema_lines = [f"# Schema for table: {table_name}", "", "| Column | Type |", "| --- | --- |"]
    for c, t in dtypes.items():
        schema_lines.append(f"| {c} | {t} |")
    schema_path.write_text("\n".join(schema_lines), encoding="utf-8")

def _load_existing_db_tables(db_path: str = "data/db/fraud.db"):
    """Load existing DB tables into session as if they were uploaded."""
    db = Path(db_path)
    if not db.exists():
        return

    try:
        with sqlite3.connect(db) as conn:
            # get list of tables
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for t in tables:
                t_name = t[0]
                if t_name == "sqlite_sequence": 
                    continue
                # Load a sample to get columns/schema
                # We won't load full DF into memory to save RAM, but we need it for 'uploaded_df' logic 
                # in various tabs (ML/ModelCompare).
                # If the user wants to use those tabs, they typically need the DF in memory.
                # Let's load it.
                try:
                    df = pd.read_sql_query(f"SELECT * FROM {t_name}", conn)
                    # Register in session
                    if "uploaded_tables" not in st.session_state:
                        st.session_state.uploaded_tables = {}
                    
                    # Generate schema file if missing
                    schema_file = Path(f"docs/schema_{t_name}.md")
                    if not schema_file.exists():
                        _write_schema_md(t_name, df)
                    
                    st.session_state.uploaded_tables[t_name] = f"docs/schema_{t_name}.md"
                    
                    # Also set table_dataframes for other tabs
                    if "table_dataframes" not in st.session_state:
                        st.session_state.table_dataframes = {}
                    st.session_state.table_dataframes[t_name] = df
                    
                    # Also set table_pkfk defaults
                    if "table_pkfk" not in st.session_state:
                         st.session_state.table_pkfk = {}
                    if t_name not in st.session_state.table_pkfk:
                         st.session_state.table_pkfk[t_name] = {"primary_key": None, "foreign_keys": []}

                except Exception as e:
                    print(f"Error loading table {t_name}: {e}")

    except Exception as e:
        print(f"Error connecting to DB {db}: {e}")

    # After loading all tables, run PK/FK detection if we have tables
    if "table_dataframes" in st.session_state and st.session_state.table_dataframes:
        try:
            from src.rag_sql.pkfk_detector import detect_primary_key, detect_foreign_keys
            
            # 1. Detect PKs for all tables
            primary_keys = {}
            for t_name, df_t in st.session_state.table_dataframes.items():
                pk = detect_primary_key(df_t)
                primary_keys[t_name] = pk
            
            # 2. Detect FKs across all tables
            foreign_keys = detect_foreign_keys(st.session_state.table_dataframes, primary_keys)
            
            # 3. Update table_pkfk in session state
            if "table_pkfk" not in st.session_state:
                st.session_state.table_pkfk = {}
            
            for t_name in st.session_state.table_dataframes.keys():
                t_pk = primary_keys.get(t_name)
                # Get FKs where this table is the source
                t_fks = [fk for fk in foreign_keys if fk[0] == t_name]
                
                st.session_state.table_pkfk[t_name] = {
                    "primary_key": t_pk,
                    "foreign_keys": t_fks
                }
            
            # print(f"Auto-detected relationships for {len(st.session_state.table_dataframes)} tables")
            
        except Exception as e:
            print(f"Error detecting relationships: {e}")

def generate_sample_questions(tables, primary_tbl, all_cols, numeric_cols, categorical_cols, relationships):
    """Generate contextually relevant sample questions for single or multiple tables."""
    questions = []
    
    if len(tables) == 1:
        # Single table questions
        table_name = tables[0]
        questions.append(f"How many rows are in the {table_name} table?")
        
        fraud_cols = [c for c in all_cols if any(x in c.lower() for x in ['fraud', 'label', 'class', 'target'])]
        if fraud_cols:
            fraud_col = fraud_cols[0]
            questions.append(f"How many records are labeled as fraud in {fraud_col}?")
            questions.append(f"What is the fraud rate (percentage) in this dataset?")
            
            if categorical_cols:
                cat_col = categorical_cols[0]
                questions.append(f"Which {cat_col} has the highest fraud rate?")
        
        if numeric_cols:
            num_col = numeric_cols[0]
            questions.append(f"What is the average {num_col}?")
            if fraud_cols:
                questions.append(f"What is the average {num_col} for fraud vs non-fraud cases?")
        
        if categorical_cols:
            cat_col = categorical_cols[0]
            questions.append(f"What are the top 5 most common {cat_col} values?")
    
    else:
        # Multi-table questions with JOINs
        questions.append(f"How many total records across all {len(tables)} selected tables?")
        
        if relationships:
            # Relationship-based questions
            rel = relationships[0]
            questions.append(f"Show all records from {rel['from_table']} joined with {rel['to_table']}")
            questions.append(f"How many {rel['from_table']} records match with {rel['to_table']}?")
            
            # Fraud across relationships
            fraud_cols = [c for c in all_cols if any(x in c.lower() for x in ['fraud', 'label', 'class', 'target'])]
            if fraud_cols:
                questions.append(f"Which {rel['to_table']} has the most fraud in {rel['from_table']}?")
                questions.append(f"Show fraud distribution across {rel['from_table']} and {rel['to_table']}")
            
            # Aggregations across tables
            if numeric_cols:
                num_col = numeric_cols[0]
                questions.append(f"What is the total {num_col} grouped by {rel['to_table']}?")
        else:
            # No detected relationships - Cartesian or generic
            questions.append(f"Show summary statistics from {', '.join(tables)}")
            questions.append(f"Compare row counts across {', '.join(tables)}")
    
    return questions[:10]

def detect_table_relationships(table_list):
    """Detect FK relationships between selected tables using pkfk metadata."""
    relationships = []
    # We need to access session state, so import streamlit inside or assume it's imported at top
    import streamlit as st
    pkfk_map = st.session_state.get("table_pkfk", {})
    
    for table in table_list:
        if table in pkfk_map:
            fks = pkfk_map[table].get("foreign_keys", [])
            for fk in fks:
                # fk format: (source_table, source_col, target_table, target_col)
                if len(fk) >= 4:
                    src_tbl, src_col, tgt_tbl, tgt_col = fk[0], fk[1], fk[2], fk[3]
                    if src_tbl in table_list and tgt_tbl in table_list:
                        relationships.append({
                            "from_table": src_tbl,
                            "from_col": src_col,
                            "to_table": tgt_tbl,
                            "to_col": tgt_col
                        })

def visualize_graph_base(container, grounding_table=None, key_suffix=""):
    """
    Render graph visualization in the specified container (st or st.sidebar).
    """
    with container.spinner("Building graph visualization..."):
        try:
            graph_store_path = Path("data/graph/graph_store.json")
            
            if not graph_store_path.exists():
                container.warning("Graph store not found. Click 'Rebuild Graph' in sidebar first.")
                return

            # Load graph store
            with open(graph_store_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            # Build NetworkX graph
            G = nx.Graph()
            
            # Extract nodes and sources from graph store
            nodes_data = graph_data.get("nodes", [])
            edges_data = graph_data.get("edges", [])
            
            # Track unique document sources
            document_sources = set()
            snippet_to_source = {}
            
            # Parse nodes to extract documents
            for node in nodes_data:
                node_type = node.get("type")
                node_id = node.get("id")
                
                if node_type == "snippet":
                    # Extract source (document name)
                    source = node.get("source", "unknown")
                    document_sources.add(source)
                    snippet_to_source[node_id] = source
            
            # Add Knowledge Base central node
            G.add_node("Knowledge Base", node_type='kb', size=1500, color='#e74c3c')
            
            # Add document nodes (from docs/)
            for doc_source in document_sources:
                if doc_source != "corpus":
                    # Clean up document name for display
                    doc_name = doc_source.replace("docs/", "").replace(".md", "")
                    G.add_node(doc_name, node_type='document', size=600, color='#2ecc71', source=doc_source)
                    # Connect document to Knowledge Base
                    G.add_edge("Knowledge Base", doc_name)
            
            # Add table nodes if we have uploaded tables
            if st.session_state.get("uploaded_tables"):
                table_names = list(st.session_state.uploaded_tables.keys())
                for table in table_names:
                    G.add_node(table, node_type='table', size=800, color='#3498db')
                    # Connect table to Knowledge Base
                    G.add_edge("Knowledge Base", table)
            
            # Add grounding table emphasis if selected
            if grounding_table and grounding_table in G.nodes():
                G.nodes[grounding_table]['size'] = 1000
                G.nodes[grounding_table]['color'] = '#f39c12'  # Orange highlight
            
            if len(G.nodes()) == 0:
                container.warning("No graph data available. Upload data/docs and rebuild graph.")
                return

            # Layout selection (simplified for sidebar if container is sidebar)
            is_sidebar = (container == st.sidebar)
            
            layout_type = "Radial (Star)"
            if not is_sidebar:
                layout_type = container.radio(
                    "Choose visualization layout:",
                    ["Radial (Star)", "Hierarchical Layers", "Circular Ring"],
                    index=0,
                    horizontal=True,
                    key=f"graph_layout_{key_suffix}"
                )
            
            # Create visualization
            # Adjust size for sidebar
            figsize = (6, 5) if is_sidebar else (16, 12)
            fig, ax = plt.subplots(figsize=figsize)
            
            # Extract node colors and sizes
            node_colors = []
            node_sizes = []
            for node in G.nodes():
                node_data = G.nodes[node]
                node_colors.append(node_data.get('color', '#95a5a6'))
                sz = node_data.get('size', 500)
                if is_sidebar:
                    sz = sz / 2.5 # Scale down for sidebar
                node_sizes.append(sz)
            
            # Choose layout based on selection
            if layout_type == "Radial (Star)":
                # Radial layout - KB at center, others in rings
                pos = {}
                center_node = "Knowledge Base"
                
                if center_node in G.nodes():
                    pos[center_node] = (0, 0)  # Center
                    
                    # Get neighbors (documents and tables)
                    neighbors = list(G.neighbors(center_node))
                    
                    # Separate by type
                    docs = [n for n in neighbors if G.nodes[n].get('node_type') == 'document']
                    tables = [n for n in neighbors if G.nodes[n].get('node_type') == 'table']
                    
                    # Place documents in inner ring
                    import math
                    radius_docs = 3.0
                    for i, doc in enumerate(docs):
                        angle = 2 * math.pi * i / max(len(docs), 1)
                        pos[doc] = (radius_docs * math.cos(angle), radius_docs * math.sin(angle))
                    
                    # Place tables in outer ring
                    radius_tables = 5.0
                    for i, table in enumerate(tables):
                        angle = 2 * math.pi * i / max(len(tables), 1)
                        pos[table] = (radius_tables * math.cos(angle), radius_tables * math.sin(angle))
                else:
                    pos = nx.spring_layout(G, seed=42, k=2.0)
            
            elif layout_type == "Hierarchical Layers":
                pos = nx.spring_layout(G, seed=42, k=3.0)
            else:  # Circular Ring
                pos = nx.circular_layout(G, scale=5.0)
            
            # Draw network
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                                 node_size=node_sizes, alpha=0.9, 
                                 edgecolors='#34495e', linewidths=1 if is_sidebar else 2, ax=ax)
            nx.draw_networkx_edges(G, pos, alpha=0.25, width=1.5 if is_sidebar else 2.5, 
                                 edge_color='#7f8c8d', style='solid', ax=ax)
            
            # Labels
            labels = {node: node for node in G.nodes()}
            font_size = 7 if is_sidebar else 10
            nx.draw_networkx_labels(G, pos, labels, font_size=font_size, 
                                  font_weight='bold', font_color='#2c3e50',
                                  bbox=dict(boxstyle='round,pad=0.2', 
                                           facecolor='white', 
                                           edgecolor='none', 
                                           alpha=0.7), ax=ax)
            
            if not is_sidebar:
                ax.set_title(f"Knowledge Graph Network ({len(G.nodes())} nodes)", fontsize=18)
            
            ax.axis('off')
            plt.tight_layout()
            
            container.pyplot(fig)
            plt.close(fig)
            
            if not is_sidebar:
                 # Show stats in main view
                c1, c2, c3 = container.columns(3)
                c1.metric("Nodes", len(G.nodes()))
                c2.metric("Edges", len(G.edges()))
                c3.metric("Docs/Tables", len(document_sources) + len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'table']))

        except Exception as e:
            container.error(f"Failed to visualize graph: {e}")
def visualize_segmented_graph(container):
    """
    Render segmented graph visualizations (Tables + 4 Document segments).
    """
    try:
        graph_store_path = Path("data/graph/graph_store.json")
        if not graph_store_path.exists():
            container.warning("Graph store not found. Click 'Rebuild Graph' in sidebar first.")
            return

        with open(graph_store_path, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)

        nodes_data = graph_data.get("nodes", [])
        
        # 1. Identify Tables and Documents
        # Identify unique documents from snippets/docs
        document_sources = set()
        for node in nodes_data:
            if node.get("type") == "snippet":
                source = node.get("source", "unknown")
                if source != "corpus":
                     document_sources.add(source)
        
        sorted_docs = sorted(list(document_sources))
        
        # Segment 1: Tables
        # Segment 2: MD 1-12
        # Segment 3: MD 13-26
        # Segment 4: MD 27-41
        # Segment 5: MD 42+
        
        segments = {
            "Tables (Database)": {"type": "table", "items": []}, 
            "Documents (Part 1: 1-12)": {"type": "doc", "items": sorted_docs[:12]},
            "Documents (Part 2: 13-26)": {"type": "doc", "items": sorted_docs[12:26]},
            "Documents (Part 3: 27-41)": {"type": "doc", "items": sorted_docs[26:41]},
            "Documents (Part 4: 42+)": {"type": "doc", "items": sorted_docs[41:]}
        }
        
        # Helper to plot a subgraph
        def plot_subgraph(title, items, is_table=False):
            # Check for content:
            # Table segment: needs st.session_state.uploaded_tables or table nodes in graph_data
            # Doc segment: needs items
            
            has_content = False
            if is_table:
                if st.session_state.get("uploaded_tables"):
                    has_content = True
                else:
                    # check graph data
                    for n in nodes_data:
                        if n.get("type") == "table":
                            has_content = True
                            break
            else:
                if items:
                    has_content = True

            if not has_content:
                return 

            with st.expander(f"🕸️ {title}", expanded=True):
                # Build Subgraph
                G = nx.Graph()
                # Central Node
                G.add_node("Knowledge Base", node_type='kb', size=1500, color='#e74c3c')
                
                if is_table:
                    # Add table nodes from session state
                    if st.session_state.get("uploaded_tables"):
                        for t in st.session_state.uploaded_tables.keys():
                            G.add_node(t, node_type='table', size=800, color='#3498db')
                            G.add_edge("Knowledge Base", t)
                    # Also check graph_store for any table nodes
                    for n in nodes_data:
                        if n.get("type") == "table":
                            t_name = n.get("id")
                            if t_name not in G.nodes():
                                 G.add_node(t_name, node_type='table', size=800, color='#3498db')
                                 G.add_edge("Knowledge Base", t_name)
                else:
                    # Document segment
                    for doc_source in items:
                        doc_name = doc_source.replace("docs/", "").replace(".md", "")
                        G.add_node(doc_name, node_type='document', size=600, color='#2ecc71')
                        G.add_edge("Knowledge Base", doc_name)
                
                # Plot
                if len(G.nodes()) > 1: # At least KB + 1 node
                    fig, ax = plt.subplots(figsize=(10, 8))
                    
                    pos = nx.spring_layout(G, seed=42, k=0.6)
                    
                    # Colors
                    node_colors = []
                    node_sizes = []
                    for n_node in G.nodes():
                         d = G.nodes[n_node]
                         node_colors.append(d.get('color', '#95a5a6'))
                         node_sizes.append(d.get('size', 500))
                    
                    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9, ax=ax)
                    nx.draw_networkx_edges(G, pos, alpha=0.3, width=1.5, ax=ax)
                    
                    labels = {n_node: n_node for n_node in G.nodes()}
                    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold', 
                                          bbox=dict(facecolor='white', edgecolor='none', alpha=0.7), ax=ax)
                    
                    ax.axis('off')
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.info("No nodes in this segment.")

        # Plot Table Segment
        plot_subgraph("Tables (Database)", [], is_table=True)
        
        # Plot Document Segments
        plot_subgraph("Documents (Part 1: 1-12)", segments["Documents (Part 1: 1-12)"]["items"])
        plot_subgraph("Documents (Part 2: 13-26)", segments["Documents (Part 2: 13-26)"]["items"])
        plot_subgraph("Documents (Part 3: 27-41)", segments["Documents (Part 3: 27-41)"]["items"])
        plot_subgraph("Documents (Part 4: 42+)", segments["Documents (Part 4: 42+)"]["items"])

    except Exception as e:
        container.error(f"Failed to visualize segmented graphs: {e}")
