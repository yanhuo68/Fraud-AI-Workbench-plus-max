# Implementation Plan - Refactoring dashboard.py

## Goal
Decompose the monolithic `dashboard.py` (3600+ lines) into a modular, maintainable architecture by extracting tabs and components into separate files.

## Proposed Structure

```
app/
├── dashboard.py           # Main entry point (reduced to ~100 lines)
├── utils.py               # Shared utility functions
├── components/
│   ├── __init__.py
│   └── sidebar.py         # Sidebar logic
└── tabs/
    ├── __init__.py
    ├── tab_upload.py
    ├── tab_ml_dashboard.py
    ├── tab_sql_rag.py
    ├── tab_kb_rag.py
    ├── tab_graph_rag.py
    ├── tab_rag_comparison.py
    ├── tab_model_comparison.py
    └── tab_erd.py
```

## Step-by-Step Refactoring


### Phase 1: Infrastructure Setup (COMPLETED)
1.  [x] Create directories: `app/tabs`, `app/components`.
2.  [x] Create `app/utils.py` and move helper functions:
    *   `rebuild_graph_base`
    *   `_write_schema_md`
    *   `_load_existing_db_tables`
    *   `parse_structured_filters`

### Phase 2: Component Extraction (COMPLETED)
1.  [x] **Sidebar**: Move sidebar logic (API keys, tools, KB rebuild) to `app/components/sidebar.py`.
    *   Created function `render_sidebar()`.

### Phase 3: Tab Extraction (COMPLETED)
For each tab, create a file in `app/tabs/` with a `render_*_tab()` function, moving the relevant code and imports.

1.  [x] **Upload Tab** -> `app/tabs/tab_upload.py`
2.  [x] **ML Dashboard** -> `app/tabs/tab_ml_dashboard.py`
3.  [x] **SQL RAG** -> `app/tabs/tab_sql_rag.py`
4.  [x] **KB RAG** -> `app/tabs/tab_kb_rag.py`
5.  [x] **Graph RAG** -> `app/tabs/tab_graph_rag.py`
6.  [x] **RAG Comparison** -> `app/tabs/tab_rag_comparison.py`
7.  [x] **Model Comparison** -> `app/tabs/tab_model_comparison.py` (Handled via import)
8.  [x] **ERD Tab** -> `app/tabs/tab_erd.py`

### Phase 4: Main Dashboard Cleanup (COMPLETED)
1.  [x] Update `dashboard.py` to:
    *   Import `render_sidebar` and tab render functions.
    *   Initialize session state (LLMs, tables).
    *   Call `render_sidebar()`.
    *   Setup `st.tabs` and call respective render functions.

## Verification Plan

### Automated Tests
*   [x] Verified syntax with `py_compile`.
*   [x] Verified file creation and content integrity.

### Manual Verification
1.  **Startup**: Launch app, ensure no import errors.
2.  **Tab Navigation**: Click through each tab (Upload, ML, SQL RAG, etc.) to ensure content renders.
3.  **Functionality Check**:
    *   Run a simple SQL RAG query.
    *   Run a KB RAG query.
    *   Check if sidebar tools (like "Scan") still work.

## Risk Management (Addressed)
*   **Import Errors**: Checked with `py_compile`, fixed missing `__init__.py`.
*   **Session State**: Preserved logic using `st.session_state`.
