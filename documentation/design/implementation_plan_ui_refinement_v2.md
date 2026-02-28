# Implementation Plan - Dropzone and Dataframe Refinement

Refine the file uploader dropzone and the data display tables to perfectly coordinate with the "Sentinel" professional dark theme.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [styles/main.css](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/styles/main.css)
- **File Uploader Dropzone**:
    - Update `[data-testid="stFileUploader"]` to have a more integrated background color using `--secondary-bg-color`.
    - Style the internal dropzone area specifically to ensure consistency.
- **Data Display (Dataframe/Table)**:
    - Update `[data-testid="stDataFrame"]` to have a background that matches the theme better.
    - Add styles for `st.table` (if used) to ensure headers and cells are coordinated.
    - Use subtle borders and background shading for rows to improve readability in dark mode.

## Verification Plan

### Manual Verification
1.  **Dropzone**: Check the "Upload Data" tab and verify the file uploader background looks integrated and professional.
2.  **Dataframe**: Upload a file and verify the preview table (head of the dataframe) is clearly readable and matches the theme.
