# UI Design: Agent Workflow (`tab_agent_workflow.py`)

## 1. Purpose
The **Agent Workflow** tab visualizes the internal multi-agent architecture of the Workbench, helping users understand how data flows through the system's components.

## 2. Layout & Structure

### A. Pipeline Visualization
-   **Image**: Displays `docs/ml_pipeline.jpg` (or generated diagram).
-   **Architecture**:
    1.  **Ingestion Layer**: Uploads -> DB/Vector Store.
    2.  **Processing Layer**: ML Models, Graph Building.
    3.  **Reasoning Layer**: SQL Agent, Search Agent, Manager Agent.
    4.  **UI Layer**: Streamlit Interface.

### B. Node Explanations
-   **Interactive Guide**: Detailed text explaining the role of each node (e.g., "What does the Manager Agent do?").

## 3. Key Logic & State
-   **Static Content**: Primarily informational/educational.
-   **Future State**: Plan to make this interactive, showing *live* agent status or logs.
