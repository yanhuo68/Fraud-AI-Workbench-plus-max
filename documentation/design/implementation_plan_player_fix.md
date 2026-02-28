# Implementation Plan - Fix Agent Player Auto Play

Address the broken "Auto Play" logic in the Agent Execution Player to allow seamless step-by-step replay of agent workflows.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [agents/execution_player.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/agents/execution_player.py)
- **State Management**: Initialize `st.session_state.is_playing = False` if not present.
- **Auto Play Control**:
    - Replace the broken for-loop with a single toggle.
    - If "Auto Play" is clicked, set `is_playing = True`.
    - If "Stop" is clicked, set `is_playing = False`.
- **Sequential Execution**:
    - Add logic at the end of `render_execution_player` to check `is_playing`.
    - If `is_playing` is True and the current step is not the last one, sleep for 1 second, increment `trace_idx`, and trigger `st.rerun()`.
    - If the last step is reached while `is_playing` is True, set `is_playing = False`.
- **Visual Feedback**:
    - Add a `st.progress` bar to show current playback progress.
    - Highlight the active step in the UI more prominently.

## Verification Plan

### Manual Verification
1. **Run a Workflow**: Run any agent workflow in the Agents tab.
2. **Test Controls**:
    - Click "Next" and "Previous" to verify manual stepping.
    - Click "Auto Play". Verify the "Active Node" and "Step Details" update automatically every second.
    - Click "Stop" during playback. Verify playback halts immediately.
    - Verify playback automatically stops at the last step.
