# Testing Guide

## Local test runs
```bash
pip install -r requirements.txt
pytest -q
```

## Test coverage (current suite)
- `tests/test_graph_rag_unit.py`  
  - Builds a simple graph corpus and queries it (embeddings off for speed).  
  - Verifies structured filter parsing.
- `tests/test_erd_generator.py`  
  - Generates Mermaid ERD with FK arrows.  
  - Builds an ERD PNG and checks the file exists.
- `tests/test_data_prep.py`  
  - Loads the raw fraud CSV and runs `preprocess`; asserts shapes are consistent.
- `tests/test_rag_sql.py`  
  - Creates DB from the raw CSV.  
  - Runs a simple SQL agent query and checks result/error handling.
- `tests/loaddata_test.py`  
  - Creates DB from raw CSV and issues a sample agent SQL question (smoke).

## Running targeted tests
```bash
pytest tests/test_graph_rag_unit.py
pytest tests/test_erd_generator.py::test_build_mermaid_and_png_with_fk
```

## Notes
- ERD tests require `graphviz` installed (included in Dockerfile).  
- Graph RAG unit test forces embeddings off to keep runtime light.  
- Some tests depend on `data/raw/Fraud Detection Dataset.csv`; ensure it exists.  
- LLM-dependent flows are not covered by the unit tests; they require API keys/local models.  
- `python -m py_compile app/dashboard.py ml/compare_models.py rag_sql/erd_generator.py` can be used as a quick sanity check.
