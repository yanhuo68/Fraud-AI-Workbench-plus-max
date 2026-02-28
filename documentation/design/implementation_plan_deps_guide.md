# Implementation Plan - Dependency Guide Generation

Create a technical document that explains the project's technology stack, detailing each dependency's purpose, usage within the workbench, and versioning.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [NEW] [dependency_guide.md](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/other/guide/dependency_guide.md)
- **Introduction**: The philosophy behind the technology choices for Sentinel.
- **Core Platform Dependencies**:
    - **Streamlit**: Frontend framework and UI orchestration.
    - **Pandas/Numpy**: Data processing and statistical analysis.
- **AI & Agent Orchestration**:
    - **LangChain/LangGraph**: Multi-agent state machine and RAG chaining.
    - **OpenAI**: Core LLM engine for reasoning and generation.
- **Machine Learning Layer**:
    - **Scikit-learn**: Isolation Forest and Random Forest implementation.
- **Data & Knowledge Persistence**:
    - **SQLite/SQLAlchemy**: Relational data storage.
    - **FAISS**: Vector indexing for document RAG.
- **Reporting & Visualization**:
    - **ReportLab/Tabulate**: PDF report generation and LLM interpretation tables.
    - **PyGraphviz**: Graphical workflow rendering.
- **Utilities**: `python-dotenv`, `requests`, `pytest`.

## Verification Plan

### Manual Verification
1.  **File Location**: Verify the file is created at `other/guide/dependency_guide.md`.
2.  **Content Detail**: Ensure each dependency includes "Module", "Why", "How", and "Version".
3.  **Completeness**: Cross-reference with `requirements.txt`.
