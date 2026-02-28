# Implementation Plan - Agent Workflow Tab

## Goal
Create a new "Agent Workflow" tab after the "ERD Diagram" tab and move all agent workflow-related functionality from the sidebar to this new tab.

## Proposed Changes

### 1. Create New Tab File
**File**: `app/tabs/tab_agent_workflow.py` [NEW]

Content will include:
- Display of LangGraph workflow diagrams (Mermaid code)
- Display of generated agent workflow images (JPG/PNG)
- Abbreviation legend for agent names
- Support for both:
  - Dynamic workflow from `st.session_state.langgraph_workflow`
  - Static fallback from `langgraph_agent_map_diagram.mermaid` file

### 2. Update Dashboard
**File**: `app/dashboard.py`

Changes:
- Add import: `from app.tabs.tab_agent_workflow import render_agent_workflow_tab`
- Update `tab_names` list to include `"🤖 Agent Workflow"` after `"🤖 ERD Diagram"`
- Add new tab rendering: `with tabs[9]: render_agent_workflow_tab()`

### 3. Update Sidebar
**File**: `app/components/sidebar.py`

Changes:
- **Remove** lines 89-186 (all agent workflow preview code)
- Keep only: API Keys, Tools (Rebuild KB, Clean DB, Rebuild Graph, Visualize Graph), and ML Pipeline image

## Verification Plan

###Manual Testing
1. Start the application: `docker compose up --build`
2. Open the app in browser at `http://localhost:8503`
3. Navigate to the new "🤖 Agent Workflow" tab (should be after ERD Diagram)
4. Verify that:
   - Mermaid diagram is displayed (if workflow exists)
   - Agent workflow image is displayed (if generated)
   - Abbreviation legend is shown
5. Check sidebar to confirm agent workflow section is removed
6. Verify other tabs still work correctly

## Files to Modify
- [NEW] `app/tabs/tab_agent_workflow.py`
- [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/dashboard.py)
- [MODIFY] [sidebar.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/components/sidebar.py)
