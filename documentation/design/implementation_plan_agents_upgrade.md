# Implementation Plan - Agents Tab Upgrade

Enhance the Agents tab by replacing hardcoded samples with dynamic, schema-aware questions and adding visual workflow grounding.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **`generate_agent_sample_questions(llm_id, cols)`**: Add a new function similar to the SQL RAG one, but focused on multi-agent collaboration (e.g., "Find patterns and explain them", "Summarize the findings for these columns").
- **Integration**: Add a "Refresh Agent Prompts" button in the Agents tab.

#### [MODIFY] [agents/agents_ui.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/agents/agents_ui.py)
- **`render_agents_ui`**:
    - Update to accept the dynamic sample questions from session state.
    - Integrate `st.session_state["graph_viz"]` or similar to show the workflow structure.
    - Add a "Show Workflow Schema" expander.

#### [MODIFY] [agents/graph_visualizer.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/agents/graph_visualizer.py)
- Ensure the visualizer works with the current LangGraph instance and renders cleanly in Streamlit.

## Verification Plan

### Manual Verification
1. **Dynamic Prompting**: Upload `creditcard.csv`, go to Agents tab, click "Refresh Agent Prompts". Verify questions use `V1-V28` instead of `oldbalanceDest`.
2. **Visual Flow**: Expand the "Workflow Visualization" and verify the LangGraph nodes (sql_planner, executor, critic) are shown.
3. **Execution**: Run a dynamic agent question and check the trace results.
