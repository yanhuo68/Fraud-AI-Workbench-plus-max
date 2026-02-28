# Implementation Plan - Model Persistence

Address the performance bottleneck where ML models are needlessly re-trained on every execution. This will be achieved by implementing a filesystem-based cache using `joblib`.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [NEW] [model_persistence.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/utils/model_persistence.py)
- **`save_model(model, name)`**: Serializes the model to `data/models/{name}.joblib`.
- **`load_model(name)`**: Deserializes and returns the model if it exists on disk.
- **`get_model_path(name)`**: Helper to generate consistent paths.

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **Persistence Logic**:
    - Generate a "Dataset Hash" (or use dataset name + model type) to uniquely identify a trained model.
    - Before calling `train_isolation_forest` or `train_random_forest`, check if a cached model exists.
    - If found, load it; otherwise, train and then save.
- **UI Update**: Add a "Model Source" indicator (e.g., "⚡ Loaded from Cache" or "⚙️ Newly Trained").

#### [MODIFY] [requirements.txt](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/requirements.txt)
- Add `joblib` to the dependencies (standard for sklearn model serialization).

## Verification Plan

### Manual Verification
1.  **First Run**: Load a dataset and run ML metrics. Verify it takes time to train (check logs).
2.  **Second Run**: Press the button again. Verify the results appear instantly and logs show "Loaded from cache".
3.  **New Data**: Upload a *different* dataset. Verify the system detects the change and re-trains/captures a new model.
