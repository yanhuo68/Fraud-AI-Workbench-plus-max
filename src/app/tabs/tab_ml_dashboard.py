import streamlit as st
import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor
import plotly.express as px

def render_ml_dashboard_tab():
    st.header("📈 ML Dashboard")

    df = None
    table_choice = None
    if "table_dataframes" in st.session_state and st.session_state.table_dataframes:
        table_choice = st.selectbox("Select table to use", list(st.session_state.table_dataframes.keys()))
        df = st.session_state.table_dataframes.get(table_choice)
    elif "uploaded_df" in st.session_state:
        df = st.session_state.uploaded_df

    if df is None:
        st.warning("📊 No data uploaded yet")
        st.info("""
        **To get started:**
        1. 👈 Go to the **Upload Data** tab
        2. Upload CSV files or execute SQL scripts
        3. Come back here to train and evaluate ML models!
        
        Once you upload data, you'll be able to:
        ✨ Train fraud detection models
        📈 Evaluate model performance
        🎯 Analyze feature importance
        🔍 Check for data drift
        """)
        return
    else:
        st.markdown("Quick training/evaluation on the uploaded dataset.")

        label_options = list(df.columns)
        default_label = "isFraud" if "isFraud" in label_options else None

        label_col = st.selectbox(
            "Select label/target column (expects binary 0/1 or yes/no/true/false)",
            options=label_options,
            index=label_options.index(default_label) if default_label in label_options else 0,
        ) if label_options else None

        def coerce_binary(series: pd.Series):
            """Try to coerce a column to binary 0/1; return (series, error_msg)."""
            s = series.copy()
            if s.dtype == bool:
                return s.astype(int), None

            if s.dtype == object:
                mapping = {
                    "yes": 1, "true": 1, "y": 1, "fraud": 1, "fraudulent": 1,
                    "no": 0, "false": 0, "n": 0, "legit": 0, "legitimate": 0,
                }
                lowered = s.str.lower().str.strip()
                if lowered.isin(mapping.keys()).all():
                    return lowered.map(mapping).astype(int), None

            # Numeric path
            try:
                s_num = pd.to_numeric(s)
                unique_vals = set(s_num.dropna().unique())
                if unique_vals.issubset({0, 1}):
                    return s_num.astype(int), None
            except Exception:
                pass

            return None, f"Selected label '{label_col}' is not binary (0/1/yes/no/true/false)."

        label_series, label_err = coerce_binary(df[label_col]) if label_col else (None, "No label selected.")

        with st.expander("ℹ️ Dataset Info", expanded=False):
            st.write(
                {
                    "Rows": len(df),
                    "Columns": list(df.columns),
                    "Selected Label": label_col or "None selected",
                    "Fraud Rate": f"{label_series.mean()*100:.3f}%" if label_series is not None else "label not usable",
                }
            )

        candidate_features = [c for c in df.columns if c != label_col]
        use_feature_subset = st.checkbox("Select features to include (otherwise auto-drop high-card categorical columns)", value=False)
        selected_features = candidate_features
        high_card_threshold = 50
        auto_drop_cols = []
        if use_feature_subset:
            selected_features = st.multiselect(
                "Choose feature columns",
                options=candidate_features,
                default=candidate_features,
            )
            if not selected_features:
                st.error("Select at least one feature or disable feature selection.")
        else:
            auto_drop_cols = [
                c for c in candidate_features
                if (not pd.api.types.is_numeric_dtype(df[c])) and df[c].nunique() > high_card_threshold
            ]
            selected_features = [c for c in candidate_features if c not in auto_drop_cols]

        st.markdown("**Features to be used**")
        if selected_features:
            st.write(selected_features)
        else:
            st.warning("No features selected; please choose at least one.")
        if auto_drop_cols:
            st.info(f"Automatically dropping high-cardinality categorical columns (> {high_card_threshold} uniques): {auto_drop_cols}")

        st.markdown("**Model hyperparameters**")
        col_hp1, col_hp2 = st.columns(2)
        with col_hp1:
            rf_estimators = st.number_input(
                "RandomForest trees",
                min_value=50,
                max_value=1000,
                value=300,
                step=50,
            )
            rf_max_depth_val = st.number_input(
                "RandomForest max depth (0 = None)",
                min_value=0,
                max_value=100,
                value=0,
                step=1,
            )
            rf_max_depth = None if rf_max_depth_val == 0 else rf_max_depth_val
        with col_hp2:
            test_size_pct = st.slider("Test set size", 0.1, 0.5, 0.2, 0.05)
            use_smote = st.checkbox("Use SMOTE (oversampling) - requires imbalanced-learn", value=False)

        if st.button("🚀 Train Model", use_container_width=True):
            if label_err:
                st.error(label_err)
            elif not selected_features:
                st.error("No features selected.")
            else:
                with st.spinner("Training model..."):
                    # Prepare X, y
                    X_raw = df[selected_features].copy()
                    st.session_state["ml_X_raw"] = X_raw.copy() # Save (unfilled) raw data for checks
                    y = label_series

                    # Simple preprocessing: fillna, get_dummies
                    # Fill numeric NaN with median, object NaN with mode
                    for c in X_raw.columns:
                        if pd.api.types.is_numeric_dtype(X_raw[c]):
                            X_raw[c] = X_raw[c].fillna(X_raw[c].median())
                        else:
                            X_raw[c] = X_raw[c].fillna(X_raw[c].mode()[0] if not X_raw[c].mode().empty else "missing")

                    X_encoded = pd.get_dummies(X_raw, drop_first=True)
                    # Align columns to be safe? simple approach for now
                    
                    X_train, X_test, y_train, y_test = train_test_split(
                        X_encoded, y, test_size=test_size_pct, random_state=42, stratify=y
                    )

                    if use_smote:
                        try:
                            from imblearn.over_sampling import SMOTE
                            sm = SMOTE(random_state=42)
                            X_train_res, y_train_res = sm.fit_resample(X_train, y_train)
                            X_train, y_train = X_train_res, y_train_res
                        except ImportError:
                            st.warning("imbalanced-learn not installed. Skipping SMOTE.")
                    
                    scaler = StandardScaler()
                    X_train_scaled = scaler.fit_transform(X_train)
                    X_test_scaled = scaler.transform(X_test)

                    clf = RandomForestClassifier(
                        n_estimators=rf_estimators,
                        max_depth=rf_max_depth,
                        random_state=42,
                        class_weight="balanced"
                    )
                    clf.fit(X_train_scaled, y_train)

                    y_pred = clf.predict(X_test_scaled)
                    y_prob = clf.predict_proba(X_test_scaled)[:, 1]

                    # Metrics
                    acc = accuracy_score(y_test, y_pred)
                    prec = precision_score(y_test, y_pred, zero_division=0)
                    rec = recall_score(y_test, y_pred, zero_division=0)
                    f1 = f1_score(y_test, y_pred, zero_division=0)
                    try:
                        auc = roc_auc_score(y_test, y_prob)
                    except:
                        auc = 0.5

                    st.success("Training complete!")
                    
                    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
                    col_m1.metric("Accuracy", f"{acc:.2%}")
                    col_m2.metric("Precision", f"{prec:.2%}")
                    col_m3.metric("Recall", f"{rec:.2%}")
                    col_m4.metric("F1 Score", f"{f1:.2f}")
                    col_m5.metric("AUC", f"{auc:.2f}")

                    with st.expander("ℹ️ Metric Definitions & Legend", expanded=False):
                        st.markdown("""
                        - **Accuracy**: Overall correctness (Correct Predictions / Total).
                        - **Precision**: When it predicts Fraud, how often is it right? (High precision = fewer false alarms).
                        - **Recall**: Out of actual Fraud cases, how many did we catch? (High recall = fewer missed frauds).
                        - **F1 Score**: Harmonic mean of Precision and Recall (good balance for imbalanced data).
                        - **AUC (Area Under Curve)**: Ability to distinguish between Fraud and Legitimate (0.5 = random guess, 1.0 = perfect).
                        """)

                    st.text("Classification Report:")
                    st.code(classification_report(y_test, y_pred))

                    # Confusion Matrix
                    cm = confusion_matrix(y_test, y_pred)
                    fig_cm = px.imshow(cm, text_auto=True, title="Confusion Matrix")
                    st.plotly_chart(fig_cm, width="stretch")
                    
                    with st.expander("ℹ️ Confusion Matrix Guide", expanded=False):
                        st.markdown("""
                        - **True Negative (Top-Left)**: Legitimate transactions correctly identified as Legitimate.
                        - **False Positive (Top-Right)**: Legitimate transactions incorrectly flagged as Fraud (False Alarm).
                        - **False Negative (Bottom-Left)**: Fraudulent transactions missed (missed detection).
                        - **True Positive (Bottom-Right)**: Fraudulent transactions correctly caught.
                        """)

                    # Feature Importance
                    importances = clf.feature_importances_
                    feat_imp = pd.DataFrame({
                        "Feature": X_encoded.columns,
                        "Importance": importances
                    }).sort_values("Importance", ascending=False).head(20)
                    
                    fig_imp = px.bar(feat_imp, x="Importance", y="Feature", orientation="h", title="Top 20 Features")
                    st.plotly_chart(fig_imp, width="stretch")
                    st.caption("✨ **Analysis**: These features had the strongest influence on the model's decisions. High importance implies this variable is a strong predictor of fraud.")

                    # Store model in session
                    st.session_state["ml_model"] = clf
                    st.session_state["ml_scaler"] = scaler
                    st.session_state["ml_feats"] = list(X_encoded.columns)
                    st.session_state["ml_metrics"] = {"acc": acc, "f1": f1, "auc": auc}
                    
                    # Store data for drift check later
                    st.session_state["ml_X_train"] = pd.DataFrame(X_train_scaled, columns=X_encoded.columns)
                    st.session_state["ml_X_test"] = pd.DataFrame(X_test_scaled, columns=X_encoded.columns)
                    st.session_state["ml_df_proc"] = X_encoded  # processed with dummies

            # --- OPTIONAL: Threshold Optimization ---
            if "ml_model" in st.session_state:
                st.markdown("---")
                st.subheader("Threshold Optimization")
                pass

        # If a model exists in session, enable "Save Model"
        if "ml_model" in st.session_state:
            st.success(f"Model ready. AUC: {st.session_state['ml_metrics']['auc']:.2f}")
            
            # Save model logic
            model_dir = Path("data/models")
            model_dir.mkdir(parents=True, exist_ok=True)
            
            model_name = st.text_input("Model Name (for saving)", value=f"rf_model_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}")
            
            if st.button("💾 Save Model + Preprocessor", use_container_width=True):
                try:
                    
                    rf_path = model_dir / f"{model_name}.joblib"
                    scaler_path = model_dir / f"scaler_{model_name}.joblib"
                    
                    joblib.dump(st.session_state["ml_model"], rf_path)
                    joblib.dump(st.session_state["ml_scaler"], scaler_path)
                    
                    # Save metadata
                    meta_path = model_dir / f"meta_{model_name}.json"
                    meta = {
                        "features": st.session_state["ml_feats"],
                        "metrics": st.session_state["ml_metrics"],
                        "timestamp": str(pd.Timestamp.now()),
                        "data_source": table_choice or "uploaded_csv"
                    }
                    meta_path.write_text(json.dumps(meta, indent=2))
                    
                    st.success(f"Saved to {model_dir}")
                    
                    # Log run for tracking
                    runs_path = model_dir / "model_runs.json"
                    runs = []
                    if runs_path.exists():
                        try:
                            runs = json.loads(runs_path.read_text())
                        except:
                            pass
                    
                    # calculate data hash?
                    data_hash = "N/A" # simplifying
                    
                    run_record = {
                        "timestamp": meta["timestamp"],
                        "model_name": model_name,
                        "auc": meta["metrics"]["auc"],
                        "f1": meta["metrics"]["f1"],
                        "data_hash": data_hash,
                        "model_file": rf_path.name,
                        "scaler_file": scaler_path.name,
                        "meta_file": meta_path.name,
                    }
                    runs.append(run_record)
                    runs_path.write_text(json.dumps(runs, indent=2))
                    
                except Exception as e:
                    st.error(f"Save failed: {e}")

            if st.button("📥 Load Latest Model", use_container_width=True):
                models = sorted(model_dir.glob("rf_model_*.joblib"))
                if not models:
                    st.warning("No saved models found.")
                else:
                    latest = models[-1]
                    name_part = latest.stem.split('rf_model_')[-1]
                    scaler_candidates = sorted(model_dir.glob(f"scaler_{name_part}*.joblib"))
                    scaler_path = scaler_candidates[-1] if scaler_candidates else None
                    meta_candidates = sorted(model_dir.glob(f"meta_{name_part}*.json"))
                    meta_path = meta_candidates[-1] if meta_candidates else None

                    st.session_state["loaded_model"] = joblib.load(latest)
                    st.session_state["loaded_scaler"] = joblib.load(scaler_path) if scaler_path else None
                    st.session_state["loaded_meta"] = json.loads(meta_path.read_text()) if meta_path and meta_path.exists() else {}

                    st.success(f"Loaded model: {latest.name}")
                    if meta_path:
                        st.info(f"Meta: {meta_path.name}")

            st.markdown("---")
            st.subheader("Data Quality & Drift Checks")
            if st.button("Run Data Checks", use_container_width=True):
                # Use RAW data for missing values check
                X_raw_saved = st.session_state.get("ml_X_raw")
                X_train_saved = st.session_state.get("ml_X_train")
                X_test_saved = st.session_state.get("ml_X_test")
                feats_saved = st.session_state.get("ml_feats")

                if X_raw_saved is None or X_train_saved is None or X_test_saved is None:
                    st.warning("Run the ML pipeline first to generate data for checks.")
                else:
                    def summarize_nulls(df_check):
                        null_counts = df_check.isna().sum()
                        return null_counts[null_counts > 0].sort_values(ascending=False)

                    # Check raw features for missing values
                    nulls = summarize_nulls(X_raw_saved)
                    st.markdown("**Missing Values (in selected features)**")
                    if nulls.empty:
                        st.info("No missing values detected in selected features.")
                    else:
                        st.dataframe(nulls)

                    # Basic stats drift between train and test for numeric cols
                    drift_rows = []
                    # Check up to 20 numeric columns
                    numeric_cols = [c for c in X_train_saved.columns if pd.api.types.is_numeric_dtype(X_train_saved[c])]
                    
                    for c in numeric_cols[:20]: 
                        m1 = X_train_saved[c].mean()
                        m2 = X_test_saved[c].mean()
                        std1 = X_train_saved[c].std()
                        # Z-test like metric
                        diff = abs(m1 - m2)
                        is_drift = False
                        if std1 > 0 and diff > 0.5 * std1: # Simple heuristic
                            is_drift = True
                        
                        drift_rows.append({
                            "feature": c, 
                            "train_mean": m1, 
                            "test_mean": m2, 
                            "diff": diff, 
                            "drift_detected": is_drift
                        })
                    
                    st.markdown("**Drift Detection (Train vs Test)**")
                    if drift_rows:
                        drift_df = pd.DataFrame(drift_rows)
                        # Show the stats table
                        st.dataframe(drift_df.style.apply(lambda x: ['background-color: #ffcdd2' if x['drift_detected'] else '' for i in x], axis=1))
                        
                        drift_count = drift_df['drift_detected'].sum()
                        if drift_count > 0:
                            st.warning(f"Detected potential drift in {drift_count} features.")
                        else:
                            st.success("No significant drift detected in top features (stats shown above).")
                    else:
                        st.info("No numeric features to check for drift.")
