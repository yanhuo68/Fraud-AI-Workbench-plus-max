# agents/sql_ranking_agent.py

"""
JOIN SQL Ranking Agent

Responsible for:
- Generating multiple JOIN SQL candidates
- Executing each candidate safely
- Scoring each result
- Selecting the best SQL
"""

from typing import List, Dict, Tuple
import pandas as pd
from src.agents.llm_router import init_llm
from src.rag_sql.sql_utils import run_sql_query
import streamlit as st


# -----------------------------------------------------
# 1. Generate Multiple JOIN SQL candidates
# -----------------------------------------------------
def generate_sql_candidates(question: str, llm_id: str, schema_text: str, k: int = 3) -> List[str]:
    """
    Generate multiple JOIN SQL queries using LLM.
    """

    llm = init_llm(llm_id)

    prompt = f"""
You are an expert SQL generator. The user asked:

{question}

You MUST obey:
- Use ONLY tables and columns in the schema below.
- Prioritize JOIN queries if there are foreign key relationships.
- Produce SQLite-compatible SQL.
- Return ONLY SQL queries with no commentary.
- Generate {k} DIFFERENT valid SQL queries.

Schema and ERD information:
{schema_text}

Return queries separated by:

===ENDSQL===
"""

    resp = llm.invoke(prompt).content.strip()

    # split into separate SQL queries
    candidates = [
        x.strip().replace("```sql", "").replace("```", "") 
        for x in resp.split("===ENDSQL===") 
        if x.strip()
    ]
    return candidates[:k]


# -----------------------------------------------------
# 2. Execute and Score SQL candidates
# -----------------------------------------------------
def score_sql_candidate(sql: str) -> Tuple[float, pd.DataFrame, str]:
    """
    Execute SQL and score result on:
    - Non-emptiness (best)
    - More rows = slightly better
    - Wider columns = slightly better
    """

    try:
        df, cols = run_sql_query(sql)
    except Exception as e:
        return -1.0, None, str(e)

    if df is None:
        return -1.0, None, "No result"

    # scoring:
    # non-empty -> +10
    score = 0
    if len(df) > 0:
        score += 10
        score += min(len(df), 50) / 5   # up to +10
        score += min(len(cols), 20) / 10  # up to +2
    else:
        score = 0

    return score, df, None


# -----------------------------------------------------
# 3. Rank all candidates and pick best
# -----------------------------------------------------
def pick_best_sql(llm, schema_text: str, question: str, candidates: List[str]) -> Dict:
    results = []

    for sql in candidates:
        score, df, error = score_sql_candidate(sql)
        results.append({
            "sql": sql,
            "score": score,
            "df": df,
            "error": error,
        })

    # sort by score descending
    best = sorted(results, key=lambda x: x["score"], reverse=True)[0]

    return {
        "best": best,
        "all_candidates": results,
    }
