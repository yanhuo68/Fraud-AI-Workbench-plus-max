# Implementation Plan - Dynamic Sample Questions

Transform the static sample questions into a dynamic system that adapt to the current Knowledge Base and uploaded dataset.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [rag_sql/knowledge_base.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/rag_sql/knowledge_base.py)
- **`generate_kb_sample_questions(llm_id: str, count: int = 5)`**:
    - Query the vector store for a broad range of content (e.g., using a query like "fraud detection overview").
    - Use the retrieved context to ask the LLM to generate `count` interesting questions.
    - Return the list of questions.

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **KB Chat Tab**:
    - Add a button "🔄 Generate KB-specific Questions".
    - If clicked (or if no questions exist), call `generate_kb_sample_questions` and store in `st.session_state["dynamic_kb_questions"]`.
    - Update the `selectbox` to pull from this session state.
- **SQL RAG Tab**:
    - Similar logic but use a prompt that includes the **Transaction Table Schema** (columns from the uploaded dataset).
    - Store result in `st.session_state["dynamic_sql_questions"]`.

## Verification Plan

### Manual Verification
1.  **Fresh Start**: Verify the app still shows some default questions if no KB/data exists.
2.  **Dataset Upload**: Upload `creditcard.csv`.
3.  **Generate SQL Questions**: Click regenerate in SQL RAG. Verify questions now mention `V1`, `V2`, `Amount`, `Time` etc. (standard creditcard.csv columns).
4.  **Generate KB Questions**: Click regenerate in KB Chat. Verify questions are derived from your specific `.md` files in `docs/`.
