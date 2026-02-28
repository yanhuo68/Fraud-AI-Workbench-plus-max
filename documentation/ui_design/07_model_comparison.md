# UI Design: Model Comparison (`tab_model_comparison.py`)

## 1. Purpose
The **Model Comparison** tab (rendered via `src.ml.compare_models`) allows advanced users to train multiple algorithms (Random Forest, XGBoost, etc.) under identical conditions and compare their performance metrics directly.

## 2. Layout & Structure

### A. Configuration
-   **Target Variable**: Select label.
-   **Test Split**: Slider for Train/Test ratio (e.g., 80/20).
-   **Models to Run**: Multiselect (RF, XGB, LR, SVM).

### B. Results Table
-   Sortable dataframe comparing:
    -   Accuracy
    -   Precision (Fraud Class)
    -   Recall (Fraud Class) - *Critical for fraud detection*
    -   F1 Score
    -   Training Time

### C. Visualizations
-   **ROC Curve Overlay**: All models plotted on a single ROC chart to visualize dominance.
-   **Confusion Matrix**: Toggle-able view for each model.

## 3. Key Logic & State
-   **`uploaded_df`**: Source data.
-   **Preprocessing**: Applies consistent encoding/scaling across all models to ensure fair comparison.
