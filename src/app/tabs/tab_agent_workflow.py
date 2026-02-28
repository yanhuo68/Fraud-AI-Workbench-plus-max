import streamlit as st
from pathlib import Path
from src.agents.graph_visualizer import get_graph_mermaid

def render_agent_workflow_tab():
    st.header("🤖 Agent Workflow")
    st.caption("Visualize the LangGraph agent workflow and architecture.")

    # Check for dynamic workflow from session state
    if "langgraph_workflow" in st.session_state and st.session_state.langgraph_workflow:
        try:
            graphs = st.session_state.langgraph_workflow
            graph_name = list(graphs.keys())[0]
            mermaid_code = get_graph_mermaid(graphs[graph_name])
            
            st.subheader("📊 Workflow Diagram (Mermaid)")
            st.markdown(f"```mermaid\n{mermaid_code}\n```")
            
            # Generate a JPG preview using graphviz for quick visual
            try:
                import graphviz
                gv = graphviz.Digraph("agent_flow", format="jpg")
                gv.attr(rankdir="LR")
                g = graphs[graph_name]
                for n in g.nodes.keys():
                    gv.node(n)
                for src, dsts in g.edges.items():
                    for dst in dsts:
                        gv.edge(src, dst)
                img_dir = Path("data/generated")
                img_dir.mkdir(parents=True, exist_ok=True)
                jpg_target = img_dir / "agent_workflow"
                rendered = gv.render(str(jpg_target), cleanup=True)
                candidates = [
                    Path(rendered),
                    Path(str(rendered) + ".jpg"),
                    jpg_target.with_suffix(".jpg"),
                    jpg_target.with_suffix(".jpg.jpg"),
                ]
                for cand in candidates:
                    if cand.exists():
                        st.image(str(cand), caption="Agent Workflow Visualization", width="stretch")
                        break
            except Exception as e:
                st.info(f"Could not generate image preview: {e}")
        except Exception as e:
            st.error(f"Error displaying workflow: {e}")
    else:
        # Fallback: show static mermaid file if present
        mermaid_file = Path("documentation/design/langgraph_agent_map_diagram.mermaid")
        if mermaid_file.exists():
            try:
                st.subheader("📊 Workflow Diagram (Mermaid)")
                st.markdown(f"```mermaid\n{mermaid_file.read_text()}\n```")
                
                st.subheader("📖 Abbreviation Legend")
                st.markdown("""
**Agent Abbreviations:**
- **U**: User
- **SP**: SQL/Schema Planner
- **SE**: SQL Executor
- **SC**: SQL Checker (validation/repair)
- **KR**: Knowledge Retriever (docs/KB)
- **KG**: Knowledge Grounder (injects context)
- **SA**: Schema Analyzer (tables/ERD)
- **O1/O2/O3**: Output branches/variants
- **MM**: Model Manager (load/save)
- **ME**: Model Evaluator (metrics)
- **MD**: Model Deployer (artifacts)
- **RS**: Report Synthesizer
""")
            except Exception as e:
                st.warning(f"Agent workflow file found but could not be displayed: {e}")
            
            # Attempt to build a JPG from mermaid edges (best-effort)
            try:
                import graphviz
                import re
                lines = mermaid_file.read_text().splitlines()
                gv = graphviz.Digraph("agent_flow_fallback", format="jpg")
                gv.attr(rankdir="LR")
                for ln in lines:
                    m = re.search(r"([A-Za-z0-9_]+)\s*[-]{1,2}>\s*([A-Za-z0-9_]+)", ln)
                    if m:
                        a, b = m.group(1), m.group(2)
                        gv.node(a)
                        gv.node(b)
                        gv.edge(a, b)
                img_dir = Path("data/generated")
                img_dir.mkdir(parents=True, exist_ok=True)
                jpg_target = img_dir / "agent_workflow_mermaid"
                for cand in [jpg_target.with_suffix(".jpg"), jpg_target.with_suffix(".jpg.jpg")]:
                    if cand.exists():
                        st.image(str(cand), caption="Agent Workflow Visualization", width="stretch")
                        break
            except Exception:
                pass
            
            # Copy mermaid file to generated for reference
            try:
                mermaid_copy = Path("data/generated/langgraph_agent_map_diagram.mermaid")
                mermaid_copy.parent.mkdir(parents=True, exist_ok=True)
                mermaid_copy.write_text(mermaid_file.read_text(), encoding="utf-8")
            except Exception:
                pass
        
        # Check for pre-generated JPG (multiple possible names)
        found_jpg = False
        for jpg_name in ["agent_workflow.jpg", "agent_workflow_mermaid.jpg"]:
            jpg_path = Path("data/generated") / jpg_name
            if jpg_path.exists():
                st.image(str(jpg_path), caption="Agent Workflow", width="stretch")
                found_jpg = True
                break
        
        if not found_jpg and not mermaid_file.exists():
            st.info("No agent workflow detected yet. Add `data/generated/agent_workflow.jpg` or `documentation/design/langgraph_agent_map_diagram.mermaid` to display the workflow.")
    
    # Node Explanations Section (always show)
    st.divider()
    st.subheader("🧠 Node Explanations")
    st.caption("Understanding each agent's role in the workflow")
    
    with st.expander("👤 **U - User**", expanded=False):
        st.markdown("""
**Role**: Entry point for user queries

The User node represents the initial interaction point where users submit their questions, requests, or commands to the system. This is where the workflow begins.

**Key Functions**:
- Accepts natural language queries
- Initiates workflow execution
- Receives final results
""")
    
    with st.expander("📋 **SP - SQL/Schema Planner**", expanded=False):
        st.markdown("""
**Role**: Analyzes query intent and plans SQL generation

The SQL/Schema Planner interprets user questions and determines the optimal SQL query structure needed to retrieve the requested information.

**Key Functions**:
- Natural language understanding
- Query intent classification
- SQL query planning and optimization
- Schema inference
""")
    
    with st.expander("⚙️ **SE - SQL Executor**", expanded=False):
        st.markdown("""
**Role**: Executes generated SQL queries against the database

The SQL Executor takes the planned SQL query and runs it against the actual database, returning structured data results.

**Key Functions**:
- Database connection management
- SQL query execution
- Result set retrieval
- Error handling for database operations
""")
    
    with st.expander("✅ **SC - SQL Checker**", expanded=False):
        st.markdown("""
**Role**: Validates and repairs malformed SQL

The SQL Checker acts as a quality control agent, validating SQL syntax and semantics before execution, and attempting to repair any detected issues.

**Key Functions**:
- SQL syntax validation
- Schema compatibility checking
- Automatic query repair
- Security validation (SQL injection prevention)
""")
    
    with st.expander("📚 **KR - Knowledge Retriever**", expanded=False):
        st.markdown("""
**Role**: Retrieves relevant documentation from knowledge base

The Knowledge Retriever searches through the documentation and knowledge base to find relevant context, guidelines, and reference materials.

**Key Functions**:
- Semantic search across documents
- FAISS vector similarity matching
- Document ranking and retrieval
- Context extraction
""")
    
    with st.expander("🔗 **KG - Knowledge Grounder**", expanded=False):
        st.markdown("""
**Role**: Injects retrieved context into responses

The Knowledge Grounder takes information from the Knowledge Retriever and integrates it into the response generation process, ensuring answers are grounded in documentation.

**Key Functions**:
- Context integration
- Fact verification
- Response augmentation
- Citation generation
""")
    
    with st.expander("🗂️ **SA - Schema Analyzer**", expanded=False):
        st.markdown("""
**Role**: Analyzes database schema and generates ERDs

The Schema Analyzer examines database structures, relationships, and constraints to provide schema understanding and visualization.

**Key Functions**:
- Table structure analysis
- Relationship detection (FK/PK)
- ERD generation
- Schema documentation
""")
    
    with st.expander("💾 **MM - Model Manager**", expanded=False):
        st.markdown("""
**Role**: Manages ML model loading and saving

The Model Manager handles the lifecycle of machine learning models, including storage, retrieval, and version management.

**Key Functions**:
- Model serialization/deserialization
- Model versioning
- Model registry management
- Artifact storage
""")
    
    with st.expander("📊 **ME - Model Evaluator**", expanded=False):
        st.markdown("""
**Role**: Computes model performance metrics

The Model Evaluator assesses trained models using various performance metrics to ensure quality and readiness for deployment.

**Key Functions**:
- Accuracy, precision, recall calculation
- Confusion matrix generation
- ROC/AUC analysis
- Model comparison
""")
    
    with st.expander("🚀 **MD - Model Deployer**", expanded=False):
        st.markdown("""
**Role**: Handles model deployment and artifacts

The Model Deployer manages the transition of models from development to production environments.

**Key Functions**:
- Model packaging
- Deployment pipeline execution
- Endpoint configuration
- Rollback capabilities
""")
    
    with st.expander("📄 **RS - Report Synthesizer**", expanded=False):
        st.markdown("""
**Role**: Generates final reports and insights

The Report Synthesizer aggregates information from various sources and produces comprehensive, user-friendly reports.

**Key Functions**:
- Multi-source data aggregation
- Insight generation
- Report formatting
- Visualization creation
""")
    
    with st.expander("🔀 **O1/O2/O3 - Output Branches**", expanded=False):
        st.markdown("""
**Role**: Represents different output paths or variants

Output branches indicate decision points in the workflow where different paths may be taken based on conditions or user preferences.

**Key Functions**:
- Conditional routing
- Output format selection
- Multi-path execution
- Result aggregation
""")
