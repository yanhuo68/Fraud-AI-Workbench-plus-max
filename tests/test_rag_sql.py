# tests/test_rag_sql.py
from src.rag_sql.db_init import create_db_from_csv, DB_PATH
from src.rag_sql.langgraph_flow import ask_sql
from pathlib import Path
import sqlite3

def test_db_created():
    create_db_from_csv("data/raw/Fraud Detection Dataset.csv")
    assert Path(DB_PATH).exists()

def test_simple_sql_agent():
    create_db_from_csv("data/raw/Fraud Detection Dataset.csv")
    state = ask_sql("Show 3 rows of the transactions table.")
    assert state["error"] is None
    assert state["result"] is not None
    assert len(state["result"]) <= 3  # LLM often uses LIMIT 3
