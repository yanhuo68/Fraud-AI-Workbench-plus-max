# Implementation Plan - Global Target Label Mapping

Unify how the "Fraud Label" (target column) is identified and mapped across all workbench components (ML, SQL RAG, and Agents). This addresses the issue where the system warns about missing `isFraud` columns even when a dataset is loaded.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **Tab 1: Upload Data**:
    - Add a "Target Column Mapping" section that appears immediately after a successful upload/select-demo.
    - Provide a selectbox to pick the column that represents the "Fraud" label.
    - Default the selection to `isFraud` if it exists, otherwise `Fraudulent`, or the first column.
    - Store the choice in `st.session_state["target_label_col"]`.
- **Tab 2: ML Dashboard**:
    - Remove the redundant local label mapping logic.
    - Use `st.session_state["target_label_col"]` to rename the column to `isFraud` for processing.
- **SQL RAG Tab**:
    - Update the `ensure_sqlite_db()` internal function to respect the global `target_label_col` when persisting the dataframe to SQLite.
    - This ensures the `transactions` table in SQLite always has an `isFraud` column for the Agents/SQL RAG to query reliably.
- **Dynamic Questions**:
    - Pass the mapped label information to `generate_sql_sample_questions` so the generated prompts are context-aware.

## Verification Plan

### Manual Verification
1.  **Standard Data**: Upload `fraud_data_sample.csv` (has `isFraud`). Verify it's auto-detected and everything works silently.
2.  **Custom Data**: Upload `creditcard.csv` (no `isFraud`). 
    - Verify the "Target Column Mapping" appears in the Upload tab.
    - Select `Class` (common label in creditcard datasets) as the target.
    - Verify **SQL RAG** no longer warns about missing `isFraud`.
    - Verify **ML Dashboard** correctly shows the class balance for `Class` (mapped to `isFraud`).
3.  **Persistence**: Refresh the page and verify the mapping is preserved in the session.
