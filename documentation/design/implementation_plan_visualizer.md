# Implementation Plan - Agent Workflow Visualizer

Enhance the "Agent Workflow Visualizer" tab by adding support for real graphical plotting of the agent workflows, moving beyond simple Mermaid text strings.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [Dockerfile](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/Dockerfile)
- Add `graphviz` and `graphviz-dev` to the `apt-get install` list.
- This is required for LangGraph to render graphs as images.

#### [MODIFY] [requirements.txt](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/requirements.txt)
- Add `pygraphviz` (or `graphviz`) to the dependencies.

#### [MODIFY] [agents/graph_visualizer.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/agents/graph_visualizer.py)
- Add a new function `get_graph_image(graph)`:
    - It will call `graph.get_graph().draw_mermaid_png()` if the graph supports it.
    - Fallback to Mermaid text if image generation fails.

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- In the `tab_agent_visualizer` section:
    - Attempt to display the workflow as an image using `st.image()`.
    - Retain the Mermaid diagram as an expandable alternative.

## Verification Plan

### Manual Verification
1.  **Rebuild Container**: Run `docker compose up --build`.
2.  **Workflow Visualizer**: Navigate to the "Agent Workflow Visualizer" tab.
3.  **Check Image**: Verify that a PNG graph of the selected workflow is displayed.
4.  **Check Mermaid**: Ensure the Mermaid text is still available in the expander.
