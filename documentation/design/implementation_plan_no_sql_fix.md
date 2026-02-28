# Implementation Plan - Eliminating NO_SQL Hallucinations

Solve the issue where the SQL RAG Agent returns `NO_SQL` for natural language questions by refining the intent classification and grounding instructions.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [rag_sql/langgraph_flow.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/rag_sql/langgraph_flow.py)
- **`sql_planner` Prompt**:
    - Re-introduce clear criteria for `NO_SQL`: Only use it for questions about software features, UI help, or non-data documentation.
    - Add a "Schema-First" rule: "If the question mentions any available columns or general data properties (counts, averages, etc.), you MUST attempt a SQL query."
    - explicitly state: "NEVER use `is_anomaly`—always use `isFraud` for fraud-related queries."
    - Remove the "Respond with ONLY the query or 'NO_SQL'" ambiguity.

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **`generate_sql_sample_questions`**:
    - Update the prompt to include 2-3 **concrete examples** of good natural language questions (e.g., "What is the average V1 value where isFraud is 1?").
    - Explicitly demand questions that focus on specific, detectable column names.
    - Ensure the suggested questions avoid analytical "wish-list" terms like "correlations" which confuse the SQL planner.

## Verification Plan

### Manual Verification
1. **Regenerate Samples**: Verify questions like "Find the top 5 transactions by amount for isFraud=1" are generated.
2. **Execute Samples**: Click a sample and Run SQL RAG. Verify it generates a valid SELECT query instead of `NO_SQL`.
3. **Invalid Request**: Ask "How do I change the theme?" and verify it correctly returns `NO_SQL`.
