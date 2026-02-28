# Implementation Plan - Fix Guideline Comparison State

## Goal Description
Fix a bug where the "Guideline Comparison" tab reportedly uses stale guideline selections on subsequent runs. Refactor the tab to store analysis results in `st.session_state`, ensuring the displayed results are explicitly managed and persist correctly across reruns, independent of the button's momentary state.

## User Review Required
None.

## Proposed Changes

### `app/tabs/tab_guideline_comparison.py`

#### [MODIFY] [tab_guideline_comparison.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/tabs/tab_guideline_comparison.py)
1.  **Session State for Results**: Introduce `st.session_state["gc_results"]` to store the output dictionaries (responses, filenames used).
2.  **Button Logic**:
    -   When "Compare Guidelines" is clicked:
        -   Read prompt inputs directly from `st.session_state[key]` where possible.
        -   Run the LLM analysis.
        -   Update `st.session_state["gc_results"]`.
3.  **Rendering Logic**:
    -   Outside the button block, check if `gc_results` exists.
    -   Render results from this state variable.
    -   Add a "Clear Results" or explicit override behavior (implicit in the update).

## Verification Plan

### Manual Verification
1.  **Load Tab**: Go to Guideline Comparison.
2.  **Run 1**: Select Guideline A and B. Click Compare. Verify results match A and B.
3.  **Run 2**: Select Guideline C and D (changing the dropdowns).
    -   Verify results from Run 1 *might* still be visible (optional, but desired) OR disappear (if we clear them).
    -   Click Compare.
4.  **Verify Run 2**: Ensure the new results match C and D.
