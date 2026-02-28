# Implementation Plan - Ensure Code Sync and Fix Logging

Ensure the Docker container always reflects the latest host code and eliminate any possibility of a logging `KeyError` by renaming conflict-prone variables.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [docker-compose.yml](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/docker-compose.yml)
- Remove the obsolete `version` attribute to avoid Docker warnings.
- **Add Volume Mounting**: Map the current directory (`.`) to `/app` inside the container. This allows instant code updates ("Live Reload") without needing to rebuild or restart the container for every change.
- Ensure `data/` and `logs/` volumes remain but are compatible with the full-folder mapping.

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- Rename the function argument `filename` to `ds_name` in `load_and_persist_dataset`.
- Rename all internal references to `filename` to `ds_name`.
- Add a visible `st.toast` or large success message to confirm the NEW code is running.

## Verification Plan

### Manual Verification
1.  **Restart with Volume**: Run `docker compose up`.
2.  **Verify Sync**: Make a small text change in `dashboard.py` title. Refresh browser. Verify the change is visible without a restart.
3.  **Demo Upload**: Click "Upload Demo". Verify success.
