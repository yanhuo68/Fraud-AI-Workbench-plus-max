# Implementation Plan - Security Fixes

Address the critical security risks identified in the risk assessment: LLM-driven SQL Injection and potential API key exposure in logs.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [NEW] [security.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/utils/security.py)
- **`validate_sql_query(sql: str)`**:
    - Use regex to ensure the query starts with `SELECT`.
    - Check for forbidden keywords: `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, `GRANT`, `REVOKE`.
    - Raise a `SecurityViolation` if the query is unsafe.

#### [MODIFY] [langgraph_flow.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/rag_sql/langgraph_flow.py)
- Import `validate_sql_query`.
- Call it within the `sql_executor` node before running `cur.execute(sql)`.
- Gracefully handle validation errors and return them in the state.

#### [MODIFY] [logging_conf.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/config/logging_conf.py)
- Implement `SensitiveDataFilter(logging.Filter)`:
    - Use regex to identify patterns that look like API keys (e.g., `sk-[a-zA-Z0-9]{32,}`).
    - Replace identified keys with `[MASKED]`.
- Attach this filter to all handlers in `setup_logging`.

## Verification Plan

### Automated Tests
1.  **SQL Validation Test**: Create a test script that tries to execute `DROP TABLE` and `DELETE` via the RAG flow and verify it is blocked.
2.  **Log Masking Test**: Log a dummy API key and verify that the output in `logs/app.log` is masked.

### Manual Verification
1.  **App Testing**: Run a normal SQL RAG query to ensure safe queries still work.
2.  **Negative Testing**: Try to "jailbreak" the RAG prompt in the UI to perform a data mutation and ensure it fails.
