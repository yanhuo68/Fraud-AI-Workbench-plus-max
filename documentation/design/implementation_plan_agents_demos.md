# Implementation Plan - Agents Demo Questions

Add a feature to the "Agents" tab that allows users to select from a list of sample questions to exercise the multi-agent workflows.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [agents/agents_ui.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/agents/agents_ui.py)
- Inside `render_agents_ui()`:
    - Add a `st.selectbox` for "Pick a sample question (optional)".
    - Define a list of sample questions tailored for multi-agent workflows.
    - Update the `user_query` logic to prioritize the selected sample if it's not the default "-- choose --".
    - Populate the `text_area` or use the selection as the query for the workflow.

## Verification Plan

### Manual Verification
1.  **Agents Tab**: Navigate to the "Agents" tab.
2.  **Sample Selection**: Select a question from the new dropdown.
3.  **Run Workflow**: Click "Run Agents" and verify the selected question is used and the workflow executes.
4.  **Custom Input**: Verify that custom text input still works if no sample is selected.
