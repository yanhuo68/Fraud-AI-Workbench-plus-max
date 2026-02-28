# Implementation Plan - Robust Agent Player Replay

Fix the "invisible" Auto Play issue by hardening the playback loop and adding high-visibility state notifications.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [agents/execution_player.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/agents/execution_player.py)
- **High-Visibility Status**:
    - Add a `st.success` or `st.info` banner at the top of the player when `is_playing` is True.
    - Explicitly state: "🎬 **Auto-Playback In Progress... Step X of Y**".
- **Step Notifications**:
    - Use `st.toast("Next node: [NodeName]")` on every step during playback to provide immediate feedback that the loop is alive.
- **Progress Bar Hardening**:
    - Move `st.progress` to a more prominent location.
- **Rerun Logic Refinement**:
    - Ensure `st.rerun()` is called ONLY after the state is fully synced.
    - Add a `st.session_state` key for total steps to ensure stability across reruns.
- **UI Layout**:
    - Use `st.container(border=True)` to better encapsulate the player and give it a premium "console" look.

## Verification Plan

### Manual Verification
1. **Run Multi-Agent Workflow**: Go to Agents tab and run any sample question.
2. **Auto Play Test**: 
    - Click "Auto Play".
    - Verify a "Playback In Progress" banner appears.
    - Verify toasts appear on every page refresh.
    - Verify the progress bar moves clearly from 0% to 100%.
3. **Interrupt Test**: Click "Stop" during the 1-second sleep period and verify the player stops on the current node.
