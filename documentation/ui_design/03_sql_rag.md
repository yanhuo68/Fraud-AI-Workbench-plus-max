# UI Design: SQL RAG (`tab_sql_rag.py`)

## 1. Purpose
The **SQL RAG** tab allows users to query relational data using natural language. It translates English questions into valid SQL queries, executes them against the SQLite database, and visualizes the results.

## 2. Layout & Structure

### A. Empty State
-   **Trigger**: If no tables are uploaded (`uploaded_tables` is empty).
-   **UI**: Friendly "No data uploaded" message with next steps.

### B. Sidebar Controls
-   **Table Selection**: Checkboxes to select which tables to query (context window optimization).
-   **LLM Selection**: Dropdown to choose the model (OpenAI, DeepSeek, Local LLM).

### C. Chat Interface
-   **Input**: Text area for natural language query (e.g., "How many high-risk users are there in NY?").
-   **Output**: 
    -   **Generated SQL**: Collapsible code block showing the raw SQL.
    -   **Data Table**: Interactive dataframe of the results.
    -   **Visualization**: Auto-generated Plotly chart (Bar, Line, Pie) if applicable.
    -   **Answer**: Text synthesis explaining the findings.

### D. Advanced Features
-   **Clean SQL**: The system validates and fixes common SQL syntax errors (e.g., Markdown stripping).
-   **Retry Logic**: Automatic retries on SQL execution failure.
-   **Session State Safety**: Robust error handling for cases where the DB is cleaned mid-session.

## 3. Key Logic & State
-   **`uploaded_tables`**: Used to build the schema context for the LLM.
-   **`chat_history`**: Stores Q&A pairs.
-   **SQL Generation**: Uses `src.rag_sql.sql_generator` to construct prompts with schema definitions.
-   **Execution**: Uses `sqlite3` to run queries safely (read-only mode enforced where possible).
