# Implementation Plan - Graph RAG Refresh Button

## Goal Description
Add a "Refresh" button to the Graph RAG tab to rotate through a larger set of sample questions. This aligns the user experience with the SQL and KB RAG tabs and encourages broader exploration of the knowledge graph.

## User Review Required
None.

## Proposed Changes

### `app/tabs/tab_graph_rag.py`

#### [MODIFY] [tab_graph_rag.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/tabs/tab_graph_rag.py)
1.  **Expand Question Pool**: Define a larger list of ~20 static sample questions focusing on graph-centric queries (relationships, central entities, document references, etc.).
2.  **Random Sampling**: Implement logic to pick 5 random questions from the pool.
3.  **Refresh Mechanism**:
    - Use `st.session_state` to store the current batch of 5 questions.
    - Add a "Refresh" button that updates this session state entry and reruns the app.
4.  **UI Update**: Place the refresh button next to the question picker.

## Verification Plan

### Manual Verification
1.  **Load Graph RAG Tab**: Verify 5 questions differ from the full list (random subset).
2.  **Click Refresh**: Verify the list of questions in the dropdown changes.
3.  **Select & Ask**: Verify selecting a refreshed question and asking it still works.
