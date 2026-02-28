# rag_sql/sql_utils.py

"""
Utilities for executing SQL against the SQLite database used by SQL RAG.
"""

from pathlib import Path
from typing import Tuple, List, Any

import sqlite3
import pandas as pd

DEFAULT_DB_PATH = Path("data/db/fraud.db")


def run_sql_query(
    query: str,
    db_path: Path = DEFAULT_DB_PATH,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Execute a SQL query and return:
    - DataFrame of results
    - List of column names

    Raises sqlite3.Error if SQL is invalid.
    """
    conn = sqlite3.connect(str(db_path))
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    cols = list(df.columns)
    return df, cols
