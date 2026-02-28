# UI Design: RAG Comparison (`tab_rag_comparison.py`)

## 1. Purpose
The **RAG Comparison** tab allows users to run the *same* question against SQL RAG, KB RAG, and Graph RAG simultaneously to compare accuracy, speed, and content quality.

## 2. Layout & Structure

### A. Input Area
-   **Sample Questions**: Dropdown with curated questions testing different capabilities (Quantitative vs. Qualitative).
-   **Refresh Qs**: Button to generating new test questions via LLM.
-   **Custom Input**: Text area for user specification.
-   **Model Selection**: Choose the "Judge" LLM.

### B. Execution
-   "Run All RAG Methods" Button.
-   Progress bar tracking execution of the three pipelines.

### C. Results Display (3 Columns)
1.  **SQL RAG**: Shows generated SQL + Data Answer.
2.  **KB RAG**: Shows Text Answer + Sources.
3.  **Graph RAG**: Shows Graph Answer + Entity Connections.

### D. Analysis & Metrics
-   **Performance Table**: Side-by-side comparison of Response Time (seconds).
-   **Consistency Analysis**: LLM-generated summary of whether the three methods agree or contradict each other.
-   **Quality Evaluation** (Optional): Deep-dive scoring (Relevance, Completeness) for each answer.

## 3. Key Logic & State
-   **Parallel Execution**: Runs the retrieval functions from `src.rag_sql`, `src.rag_sql.knowledge_base`, and `src.rag_sql.graph_rag`.
-   **Fallback Handling**: Graceful error messages if one method fails (e.g., SQL RAG fails on a conceptual question).
