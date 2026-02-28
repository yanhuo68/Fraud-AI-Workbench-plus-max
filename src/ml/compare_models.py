# ml/compare_models.py

import streamlit as st
import pandas as pd
import numpy as np

from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)
from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt
from io import BytesIO

from src.agents.llm_router import init_llm
from src.ml.report_generator import generate_model_comparison_pdf


def compute_supervised_metrics(model, X_test, y_test):
    prob = model.predict_proba(X_test)[:, 1]
    pred = (prob >= 0.5).astype(int)

    return {
        "Precision": precision_score(y_test, pred, zero_division=0),
        "Recall": recall_score(y_test, pred, zero_division=0),
        "F1": f1_score(y_test, pred, zero_division=0),
        "AUC": roc_auc_score(y_test, prob),
        "proba": prob,  # keep for ROC
    }


def compute_unsupervised_metrics(scores, y_true):
    k = max(1, int(0.01 * len(scores)))  # top 1% anomalies
    idx = np.argsort(scores)[::-1][:k]
    precision_at_k = float(np.mean(y_true.iloc[idx] == 1))

    return {
        "Precision@K": precision_at_k,
        "Top-K Count": k,
    }


def encode_features(df: pd.DataFrame):
    df_enc = df.copy()
    for col in df_enc.columns:
        if not pd.api.types.is_numeric_dtype(df_enc[col]):
            df_enc[col], _ = pd.factorize(df_enc[col].astype(str))
    df_enc = df_enc.fillna(0)
    return df_enc


