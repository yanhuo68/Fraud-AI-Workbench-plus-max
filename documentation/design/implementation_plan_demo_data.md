# Implementation Plan - Demo Data Selection

Add a feature to the "Upload Data" tab that allows users to select and load demo datasets from the `data/raw/` directory.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- Create a helper function `load_and_persist_dataset(df, filename)` to handle:
    - Setting `st.session_state["uploaded_df"]`.
    - Clearing related session state cache (`ml_unsup_scores`, etc.).
    - Writing to the SQLite `transactions` table.
    - Logging and showing UI success messages.
- Update the existing `st.file_uploader` logic to use this helper.
- Add a new section under "Upload Data" labeled "Select Demo Dataset":
    - Use `Path("data/raw").glob("*.csv")` to list available files.
    - Add a `st.selectbox` to pick a file.
    - Add a `st.button("Upload Demo")` that reads the selected file and calls the helper function.

## Verification Plan

### Manual Verification
1.  **Standard Upload**: Upload a CSV file via `file_uploader`. Verify it still works and persists to the DB.
2.  **Demo Upload**: Select `Fraud Detection Dataset.csv` from the selectbox and click "Upload Demo".
    - Verify the data is loaded and displayed.
    - Verify the "ML Dashboard" tab shows the demo data.
    - Verify the SQLite database is updated.
