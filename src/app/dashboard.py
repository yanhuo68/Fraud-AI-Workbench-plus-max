import streamlit as st
import sys
from pathlib import Path

# Ensure project root is on sys.path when launched from other working dirs
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Page check to avoid double set_page_config if handled elsewhere, but usually dashboard is main
# We put this first before other imports that might use st
st.set_page_config(
    page_title="Fraud Detection AI Workbench",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    /* Global Button Style (Main Area default) - Light Blue */
    div.stButton > button {
        background-color: #0F52BA !important;
        color: white !important;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #0a3d8f !important; /* Darker blue */
        color: white !important;
    }

    /* Download Buttons - Light Blue */
    .stDownloadButton > button {
        background-color: #0F52BA !important;
        color: white !important;
        border: none;
    }
    .stDownloadButton > button:hover {
        background-color: #0a3d8f !important;
        color: white !important;
    }
    
    /* File Uploader 'Browse files' Button - Light Blue */
    [data-testid="stFileUploader"] button {
         background-color: #0F52BA !important;
         color: white !important;
         border: none;
    }
    [data-testid="stFileUploader"] button:hover {
         background-color: #0a3d8f !important;
         color: white !important;
    }

    /* Sidebar Button Nuke - Force same length */
    [data-testid="stSidebar"] div[data-testid="stButton"],
    [data-testid="stSidebar"] div[data-testid="stDownloadButton"],
    [data-testid="stSidebar"] div[data-testid="stLinkButton"],
    [data-testid="stSidebar"] .element-container {
        width: 100% !important;
    }
    
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
    [data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
    [data-testid="stSidebar"] [data-testid="stBaseButton-header"] {
        background-color: #d32f2f !important;
        color: white !important;
        border: none !important;
        width: 100% !important;
        min-width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        margin-bottom: 5px !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: #b71c1c !important;
    }
    
    /* Ensure Sidebar Expander Buttons are also Red and Full Width */
    [data-testid="stSidebar"] [data-testid="stExpander"] button {
        background-color: #d32f2f !important;
        color: white !important;
        border: none;
        width: 100% !important;
    }

    /* Sidebar Expander Headers - Red with White Text */
    [data-testid="stSidebar"] details > summary {
        background-color: #d32f2f !important;
        color: white !important;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    [data-testid="stSidebar"] details > summary:hover {
        background-color: #b71c1c !important; /* Darker red */
        color: white !important;
    }
    /* Fix Expander Arrow Icon Color */
    [data-testid="stSidebar"] details > summary svg {
        fill: white !important;
        color: white !important;
    }

    /* Specific Sidebar Overrides */
    
    /* 1. Start Demo - Green (4th element) */
    [data-testid="stSidebar"] .element-container:nth-of-type(4) button,
    [data-testid="stSidebar"] button[aria-label*="🎥"],
    [data-testid="stSidebar"] button[aria-label*="Start Demo"] {
        background-color: #4caf50 !important;
        color: white !important;
    }
    [data-testid="stSidebar"] .element-container:nth-of-type(4) button:hover,
    [data-testid="stSidebar"] button[aria-label*="🎥"]:hover {
        background-color: #388e3c !important;
    }

    /* 2. Fraud Guidelines - Light Gray (12th element) */
    [data-testid="stSidebar"] .element-container:nth-of-type(12) details > summary {
        background-color: #d3d3d3 !important;
        color: #333333 !important;
    }
    [data-testid="stSidebar"] .element-container:nth-of-type(12) details > summary:hover {
        background-color: #bdbdbd !important;
    }

    /* 3. Help & Documentation - Darker Gray (14th element) */
    [data-testid="stSidebar"] .element-container:nth-of-type(14) details > summary {
        background-color: #616161 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .element-container:nth-of-type(14) details > summary:hover {
        background-color: #424242 !important;
    }

    /* MultiSelect Tags - Light Green & White Text */
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: #66bb6a !important; /* Light Green */
        color: white !important;
    }
    
    /* Make All Tab Labels Bold */
    .stTabs [data-baseweb="tab"] p {
        font-weight: bold !important;
        font-size: 1.05rem; /* Slight increase for emphasis */
    }
</style>
""", unsafe_allow_html=True)

# Import modular components
from src.app.components.sidebar import render_sidebar
from src.app.tabs.tab_upload import render_upload_tab
from src.app.tabs.tab_ml_dashboard import render_ml_dashboard_tab
from src.app.tabs.tab_sql_rag import render_sql_rag_tab
from src.app.tabs.tab_kb_rag import render_kb_rag_tab
from src.app.tabs.tab_graph_rag import render_graph_rag_tab
from src.app.tabs.tab_rag_comparison import render_rag_comparison_tab
from src.app.tabs.tab_guideline_comparison import render_guideline_comparison_tab
from src.app.tabs.tab_erd import render_erd_tab
from src.app.tabs.tab_agent_workflow import render_agent_workflow_tab
from src.ml.compare_models import run_model_comparison
from src.app.utils import _load_existing_db_tables

# Auto-load existing DB tables on startup
if "db_autoloaded" not in st.session_state:
    try:
        _load_existing_db_tables()
        st.session_state["db_autoloaded"] = True
    except Exception as e:
        print(f"Error auto-loading tables: {e}")

# Render Sidebar (API keys, tools, etc.)
render_sidebar()

# Main Title
st.title("🕵️‍♂️ Fraud Detection AI Workbench")

# --------------------------------------------------------------------------
# HELP OVERLAY LOGIC
# --------------------------------------------------------------------------
if st.session_state.get("help_active") and st.session_state.get("help_file_path"):
    help_path = Path(st.session_state.help_file_path)
    if help_path.exists():
        st.markdown(f"### 📘 Documentation: {help_path.parent.name} / {help_path.name}")
        st.markdown("---")
        try:
            content = help_path.read_text(encoding="utf-8")
            st.markdown(content)
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.error(f"File not found: {help_path}")
    
    # Return early to effectively "overlay" and hide the normal dashboard tabs
    # We add a small footer to remind execution context
    st.markdown("---")
    st.caption("ℹ️ Click 'Close Help' in the sidebar to return to the application.")
    st.stop()
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# DEMO MODE OVERLAY LOGIC
# --------------------------------------------------------------------------
from src.app.demo_mode import render_demo_mode
if st.session_state.get("demo_active"):
    render_demo_mode()
    st.stop()
# --------------------------------------------------------------------------

# Create Tabs
tab_names = [
    "📁 Upload Data",
    "📈 ML Dashboard",
    "🧠 SQL RAG",
    "💬 KB RAG",
    "🧭 Graph RAG",
    "⚖️ RAG Comparison",
    "📊 Model Comparison",
    "📋 Guideline Comparison",
    "🤖 ERD Diagram",
    "🤖 Agent Workflow",
]

tabs = st.tabs(tab_names)

# Render Content into Tabs
with tabs[0]:
    render_upload_tab()

with tabs[1]:
    render_ml_dashboard_tab()

with tabs[2]:
    render_sql_rag_tab()

with tabs[3]:
    render_kb_rag_tab()

with tabs[4]:
    render_graph_rag_tab()

with tabs[5]:
    render_rag_comparison_tab()

with tabs[6]:
    try:
        run_model_comparison()
    except Exception as e:
        st.error(f"Error loading Model Comparison: {e}")

with tabs[7]:
    render_guideline_comparison_tab()

with tabs[8]:
    render_erd_tab()

with tabs[9]:
    render_agent_workflow_tab()
