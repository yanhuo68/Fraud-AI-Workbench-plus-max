# Implementation Plan - Sidebar API Key Configuration

Enable dynamic API key configuration in the sidebar, allowing users to override system environment variables.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [agents/llm_router.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/agents/llm_router.py)
- Add a `get_api_key(key_name: str)` helper function that checks `st.session_state` first, then `os.getenv`.
- Update `init_llm` to use `get_api_key` for both OpenAI and DeepSeek.

#### [MODIFY] [rag_sql/knowledge_base.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/rag_sql/knowledge_base.py)
- Import `get_api_key` from `agents.llm_router`.
- Use `OpenAIEmbeddings(api_key=get_api_key("OPENAI_API_KEY"))` when creating or loading the vectorstore.

#### [MODIFY] [dashboard.py](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/dashboard.py)
- Add a new "API Configuration" section in the sidebar using `st.sidebar.expander`.
- Add `st.text_input` for `OPENAI_API_KEY` and `DEEPSEEK_API_KEY` with `type="password"`.
- Update the "Rebuild KB Index" `subprocess.run` call to include the custom API keys in the environment via the `env` argument.

## Verification Plan

### Manual Verification
1.  **Env Only**: Run the app with valid env keys and no sidebar input. Verify SQL RAG and KB Chat work.
2.  **Sidebar Override**: Input a *different* valid key in the sidebar. Verify the app uses the sidebar key (logs/behavior).
3.  **Priority Test**: Input an *invalid* key in the sidebar while having a *valid* env key. Verify the app fails with 401, proving sidebar priority.
4.  **KB Rebuild**: Test "Rebuild KB Index" with sidebar key only. Verify it succeeds.
