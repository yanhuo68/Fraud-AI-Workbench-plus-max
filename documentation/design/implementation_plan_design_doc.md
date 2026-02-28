# Implementation Plan - Technical Design Document

Create a deep-dive technical design document that explains the internal architecture and front-to-back integration of the Sentinel Fraud AI workbench.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [NEW] [design_document.md](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/other/manual%20guide/design_document.md)
- **High-Level Architecture**: Mermaid diagram showing the interaction between Streamlit (Frontend), Python Logic (Middleware), and Database/LLM layers (Backend).
- **Core Design Patterns**: Dependency injection for LLM providers, Session State management for data continuity.
- **Detailed Integration by Tab**:
    - **Data Management**: CSV -> Pandas -> SQLite pipeline.
    - **ML Pipeline**: Feature engineering -> Model inference -> Interpreted results.
    - **SQL RAG Loop**: Prompt Engineering -> SQL Generation -> DB Execution -> Natural Language Response.
    - **KB RAG Engine**: Vector Indexing -> Semantic Search -> Augmented Generation.
    - **Multi-Agent Orchestration**: LangGraph State Machine -> Node Execution -> Edge Routing.
- **Workflow Visualization**: Diagramming how the visualizer extracts the LangGraph DAG.

## Verification Plan

### Manual Verification
1.  **File Existence**: Verify the file is created at `other/manual guide/design_document.md`.
2.  **Diagram Rendering**: Ensure all Mermaid diagrams are syntactically correct and render as expected.
3.  **Technical Accuracy**: Cross-reference description with the codebase.
