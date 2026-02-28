# UI Design: KB RAG (`tab_kb_rag.py`)

## 1. Purpose
The **KB RAG (Knowledge Base)** tab enables users to chat with unstructured documents (policy manuals, investigation guidelines, reports) uploaded to the `docs/` directory.

## 2. Layout & Structure

### A. Empty State
-   **Trigger**: If Knowledge Base index (`data/kb/faiss_index`) is missing.
-   **UI**: Warning message guiding user to click "Rebuild KB Index" in the sidebar.

### B. Chat Interface
-   **Input**: Text input for questions (e.g., "What is the policy for handle high-value crypto transactions?").
-   **Refesh Questions**: Button to generate sample questions based on document content using LLM.
-   **Output**:
    -   **Answer**: LLM-generated response grounded in the retrieved documents.
    -   **Sources**: Collapsible "Context" section showing exact snippets and filenames used to generate the answer.
    -   **Citations**: Inline references to source documents.

## 3. Key Logic & State
-   **FAISS Index**: Vector store located at `data/kb/`.
-   **Retriever**: Uses `langchain` and `OpenAIEmbeddings` to find relevant chunks.
-   **RAG Pipeline**: 
    1.  User query -> Embedding.
    2.  Vector search -> Top K chunks.
    3.  LLM Generation -> Answer based ONLY on context.
