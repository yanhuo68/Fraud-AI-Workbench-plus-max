# Implementation Plan - KB Demo Questions and Logging Sync Fix

Resolve the persistent logging `KeyError` and add demo questions to the Knowledge Base Chat tab.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **Version Banner**: Add a `st.sidebar.info("Code Version: 1.0.2")` to help verify that the latest edits are active in the Docker container.
- **Logging Fix**: Perform a case-sensitive global search and replace for any `extra` dictionary keys named `"filename"`. Ensure `load_and_persist_dataset` uses a completely unique name for its extra payload.
- **KB Demo Questions**:
    - Update `tab_kb_chat` to include a `st.selectbox` for sample questions.
    - Sample questions:
        - "What are the key fields in the online payments fraud dataset?"
        - "Explain the 'Transfer -> Cash-out' fraud chain."
        - "What is 'Account Takeover' in the context of fraud?"
        - "Define Pattern B: Zero-Balance Manipulation."
        - "How are LLMs used in this project?"
    - Selecting a question should populate the `st.text_area` for the KB chat.

## Verification Plan

### Manual Verification
1.  **Check Sync**: Verify the sidebar shows "Code Version: 1.0.2". If it doesn't, the volume mount is not working.
2.  **KB Demo Questions**: In the "KB Chat" tab, select a sample question. Verify it populates the input field and can be sent to the AI.
3.  **Data Upload**: Test "Upload Demo" again. Verify no `KeyError` occurs.
