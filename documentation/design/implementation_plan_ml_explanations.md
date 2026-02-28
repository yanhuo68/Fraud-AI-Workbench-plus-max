# Implementation Plan - ML Dashboard Explanations

## Goal Description
Enhance the ML Dashboard results section with "professional" explanations and analysis guides to help non-technical users understand the metrics, confusion matrix, and feature importance.

## User Review Required
None.

## Proposed Changes

### `app/tabs/tab_ml_dashboard.py`

#### [MODIFY] [tab_ml_dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/tabs/tab_ml_dashboard.py)
- **Metric Definitions**:
    - Add an `st.expander` or info box below the metrics row defining Accuracy, Precision, Recall, F1, and AUC.
- **Classification Report**:
    - Add a brief "How to read this" note.
- **Confusion Matrix**:
    - Add an "Analysis Guide" (markdown) explaining True Positives vs False Positives in the context of fraud.
- **Feature Importance**:
    - Add an explanation of what "importance" means (e.g., "features that most influenced the model's decision").

## Verification Plan

### Manual Verification
1.  **Run Pipeline**:
    - Go to ML Dashboard.
    - Select a dataset and train a model.
2.  **Verify UI**:
    - Check for the new "Guide" or "Explanation" sections near each chart.
    - Ensure text is clear and formatted correctly.
