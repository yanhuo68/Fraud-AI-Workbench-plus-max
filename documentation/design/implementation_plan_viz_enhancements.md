# Implementation Plan - Visualization Enhancements

## Goal
Improve visual clarity and educational value of ML Pipeline and Agent Workflow diagrams.

## Proposed Changes

### 1. ML Pipeline Diagram Enhancement
**Problem**: Current diagram in `docs/ml_pipeline.jpg` is too small and lacks visual distinction between nodes.

**Solution**: Generate a new, larger ML pipeline diagram with color-coded nodes.

**Approach**:
- Use `generate_image` tool to create a professional ML pipeline workflow diagram
- Include standard ML stages: Data Collection → Preprocessing → Feature Engineering → Model Training → Evaluation → Deployment → Monitoring
- Each node should have a distinct color for easy identification
- Make it large enough to be readable in the sidebar
- Save as `docs/ml_pipeline.jpg` (replacing existing)

### 2. Agent Workflow Tab - Node Insights
**Problem**: Network diagram displays agent workflow but doesn't explain what each node does.

**Solution**: Add explanatory content to the Agent Workflow tab.

**File**: `app/tabs/tab_agent_workflow.py`

Changes:
- Add a new section "📖 Node Explanations" after the diagram
- Create a detailed explanation for each agent node type:
  - **U (User)**: Entry point for user queries
  - **SP (SQL/Schema Planner)**: Analyzes query intent and plans SQL generation
  - **SE (SQL Executor)**: Executes generated SQL queries against the database
  - **SC (SQL Checker)**: Validates and repairs malformed SQL
  - **KR (Knowledge Retriever)**: Retrieves relevant documentation from knowledge base
  - **KG (Knowledge Grounder)**: Injects context into responses
  - **SA (Schema Analyzer)**: Analyzes database schema and generates ERDs
  - **MM (Model Manager)**: Manages ML model loading and saving
  - **ME (Model Evaluator)**: Computes model performance metrics
  - **MD (Model Deployer)**: Handles model deployment and artifacts
  - **RS (Report Synthesizer)**: Generates final reports and insights

## Files to Modify
- [NEW] `docs/ml_pipeline.jpg` (generated image)
- [MODIFY] [tab_agent_workflow.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max/app/tabs/tab_agent_workflow.py)

## Verification Plan
1. Check that new ML pipeline image displays clearly in sidebar
2. Verify Agent Workflow tab shows node explanations
3. Confirm all explanations are accurate and helpful
