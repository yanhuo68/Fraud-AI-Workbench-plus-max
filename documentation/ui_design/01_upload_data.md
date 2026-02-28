# UI Design: Upload Data Tab (`tab_upload.py`)

## 1. Purpose
The **Upload Data** tab serves as the entry point for the Fraud Detection AI Workbench. It allows users to ingest data from various sources (CSV uploads, Demo datasets) and execute SQL scripts to set up the relational database schema.

## 2. Layout & Structure

### A. Quick Start: Load Demo Dataset
-   **Component**: Dropdown (`st.selectbox`) + "Load Demo" Button (`st.button`).
-   **Functionality**:
    -   Scans `data/raw/*.csv` automatically.
    -   Loads the selected CSV into `st.session_state.uploaded_df`.
    -   Saves the file to `data/uploads/`.
    -   Ingests the data into the SQLite database (`data/db/rag1.db`).
    -   Auto-detects Primary Keys (PK) and Foreign Keys (FK).
    -   Registers the table in session state (`uploaded_tables`).

### B. Upload Your Own CSV
-   **Component**: File Uploader (`st.file_uploader`).
-   **Functionality**:
    -   Accepts multiple CSV files.
    -   Performs robustness checks (empty files, parsing errors).
    -   Ingests valid files into the database.
    -   Updates the table registry.

### C. Load Demo SQL Schema
-   **Component**: Multi-select (`st.multiselect`) + "Execute Demo SQL" Button.
-   **Functionality**:
    -   Scans `data/raw/use_case/*.sql` (e.g., `create_tables.sql`, `insert_data.sql`).
    -   Displays file previews (first 5 lines/comments).
    -   Executes selected scripts against the SQLite database.
    -   **Critical**: Triggers `_load_existing_db_tables()` which now includes **automatic PK/FK relationship detection**.

### D. Upload & Execute SQL Script
-   **Component**: File Uploader (`.sql`) + Execute Button.
-   **Functionality**: Allows ad-hoc execution of custom SQL scripts to modify the database schema.

### E. Graph Base Visualization
-   **Component**: Button/Toggle.
-   **Functionality**:
    -   Displays the segmented Knowledge Graph if built.
    -   Segments visualized: Tables, Documents (chunked).

## 3. Key Logic & State
-   **`uploaded_tables`**: Dict storing loaded table names and their schema file paths.
-   **`table_dataframes`**: Dict storing the actual DataFrames for loaded tables.
-   **`table_pkfk`**: metadata dict storing PK/FK relationships (Critical for ERD and RAG).
-   **Auto-Ingestion**: The tab handles the logic of converting raw CSVs into SQL tables and auto-generating markdown schemas in `docs/`.
