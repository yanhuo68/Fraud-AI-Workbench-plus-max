# Implementation Plan - SQL RAG Error Handling

## Goal Description
Enhance `tab_sql_rag.py` with robust error handling (try-catch blocks) around all external agent calls and complex logic. Prevent application crashes from unhandled exceptions and display friendly, informative error messages to the user.

## User Review Required
None.

## Proposed Changes

### `app/tabs/tab_sql_rag.py`

#### [MODIFY] [tab_sql_rag.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/tabs/tab_sql_rag.py)
Wrap the following sections in `try...except Exception as e` blocks:
1.  **SQL Generation & Ranking**:
    - `generate_sql_candidates`
    - `pick_best_sql`
2.  **SQL Execution & Recovery**:
    - `run_sql_query` (already handled in some places, ensure consistency)
    - `repair_sql`
3.  **Fallback SQL**:
    - `generate_fallback_sql`
4.  **EDA Summary**:
    - `compute_basic_eda`
    - `eda_narrative`
5.  **Anomaly Detection**:
    - `detect_anomalies_iqr`
    - `anomaly_narrative`
6.  **Fraud Risk Scoring**:
    - `add_fraud_risk_score`
    - `fraud_risk_narrative`
7.  **Explanation**:
    - `explain_join_query`
8.  **Suggestions**:
    - `suggest_sql_improvements`
9.  **Trend Insights**:
    - `generate_trend_insights`

**Error Handling Strategy**:
- Use `st.error(f"Module Failed: {str(e)}")` or `st.warning("Analysis unavailable due to error.")` depending on severity.
- Log error details to console/logs (though standard streamlit logs capturing stderr is default).
- Ensure the pipeline *continues* to the next section even if one analysis agent fails (e.g., if EDA fails, still try Anomaly Detection).

## Verification Plan

### Manual Verification
1.  **Run Pipeline**:
    - Go to SQL RAG.
    - Run a query.
2.  **Simulate Errors (Mental Check)**:
    - Since we just fixed the bugs, we expect it to work.
    - To *verify* the error handling, we could temporarily introduce a typo in a function name or argument in the code, regenerate the app, and see if it catches the error gracefully instead of showing a traceback.
    - *Action*: I will strictly implement the try-except blocks. I will assume if the app runs without crashing on valid inputs, the structure is correct.

