# Implementation Plan - Fix Logging and Improve Error Handling

Resolve the logging `KeyError`, add robust error handling to the upload process, and ensure `data/raw/` is correctly included in the build and repository.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- Rename the `"filename"` key to `"loaded_filename"` in the `extra` dictionary of the `logger.info` call within `load_and_persist_dataset` to avoid conflicting with the standard `LogRecord` attribute.
- Wrap `load_and_persist_dataset` and its callers in `try...except` blocks to display user-friendly error messages in Streamlit instead of crashing the app.

#### [MODIFY] [.dockerignore](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/.dockerignore)
- Add a comment to explicitly clarify that `data/raw/` is included.

### [Root Directory]

#### [MODIFY] [.gitignore](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/.gitignore)
- Add a comment to explicitly clarify that `data/raw/` is included (not ignored).

## Verification Plan

### Manual Verification
1.  **Demo Upload**: Click "Upload Demo" again. Verify that the `KeyError` is gone and the data loads successfully.
2.  **Error Handling**: Temporarily "break" a file path or rename a column to trigger an error. Verify the UI shows a red error box instead of a traceback crash.
3.  **Build Check**: Run `docker compose build`. Verify that `data/raw/` content is present in the image.
