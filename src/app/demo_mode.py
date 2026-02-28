import streamlit as st
from pathlib import Path

# Mapping of directory names to Display Titles
# Order matters here - this determines the order of the slideshow
TAB_MAPPING = {
    "upload_data": "📁 Upload Data",
    "ml_dashboard": "📈 ML Dashboard",
    "sql_rag": "🧠 SQL RAG",
    "kb_rag": "💬 KB RAG",
    "graph_rag": "🧭 Graph RAG",
    "rag_comparison": "⚖️ RAG Comparison",
    "model_comparison": "📊 Model Comparison",
    "guideline_comparison": "📋 Guideline Comparison",
    "erd_diagram": "📊 ERD Diagram",
    "agent_workflow": "🤖 Agent Workflow"
}

def load_slides():
    """
    Scans documentation/screen/ for images and builds a flat list of slides.
    Returns: list of dicts {'tab_name': str, 'image_path': Path, 'title': str}
    """
    slides = []
    base_dir = Path("documentation/screen")
    
    if not base_dir.exists():
        return []

    # Iterate through tabs in the defined order
    for dir_name, display_title in TAB_MAPPING.items():
        tab_dir = base_dir / dir_name
        if tab_dir.exists() and tab_dir.is_dir():
            # Get all png files, sorted by name
            images = sorted(list(tab_dir.glob("*.png")))
            for img in images:
                slides.append({
                    "tab_name": dir_name,
                    "title": display_title,
                    "image_path": img,
                    "image_name": img.name
                })
    
    return slides

def render_demo_mode():
    """
    Renders the Demo Mode overlay.
    """
    st.markdown("## 🎥 Application Demo Tour")
    st.markdown("---")

    slides = load_slides()
    
    if not slides:
        st.error("No demo screenshots found in `documentation/screen/`.")
        if st.button("❌ Close Demo", use_container_width=True):
            st.session_state.demo_active = False
            st.rerun()
        return

    # Initialize step if not present
    if "demo_step" not in st.session_state:
        st.session_state.demo_step = 0

    # Ensure step is within bounds
    current_step = st.session_state.demo_step
    if current_step < 0: current_step = 0
    if current_step >= len(slides): current_step = len(slides) - 1
    st.session_state.demo_step = current_step

    slide = slides[current_step]

    # Top Navigation Bar
    col_prev, col_info, col_next, col_close = st.columns([1, 4, 1, 1])
    
    with col_prev:
        if st.button("⬅️ Previous", key="demo_prev", disabled=(current_step == 0), use_container_width=True):
            st.session_state.demo_step -= 1
            st.rerun()
            
    with col_next:
        if st.button("Next ➡️", key="demo_next", disabled=(current_step == len(slides) - 1), use_container_width=True):
            st.session_state.demo_step += 1
            st.rerun()
            
    with col_close:
        if st.button("❌ Close", key="demo_close", use_container_width=True):
            st.session_state.demo_active = False
            st.rerun()

    with col_info:
        progress = (current_step + 1) / len(slides)
        st.progress(progress)
        st.caption(f"Slide {current_step + 1} of {len(slides)}")

    # Main Content
    st.header(f"{slide['title']}")
    
    # Display Image
    st.image(str(slide['image_path']), width="stretch")
    
    # Check for accompanying description text file (e.g. 1.txt for 1.png)
    txt_path = slide['image_path'].with_suffix(".txt")
    if txt_path.exists():
        st.info(txt_path.read_text(encoding="utf-8"))
    else:
        # Default description if no text file
        st.caption(f"Screenshot: {slide['image_name']}")

    st.markdown("---")
    # Duplicate Nav at bottom for convenience
    b_col_prev, b_col_space, b_col_next = st.columns([1, 4, 1])
    with b_col_prev:
        if st.button("⬅️ ", key="demo_prev_btm", disabled=(current_step == 0), use_container_width=True):
            st.session_state.demo_step -= 1
            st.rerun()
    with b_col_next:
        if st.button(" ➡️", key="demo_next_btm", disabled=(current_step == len(slides) - 1), use_container_width=True):
            st.session_state.demo_step += 1
            st.rerun()
