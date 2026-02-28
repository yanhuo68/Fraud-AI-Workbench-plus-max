# UI Design: Sidebar (`sidebar.py`)

## 1. Purpose
The **Sidebar** persists across all tabs and provides global configuration, tools, and administration functions.

## 2. Layout & Structure

### A. API Keys (Expandable)
-   **Inputs**: Password fields for OpenAI, DeepSeek, Google, Anthropic.
-   **Logic**:
    -   Overrides system environment variables for the current session.
    -   Crucial for users who cannot set `.env` files (e.g., hosted deployments).

### B. Tools
1.  **Rebuild KB Index**: 
    -   Triggers `src/rag_sql/build_kb_index.py`.
    -   Logs output to `logs/rebuild_kb.log`.
2.  **Clean DB**:
    -   Deletes SQLite files.
    -   Clears `uploaded_tables` from session state.
3.  **Clean KB**:
    -   Deletes Vector Store (`data/kb`) and Graph Store (`data/graph`).
    -   Clears relevant session/cache keys.
4.  **Rebuild Graph**:
    -   Regenerates the Knowledge Graph.
5.  **Visualize Graph**:
    -   Shortcut to jump to graph visualization options.

### C. Workflow Reference
-   **Image**: Small thumbnail of the ML Pipeline for quick reference.

## 3. Key Logic & State
-   **Global State Management**: Actions here (Clean, Rebuild) affect the persistent storage (`data/`) and global session state, impacting all tabs immediately.