def run_model_comparison():
    st.title("📊 Model Comparison Dashboard")

    df = None
    if "uploaded_df" in st.session_state:
        df = st.session_state.uploaded_df.copy()
    elif "table_dataframes" in st.session_state and st.session_state.table_dataframes:
        table_names = list(st.session_state.table_dataframes.keys())
        table_choice = st.selectbox("Select table", table_names)
        df = st.session_state.table_dataframes[table_choice].copy()
    if df is None:
        st.warning("Please upload dataset in the upload tab first.")
        return

    label_options = list(df.columns)
    default_label = "isFraud" if "isFraud" in label_options else None
    label_col = st.selectbox(
        "Select label/target column (expects binary 0/1)",
        options=label_options,
        index=label_options.index(default_label) if default_label in label_options else 0,
    )

    try:
        y = pd.to_numeric(df[label_col]).astype(int)
    except Exception:
        st.error("Selected label is not numeric/binary; please choose a binary column.")
        return
    if set(y.unique()) - {0, 1}:
        st.error("Label must be binary (0/1).")
        return

    X = encode_features(df.drop(columns=[label_col]))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Dataset summary for report
    dataset_summary = {
        "Rows": len(df),
        "Fraud Rate": f"{(y.mean() * 100):.3f}%",
        "Num Features": X.shape[1],
    }

    st.subheader("📌 Training Models...")

    results = {}

    # ---------- Supervised models ----------
    rf = RandomForestClassifier(n_estimators=200, random_state=42)
    rf.fit(X_train, y_train)
    results["Random Forest"] = compute_supervised_metrics(rf, X_test, y_test)

    gb = GradientBoostingClassifier(random_state=42)
    gb.fit(X_train, y_train)
    results["Gradient Boosting"] = compute_supervised_metrics(gb, X_test, y_test)

    lr = LogisticRegression(max_iter=2000)
    lr.fit(X_train, y_train)
    results["Logistic Regression"] = compute_supervised_metrics(lr, X_test, y_test)

    # ---------- Unsupervised models ----------
    if_model = IsolationForest(contamination=y.mean(), random_state=42)
    if_model.fit(X_train)
    if_scores = -if_model.decision_function(X_test)
    results["Isolation Forest"] = compute_unsupervised_metrics(if_scores, y_test)

    lof = LocalOutlierFactor(n_neighbors=30, novelty=True)
    lof.fit(X_train)
    lof_scores = -lof.score_samples(X_test)
    results["Local Outlier Factor"] = compute_unsupervised_metrics(lof_scores, y_test)

    oc = OneClassSVM(kernel="rbf", gamma="scale")
    oc.fit(X_train)
    oc_scores = -oc.score_samples(X_test)
    results["One-Class SVM"] = compute_unsupervised_metrics(oc_scores, y_test)

    # ---------- Display comparison ----------
    st.subheader("📊 Model Performance Comparison")
    display_rows = []
    display_results = {}
    keep_keys = ["Precision", "Recall", "F1", "AUC", "Precision@K", "Top-K Count"]
    for model_name, metrics in results.items():
        cleaned = {}
        for k in keep_keys:
            if k in metrics:
                val = metrics[k]
                try:
                    cleaned[k] = float(val)
                except Exception:
                    cleaned[k] = val
        cleaned["Model"] = model_name
        display_rows.append(cleaned)
        display_results[model_name] = {kk: vv for kk, vv in cleaned.items() if kk != "Model"}

    st.markdown("**Model Metrics (scalar only)**")
    for row in display_rows:
        model_name = row.get("Model", "model")
        parts = []
        for k in keep_keys:
            if k in row:
                v = row[k]
                if isinstance(v, float):
                    v_str = f"{v:.4f}"
                else:
                    v_str = str(v)
                parts.append(f"{k}: {v_str}")
        st.markdown(f"- **{model_name}** — " + ", ".join(parts))

    # ---------- ROC Curves ----------
    st.subheader("📈 ROC Curves (Supervised Models)")

    fig = plt.figure(figsize=(7, 4))
    for name, model in [("Random Forest", rf), ("Gradient Boosting", gb), ("Logistic Regression", lr)]:
        prob = results[name]["proba"]
        fpr, tpr, _ = roc_curve(y_test, prob)
        plt.plot(fpr, tpr, label=name)

    plt.plot([0, 1], [0, 1], "--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.legend()
    st.pyplot(fig)
    st.markdown(
        """
**How to read this plot**
- Each curve shows TPR vs FPR across thresholds for a model (higher and more to the top-left is better).
- The dashed diagonal is random chance; curves above it indicate useful discrimination.
- Steeper rise near low FPR is valuable for fraud (catching fraud with few false alarms).
"""
    )

    # ---------- LLM Interpretation ----------
    st.subheader("🧠 LLM Interpretation of Results")

    # Check if API key is properly configured using the same logic as init_llm
    from src.agents.llm_router import get_api_key
    openai_key = get_api_key("OPENAI_API_KEY") or ""
    has_valid_key = openai_key and not openai_key.startswith("your") and not openai_key.startswith("sk-your")
    
    llm_text = "LLM interpretation not available."
    
    if not has_valid_key:
        st.info("""
        👋 **Welcome! API Key Setup Required**
        
        To use LLM-powered interpretation, please configure your OpenAI API key using **one of these options**:
        
        **🚀 Quick Start (Recommended for Testing)**
        - Click the **sidebar** on the left
        - Expand **"🔑 API Keys"** section  
        - Enter your OpenAI API key
        - ✅ Works immediately! (Session-based)
        
        **🔒 Production Setup (Persistent)**
        
        *Option A: System Environment Variable (Most Secure)*
        ```bash
        # Set on your Mac/Linux
        export OPENAI_API_KEY=sk-proj-your-actual-key
        
        # Then restart Docker
        docker compose down && docker compose up --build
        ```
        
        *Option B: Edit .env File*
        1. Open `.env` file in project root
        2. Replace placeholder with your real key:
           `OPENAI_API_KEY=sk-proj-your-actual-key`
        3. Restart Docker: `docker compose down && docker compose up --build`
        
        📌 **Note:** The model comparison metrics above are still available without LLM interpretation.
        
        Need an API key? Get one at [OpenAI Platform](https://platform.openai.com/account/api-keys)
        """)
    else:
        try:
            llm = init_llm(st.session_state.get("selected_llm", "openai:gpt-4o-mini"))

            header = ["Model"] + keep_keys
            rows_md = ["|" + "|".join(header) + "|", "|" + "|".join(["---"] * len(header)) + "|"]
            for row in display_rows:
                vals = []
                for col in header:
                    val = row.get(col, "")
                    if isinstance(val, float):
                        val = f"{val:.4f}"
                    vals.append(str(val))
                rows_md.append("|" + "|".join(vals) + "|")
            results_md = "\n".join(rows_md)

            summary_prompt = f"""
            You are a senior fraud analytics and ML expert.

            Below is a model comparison table for fraud detection:

            {results_md}

            Dataset summary:
            - Rows: {dataset_summary["Rows"]}
            - Fraud Rate: {dataset_summary["Fraud Rate"]}
            - Num Features: {dataset_summary["Num Features"]}

            Using the guidelines in the fraud knowledge-base (e.g., ml_evaluation_metrics, fraud_risk_rules, model_interpretation),
            provide a concise but rich report that explains:

            1. Which supervised model performs best and why.
            2. How the anomaly detection models (Isolation Forest, LOF, One-Class SVM) should be interpreted.
            3. Trade-offs between false positives and false negatives.
            4. A recommendation for which model(s) to use in production and how to combine them.

            Use clear headings and bullet points.
            """

            with st.spinner("Generating analysis with LLM..."):
                llm_response = llm.invoke(summary_prompt)

            llm_text = llm_response.content
            st.markdown(llm_text)
            
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "AuthenticationError" in error_msg or "invalid_api_key" in error_msg:
                st.error("""
                ❌ **API Key Authentication Failed**
                
                Your OpenAI API key is invalid or expired.
                
                **Fix:**
                1. Get a valid key from [OpenAI Platform](https://platform.openai.com/account/api-keys)
                2. Update `.env`: `OPENAI_API_KEY=sk-your-actual-key`
                3. Restart: `docker compose down && docker compose up --build`
                """)
            else:
                st.error(f"❌ LLM Error: {error_msg}")
            st.info("Skipping LLM interpretation. Metrics above are still available.")
            llm_text = "LLM interpretation unavailable due to API key issue."

    # Store for PDF generation
    st.session_state["model_comparison_results"] = display_results
    st.session_state["model_comparison_dataset_summary"] = dataset_summary
    st.session_state["model_comparison_llm_text"] = llm_text
    st.session_state["model_comparison_roc_fig"] = fig


    # ---------- PDF Export ----------
    st.subheader("📄 Export Model Comparison Report")

    if st.button("📥 Generate PDF Report"):
        with st.spinner("Generating PDF report..."):
            # Create PDF in a temp buffer, then offer as download
            tmp_path = "data/reports/model_comparison_report.pdf"
            pdf_path = generate_model_comparison_pdf(
                results=display_results,
                roc_fig=fig,
                dataset_summary=dataset_summary,
                llm_text=llm_text,
                output_path=tmp_path,
            )
            # Read back into memory
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

        st.success("PDF report generated.")
        st.download_button(
            label="⬇️ Download Model Comparison Report (PDF)",
            data=pdf_bytes,
            file_name="model_comparison_report.pdf",
            mime="application/pdf",
        )
