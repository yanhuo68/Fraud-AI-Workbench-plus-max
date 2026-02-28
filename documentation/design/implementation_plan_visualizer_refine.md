# Implementation Plan - Visualizer Refinement

Improve the appearance of the Agent Workflow Visualizer by centering/resizing the graph and ensuring its background coordinates with the dark theme.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- Use `st.columns([1, 2, 1])` to center the workflow graph and make it appear smaller (using the middle column).
- Wrap the image in a container with a custom class for CSS targeting.

#### [MODIFY] [styles/main.css](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/styles/main.css)
- Add styling for the workflow graph container:
    - Set a `background-color` (using `--warmer-bg` or a slightly lighter charcoal).
    - Add `padding` and `border-radius`.
    - Apply a subtle `box-shadow`.
    - If the PNG has a hard white background, apply a `filter: invert(0.9) hue-rotate(180deg)` (optional adjustment) or simply a background that softens the transition.

## Verification Plan

### Manual Verification
1.  **Visualizer Tab**: Navigate to the "Agent Workflow Visualizer" tab.
2.  **Sizing Check**: Verify the graph is centered and reasonably sized.
3.  **Background Check**: Verify the graph container background looks professional and integrated with the theme.
