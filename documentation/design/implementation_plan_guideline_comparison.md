# Implementation Plan - Guideline Comparison Tab

## Goal Description
Add a new "Guideline Comparison" tab to the workbench. This tab allows users to select data (tables), choose fraud detection guidelines (with and without "fraud risk" in the title), and use an LLM to analyze the data against these guidelines. It also includes a template-based assessment using `fraud-detection-assessment-template.md` and `fraud-risk-assessment-template.md`, followed by an AI comparison of the results and recommendations.

## User Review Required
None.

## Proposed Changes

### `app/dashboard.py`

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/dashboard.py)
- Import `render_guideline_comparison_tab` from `app.tabs.tab_guideline_comparison`.
- Add "Guideline Comparison" to `tab_names` list, inserting it between "Model Comparison" and "ERD Diagram".
- Add the corresponding `with tabs[...]:` block to render the new tab.

### `app/tabs/tab_guideline_comparison.py`

#### [NEW] [tab_guideline_comparison.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/tabs/tab_guideline_comparison.py)
Create a new file with `render_guideline_comparison_tab` function containing:
1.  **Data Selection**: Sidebar or top section to select uploaded tables (using `st.session_state.uploaded_tables` / `table_dataframes`).
2.  **LLM Selection**: Dropdown to select LLM (reusing `st.session_state.available_llms`) with a Scan button.
3.  **Guideline Selection**:
    -   Scan `docs/` for markdown files.
    -   Filter into two lists:
        -   Start with `fraud` AND contain `risk` -> "Fraud Risk Guidelines"
        -   Start with `fraud` AND NOT contain `risk` -> "Fraud Detection Guidelines"
    -   Two columns with selectboxes for these lists.
4.  **Comparison Action**: "Compare Guideline" button.
5.  **Analysis Logic**:
    -   Retrieve selected table data (sample/head).
    -   Read content of selected guideline files.
    -   Read content of `docs/fraud-detection-assessment-template.md` and `docs/fraud-risk-assessment-template.md`.
    -   Construct prompts for the LLM:
        -   **Prompt 1**: Analyze data using Selected Detection Guideline + Detection Template.
        -   **Prompt 2**: Analyze data using Selected Risk Guideline + Risk Template.
    -   **Prompt 3**: Compare the outputs of Step 1 & 2, highlight commonalities/differences, and provide recommendations for improving the documentation.
6.  **Display**:
    -   Render results in 2 columns (Detection vs Risk Analysis).
    -   Render "AI Insights & Recommendations" below.

## Verification Plan

### Manual Verification
1.  **Start App**: Run `docker compose up --build`.
2.  **Navigate**: Go to the new "Guideline Comparison" tab.
3.  **Select Data**: Ensure tables are loaded (if not, upload a CSV in Upload tab). Select a table.
4.  **Select LLM**: Choose an available LLM.
5.  **Select Guidelines**: Pick one from each dropdown.
6.  **Run Comparison**: Click "Compare Guideline".
7.  **Check Output**:
    -   Verify two columns of analysis appear.
    -   Verify the "AI Insights & Recommendations" section appears and contains relevant text.
