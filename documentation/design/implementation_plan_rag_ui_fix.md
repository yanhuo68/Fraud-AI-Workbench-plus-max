# Implementation Plan - Fix RAG Comparison UI Sync

## Goal Description
Fix a bug in the RAG Comparison tab where the "Question for all RAG methods" text area fails to update when the user selects a sample question or clicks the "Refresh" button. This is caused by Streamlit's state persistence behavior for widgets with defined keys.

## User Review Required
None.

## Proposed Changes

### `app/tabs/tab_rag_comparison.py`

#### [MODIFY] [tab_rag_comparison.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/tabs/tab_rag_comparison.py)
1.  **Define Callback**: Create `update_comp_input()` to sync the selectbox value to the text area's session state.
2.  **Bind Callback**: Add `on_change=update_comp_input` to the sample question `selectbox`.
3.  **Update Refresh Logic**: explicitily set `st.session_state["comp_question_input"]` to the first new question when the refresh button is clicked.

## Verification Plan

### Manual Verification
1.  **Load RAG Comparison**: Select a different question from the dropdown. Verify text area updates.
2.  **Type in Text Area**: Verify manual typing still works.
3.  **Click Refresh**: Verify the text area updates to the first question of the new batch.
4.  **Select After Refresh**: Verify selecting from the new batch updates the text area.
