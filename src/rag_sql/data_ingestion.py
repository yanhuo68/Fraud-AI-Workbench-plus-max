# rag_sql/data_ingestion.py

from pathlib import Path
import pandas as pd
import sqlite3
from datetime import datetime
import re
from typing import List

import streamlit as st
from src.rag_sql.pkfk_detector import detect_primary_key, detect_foreign_keys

DEFAULT_DB_PATH = Path("data/db/fraud.db")
DOCS_DIR = Path("docs")


def sanitize_table_name(filename: str) -> str:
    """
    Convert filename to a safe SQLite table name.
    Examples:
        "Fraud Data.csv" -> "fraud_data"
        "2024-Jan-Transactions.csv" -> "t2024_jan_transactions"
    """
    name = filename.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name).strip("_")
    if name[0].isdigit():
        name = "t_" + name
    return name


def write_schema_markdown(df: pd.DataFrame, table_name: str):
    schema_path = DOCS_DIR / f"schema_{table_name}.md"
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append(f"# Schema for `{table_name}`\n")
    lines.append(f"_Generated: {datetime.utcnow().isoformat(timespec='seconds')}Z_\n\n")
    lines.append("| Column | Pandas Type | SQL Type | Null Count | Sample |\n")
    lines.append("|--------|-------------|----------|------------|--------|\n")

    for col in df.columns:
        dtype = str(df[col].dtype)

        if "int" in dtype:
            sql_type = "INTEGER"
        elif "float" in dtype:
            sql_type = "REAL"
        else:
            sql_type = "TEXT"

        nulls = df[col].isna().sum()
        sample = str(df[col].dropna().iloc[0]) if df[col].dropna().any() else ""

        lines.append(f"| {col} | {dtype} | {sql_type} | {nulls} | {sample} |\n")

    lines.append("\n")
    lines.append("### Notes\n")
    lines.append(f"- Table name: `{table_name}`\n")
    lines.append("- Generated automatically from uploaded CSV.\n")

    schema_path.write_text("".join(lines), encoding="utf-8")
    return schema_path

def write_schema_markdown_with_pkfk(
    df: pd.DataFrame,
    table_name: str,
    primary_key: str | None,
    foreign_keys: List[tuple],
):
    schema_path = DOCS_DIR / f"schema_{table_name}.md"
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append(f"# Schema for `{table_name}`\n")
    lines.append(f"_Generated: {datetime.utcnow().isoformat(timespec='seconds')}Z_\n\n")

    # Primary Key
    lines.append("## Primary Key\n")
    lines.append(f"- `{primary_key}`\n\n" if primary_key else "- None detected\n\n")

    # Foreign Keys
    lines.append("## Foreign Keys\n")
    if foreign_keys:
        for fk in foreign_keys:
            table_A, colA, table_B, pkB = fk
            lines.append(f"- `{colA}` → `{table_B}.{pkB}`\n")
    else:
        lines.append("- None detected\n")
    lines.append("\n")

    # Columns table
    lines.append("## Columns\n")
    lines.append("| Column | Pandas Type | Nulls | Sample |\n")
    lines.append("|--------|-------------|--------|---------|\n")
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = df[col].isna().sum()
        sample = str(df[col].dropna().iloc[0]) if df[col].dropna().any() else ""
        lines.append(f"| {col} | {dtype} | {nulls} | {sample} |\n")

    schema_path.write_text("".join(lines), encoding="utf-8")
    return schema_path

def ingest_uploaded_csv_dynamic(df: pd.DataFrame, filename: str):
    from src.rag_sql.pkfk_detector import detect_primary_key, detect_foreign_keys

    table_name = sanitize_table_name(filename)

    # Save table
    conn = sqlite3.connect(str(DEFAULT_DB_PATH))
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    finally:
        conn.close()

    # Detect PK
    pk = detect_primary_key(df)


