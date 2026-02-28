# Implementation Plan - Adjustable Split & Data Transparency

Empower users to control the train/test split ratio and provide high-visibility metrics on the scale of the evaluation.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [ml/data_prep.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/ml/data_prep.py)
- **`preprocess(df, test_size=0.2)`**: Update the function signature and use the `test_size` argument in `train_test_split`.

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **Configuration Section**:
    - Add `st.slider("Test Set Size", 0.1, 0.5, 0.2)` to the ML settings.
    - Use this value when calling `preprocess`.
- **UI Enhancements**:
    - Add a `st.info` or `st.warning` box titled **"📊 Evaluation Scope"** that clearly explains: "Currently, {X}% of your data is held out to TEST the model. The metrics below only reflect this 20% sample to ensure unbiased results."
    - Update the results captions to use bold text for the evaluation row counts.

## Verification Plan

### Manual Verification
1.  **Slider Test**: Change the split to 10% and run. Verify the row count in the caption updates to reflect ~10% of the dataset.
2.  **Visual Proof**: Check that the "Evaluation Scope" info box is prominent and easy to find.
3.  **Accuracy**: Verify that `Detected frauds` (e.g., 18/18) scales correctly when the test split is adjusted.
