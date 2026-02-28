# Implementation Plan - SQL Upload & Graph Segmentation

## Goal Description
Restore the missing "Upload & Execute SQL Script" functionality in the Upload Tab and refactor the Graph Visualization to be segmented and displayed in the main content area instead of the sidebar.

## User Review Required
> [!IMPORTANT]
> The sidebar visualization button will be removed. Graph visualization will now be a dedicated section in the Upload Tab.

## Proposed Changes

### `app/tabs/tab_upload.py`

#### [MODIFY] [tab_upload.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/tabs/tab_upload.py)
- **Add SQL File Uploader**: Insert a file uploader for `.sql` files.
- **Add Execute Button**: Implement logic to execute uploaded SQL scripts against `rag1.db`.
- **Update Graph Visualization**:
    - Remove the existing single graph rendering logic.
    - Call the new `visualize_segmented_graph` function from `app/utils.py`.
    - Place this section prominently under "Graph Base Visualization".

### `app/components/sidebar.py`

#### [MODIFY] [sidebar.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/components/sidebar.py)
- **Modify**: The "🎨 Visualize Graph" button behavior.
    - **Old**: Called `visualize_graph_base(st.sidebar)`.
    - **New**: Sets `st.session_state.show_segmented_graph = True`. Does NOT render graph in sidebar.

### `app/utils.py`

#### [MODIFY] [utils.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/utils.py)
- **Add `visualize_segmented_graph` function**:
    - **Logic**:
        - Load `graph_store.json`.
        - **Graph 1 (Tables)**: Filter for nodes where `type == 'table'`.
        - **Graph 2 (MD 1-12)**: Filter for `type == 'document'` and source filename is in the 1st batch of 12 sorted files.
        - **Graph 3 (MD 13-26)**: Filter for `type == 'document'` and source filename is in the 2nd batch.
        - **Graph 4 (MD 27-41)**: Filter for `type == 'document'` and source filename is in the 3rd batch.
        - **Graph 5 (MD 42+)**: Filter for `type == 'document'` and source filename is in the rest.
        - For each segment, create a `NetworkX` graph, add the "Knowledge Base" central node, and render using `matplotlib` (or `st.graphviz_chart` if preferred for cleanliness, but user said "plot graph", usually matplotlib in this app context. `visualize_graph_base` used matplotlib. I will stick to that).

## Verification Plan

### Manual Verification
1.  **SQL Upload**:
    - Create a dummy `.sql` file (e.g., `CREATE TABLE test (id INT);`).
    - Upload it via the new "Upload SQL Script" section.
    - Click "Execute" and verify success message.
2.  **Graph Visualization**:
    - Go to Upload Tab.
    - Scroll to "Graph Base Visualization".
    - Verify 5 distinct graph sections appear (Tables, MD 1-12, etc.).
    - Verify graphs are not "messy" (fewer nodes per graph).
3.  **Sidebar**:
    - Verify "Visualize Graph" button is gone.
