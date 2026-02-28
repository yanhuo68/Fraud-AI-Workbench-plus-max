# UI Design: Graph RAG (`tab_graph_rag.py`)

## 1. Purpose
The **Graph RAG** tab enables "Global Search" and relationship-based querying. Unlike standard Vector RAG, it understands connections between entities (e.g., User -> Device -> IP) using a Knowledge Graph.

## 2. Layout & Structure

### A. Empty State
-   **Trigger**: If Graph Corpus (`data/graph/graph_corpus.txt`) is missing.
-   **UI**: Warning message guiding user to click "Rebuild Graph" in the sidebar.

### B. Visualization
-   **Graph View**: Interactive network visualization showing:
    -   **Nodes**: Documents, Tables, and Key Concepts.
    -   **Edges**: Relationships/References.
-   **Segments**: Option to view specific sub-graphs (e.g., just the Table relationships, or specific Document groups).

### C. Chat Interface
-   **Input**: Questions about relationships or summaries (e.g., "How are high-risk users connected to specific merchants?").
-   **Output**:
    -   **Answer**: Generated using Graph RAG logic (often traversing moves).
    -   **Graph Context**: Textual description of the paths/subgraphs used.

## 3. Key Logic & State
-   **`graph_store.json`**: Stores the node/edge data.
-   **NetworkX**: Used for graph processing and visualization.
-   **Logic**:
    -   Combines keyword search with graph traversal.
    -   Can "hop" from a user to a transaction to a merchant to detect rings.
