# Implementation Plan - UI Visibility and Styling Refinements

Address visibility issues in the sidebar, improve the appearance of the file uploader, and ensure the selected demo dataset is clearly indicated.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [styles/main.css](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/styles/main.css)
- **Sidebar Text**: Add explicit white/light-gray text color for all elements in the sidebar to ensure readability against the dark translucent background.
- **File Uploader**:
    - Style the dropzone with a matching background-color, border-style (dashed), and hover effect.
    - Customize the "Browse files" button styling.
    - Color the labels and helper texts to match the theme.
- **Selectbox & Inputs**: Ensure that the "selected" state in selectboxes has a clear contrast.

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **Current Dataset Indicator**: Add a small "Currently Loaded: [filename]" info box at the top of the "Manage Fraud Dataset" section so users always know what data is in the system.

## Verification Plan

### Manual Verification
1.  **Sidebar**: Open the sidebar and verify that configuration labels, inputs, and captions are clearly readable.
2.  **Upload Component**: Verify the file uploader looks professional and matches the theme.
3.  **Demo Selection**: select a demo dataset, click upload, and verify the "Currently Loaded" indicator updates correctly.
