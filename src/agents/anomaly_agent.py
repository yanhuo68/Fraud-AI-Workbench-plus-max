# agents/anomaly_agent.py

"""
Anomaly Detection Agent for SQL results.

Uses IQR-based detection on numeric columns to flag outliers.
"""

import pandas as pd
from src.agents.llm_router import init_llm


def detect_anomalies_iqr(df: pd.DataFrame, multiplier: float = 1.5):
    """
    Return:
    - anomalies: DataFrame of rows flagged as anomalies (any numeric col)
    - info: dict describing thresholds per column
    """
    if df is None or df.empty:
        return None, {}

    num_df = df.select_dtypes(include="number")
    if num_df.empty:
        return None, {}

    info = {}
    mask = pd.Series(False, index=df.index)

    for col in num_df.columns:
        q1 = num_df[col].quantile(0.25)
        q3 = num_df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        col_mask = (num_df[col] < lower) | (num_df[col] > upper)
        mask |= col_mask
        info[col] = {"q1": q1, "q3": q3, "lower": lower, "upper": upper}

    anomalies = df[mask]
    return anomalies, info


def anomaly_narrative(
    question: str,
    df: pd.DataFrame,
    anomalies: pd.DataFrame,
    thresholds: dict,
    schema_text: str,
    llm_id: str,
) -> str:
    """
    Use LLM to explain anomalies and their relevance to fraud.
    """

    llm = init_llm(llm_id)

    if anomalies is None or anomalies.empty:
        anomalies_preview = "NO_ANOMALIES_FOUND"
    else:
        anomalies_preview = anomalies.head(20).to_markdown(index=False)

    threshold_text = ""
    for col, t in thresholds.items():
        threshold_text += (
            f"- {col}: lower={t['lower']:.4f}, upper={t['upper']:.4f}, "
            f"Q1={t['q1']:.4f}, Q3={t['q3']:.4f}\n"
        )

    prompt = f"""
You are a fraud analytics expert.

The user asked:
{question}

We ran anomaly detection (IQR-based) on the SQL result.

Detected anomalies (sample):
{anomalies_preview}

Thresholds used per numeric column:
{threshold_text}

Schema and ERD:
{schema_text}

Tasks:
1. Explain what kind of anomalies we are seeing.
2. Relate these anomalies to potential fraud or unusual behavior.
3. Suggest next steps (further queries, filters, or investigations).

Provide a concise explanation.
"""

    return llm.invoke(prompt).content
