# UI Design: ERD Diagram (`tab_erd.py`)

## 1. Purpose
The **ERD Diagram** tab visualizes the schema of the uploaded/loaded relational database tables, showing columns, data types, and relationships (Foreign Keys).

## 2. Layout & Structure

### A. Empty State
-   **Trigger**: No tables loaded.
-   **UI**: Message guiding user to upload data.

### B. Diagram Rendering
-   **Mermaid.js**: Renders text-based ERD definitions into interactive diagrams.
-   **Graphviz (Fallback/Export)**: Optional PNG generation.

### C. Features
-   **Automatic Detection**: Lines are drawn based on `table_pkfk` metadata.
-   **Visual Cues**:
    -   `*` denotes Primary Key.
    -   Arrows (`}o--||`) denote FK relationships (One-to-Many).
-   **Limit Controls**: Slider to limit the number of columns shown per table (for very wide tables).

## 3. Key Logic & State
-   **`table_pkfk`**: The single source of truth for relationships. Populated via `src.app.utils._load_existing_db_tables` (and its auto-detection logic).
-   **Mermaid Generator**: `src.rag_sql.erd_generator.build_mermaid_erd` converts metadata to Mermaid syntax string.
