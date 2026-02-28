# Implementation Plan - Home Tab Integration

Add a comprehensive "Home" tab to serve as the landing page for the Sentinel Fraud AI workbench. This tab will provide an overview of the application, describe each feature, and showcase demo screenshots.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- **Tab Structure**: Add `tab_home` as the first tab in the `st.tabs` list.
- **Home Tab Content**:
    - **App Description**: A high-level overview of Sentinel Fraud AI.
    - **Feature Breakdown**: Detailed descriptions for:
        - Data Upload & Management
        - ML Dashboard (Supervised/Unsupervised)
        - SQL RAG (AI-driven Querying)
        - KB Chat (Context-aware Investigation)
        - Multi-Agent Console
        - Model Comparison & Evaluation
        - Agent Workflow Visualization
    - **AI Analytics Notice**: Explicitly state that data upload is required for AI analytics functionality.
    - **Demo Screenshots**: Use `st.expander` or gallery layout to display images from `other/screens/` as feature demonstrations.

## Verification Plan

### Manual Verification
1.  **Landing Page**: Open the workbench and verify that the "Home" tab is the default landing page.
2.  **Navigation**: Ensure descriptions and images for all tabs are present and correctly formatted.
3.  **Warning Visibility**: Confirm the AI analytics data dependency notice is prominent.
4.  **Image Rendering**: Verify all screenshots from `other/screens/` render correctly in the "Home" tab.
