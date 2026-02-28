# UI Design: ML Dashboard (`tab_ml_dashboard.py`)

## 1. Purpose
The **ML Dashboard** provides a no-code interface for training, evaluating, and analyzing machine learning models for fraud detection. It uses the currently uploaded/selected dataset.

## 2. Layout & Structure

### A. Empty State
-   **Trigger**: If `uploaded_df` is missing from session state.
-   **UI**: Friendly warning with instructions to go to the "Upload Data" tab to load a dataset.

### B. Configuration Sidebar (Expandable)
-   **Target Column**: Selectbox to choose the label column (e.g., `is_fraud`).
-   **Features**: Multiselect to include/exclude columns.
-   **Model Type**: Dropdown (Random Forest, Logistic Regression, XGBoost).
-   **Hyperparameters**: Sliders for `n_estimators`, `max_depth`, etc.

### C. Main Dashboard Area
1.  **Dataset Overview**:
    -   Metrics: Rows, Columns, Fraud Rate (%).
    -   Visuals: Class distribution pie chart.
2.  **Training Progress**:
    -   Spinners/Status bars during training.
3.  **Model Performance**:
    -   **Metrics**: Accuracy, Precision, Recall, F1-Score (with clear definitions in tooltips/expanders).
    -   **Confusion Matrix**: Heatmap showing True Positives, False Positives, etc., with an interpretation guide.
    -   **ROC Curve**: Plotly chart showing model discrimination capability.
4.  **Feature Importance**:
    -   Bar chart ranking features by predictive power.
    -   Table view for raw importance scores.
5.  **Drift Detection**:
    -   Analysis of feature distribution changes (requires reference dataset or train/test split comparison).

## 3. Key Logic & State
-   **`uploaded_df`**: The primary inputs.
-   **`ml_model`**: Stores the trained model object.
-   **`ml_results`**: Stores evaluation metrics (accuracy, confusion matrix).
-   **Auto-ML**: The tab uses `src/ml/` modules to automatically handle preprocessing (imputation, encoding) and training.
