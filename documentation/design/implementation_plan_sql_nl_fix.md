# Implementation Plan - SQL RAG Natural Language & Schema Grounding

Fix two critical issues in the SQL RAG assistant:
1. Sample questions being generated as SQL code instead of natural language.
2. SQL Planner hallucinating columns like `is_anomaly` and using invalid Date math for the dataset.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **`generate_sql_sample_questions`**:
    - Update prompt to explicitly demand **"Natural Language, human-readable questions only"**.
    - Explicitly forbid any SQL code, backticks, or programming syntax in the returned questions.
    - Remind the LLM to use the mapped fraud column name (e.g., `isFraud`).

#### [MODIFY] [rag_sql/langgraph_flow.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/rag_sql/langgraph_flow.py)
- **`sql_planner`**:
    - Tighten the system prompt even further.
    - Rule: **"NEVER use columns not listed in the Available columns. Specifically, do NOT use 'is_anomaly', 'date', or 'timestamp' if they are missing."**
    - Rule: **"For creditcard.csv datasets, the 'Time' column is a FLOAT representing seconds, NOT a DATE. Do NOT use DATE() functions on it."**
    - Strengthen the mapping of "Fraud" to the available `isFraud` column.

## Verification Plan

### Manual Verification
1. **Refresh Prompts**: Click "Refresh Analysis Prompts" in SQL RAG. Verify questions are natural language (e.g., "How many frauds occurred...").
2. **Run Questions**: Select a question and Run SQL RAG. Verify the generated SQL uses `isFraud` and legitimate columns from the schema, with no date-math errors.
3. **Check Results**: Verify the query returns actual data (not 0 results due to hallucinated filters).
