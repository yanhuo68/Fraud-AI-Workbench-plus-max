# Implementation Plan - Native Theme and UI Cohesion

Eliminate high-contrast "light" components in the dark theme by leveraging Streamlit's native configuration and more aggressive CSS targeting.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [NEW] [.streamlit/config.toml](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/.streamlit/config.toml)
- Set `[theme]` to force a dark base:
    - `primaryColor = "#4A90E2"`
    - `backgroundColor = "#0E1117"`
    - `secondaryBackgroundColor = "#1A1C23"`
    - `textColor = "#E0E0E0"`
    - `font = "sans serif"`
- This ensures all internal components (uploader, logic tables) align with the workbench's colors at the core level.

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- Add `st.set_page_config(page_title="Sentinel Fraud AI", layout="wide")` as the very first Streamlit command.

#### [MODIFY] [styles/main.css](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/styles/main.css)
- **Dropzone Fix**: Target the inner div classes (like `.st-ae`, `.st-af`) that Streamlit uses for the file uploader dropzone area to force transparency or matching dark colors.
- **Dataframe Fix**: Target the `stDataFrame` more specifically to ensure the "grid" background doesn't default to white.
- **Sidebar Dropdown**: Ensure the dropdown background and text have zero contrast issues.

## Verification Plan

### Manual Verification
1.  **Native Theme**: Refresh the app. Verify that even *before* custom CSS loads, the app is natively dark.
2.  **Uploader**: Check the "Upload Data" dropzone. It should now have a subtle, dark background that blends with the page.
3.  **Dataframe**: Verify the dataframe headers and cells use the dark palette with white/light-gray text.
