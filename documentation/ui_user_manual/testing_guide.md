# Testing Guide

This document explains how to run unit and integration tests for the Fraud Detection AI Workbench.

## Prerequisites
*   You must be in the project root directory.
*   You must have installed the dependencies (`pip install -r requirements.txt`).
*   You must have `pytest` installed (`pip install pytest`).

## Running Unit Tests
We use `pytest` for all testing. The configuration is stored in `pytest.ini`.

To run all tests:
```bash
pytest tests/
```

To run a specific test file:
```bash
pytest tests/test_rag_sql.py
```

## Test Files Overview
| File | Purpose |
| :--- | :--- |
| `tests/test_rag_sql.py` | Tests the SQL RAG agent logic and database creation. |
| `tests/test_kb_rag.py` | Tests the Knowledge Base retrieval (if available). |
| `tests/test_data_prep.py` | Tests data loading, preprocessing, and splitting logic. |
| `tests/test_graph_rag_unit.py` | Tests graph construction and query parsing. |
| `tests/test_erd_generator.py` | Tests ERD diagram generation (Mermaid & PNG). |

## Integration Testing
The current test suite covers key integration points:
1.  **Database Integration**: `test_rag_sql.py` creates a real SQLite DB from CSV and queries it.
2.  **ML Pipeline**: `test_data_prep.py` verifies the end-to-end data transformation pipeline.
3.  **Graph System**: `test_graph_rag_unit.py` exercises the graph builder and query engine.

## Troubleshooting
*   **Import Errors**: Ensure you are running `pytest` from the **root** folder, not inside `tests/`.
*   **Missing Data**: Ensure `data/raw/Fraud Detection Dataset.csv` exists, as tests rely on it.
