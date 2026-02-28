# Implementation Plan - SQL RAG Intent Correction

Address the issue where AI-suggested questions are misclassified as `NO_SQL` (documentation/workflow) instead of generating data queries.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **`generate_sql_sample_questions`**:
    - Update the prompt to explicitly instruct the LLM to generate **"specifically answerable by a single SQLite SELECT statement"** questions.
    - Discourage abstract analytical terms like "correlate" or "overall patterns" in suggested questions.
    - Encourage concrete requests: "What is the average X...", "Show me top 10 Y...", "Count frauds where Z...".

#### [MODIFY] [rag_sql/langgraph_flow.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/rag_sql/langgraph_flow.py)
- **`sql_planner`**:
    - Refine the system prompt to clarify that any question about **data distribution, specific rows, or metrics** MUST result in a SQL query.
    - `NO_SQL` should ONLY be used for questions about "how the app works", "what is this code", or general documentation.
    - Add a instruction: "If a question is complex (e.g., correlation), generate a query that retrieves relevant summary statistics (e.g., averages or counts) to help the user."

## Verification Plan

### Manual Verification
1.  **Regenerate Questions**: Click "Refresh Analysis Prompts" in the SQL RAG tab. Verify the new questions are more concrete (e.g., "What is the average V1 value for frauds?").
2.  **Run Suggested Questions**: Click one of the new suggested questions and run SQL RAG. Verify it now results in a valid SQL query and displayed data instead of `NO_SQL`.
3.  **Ambiguity Test**: Ask a documentation question (e.g., "How does the caching work?") and verify it still correctly returns `NO_SQL` (or the equivalent error message).
