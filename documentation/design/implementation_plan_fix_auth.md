# Implementation Plan - Fix OpenAI Authentication Error

Resolve the `AuthenticationError` caused by a placeholder API key in the `.env` file.

## Proposed Changes

### [Fraud-AI-Workbench-basic]

#### [MODIFY] [.env](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/.env)
- Comment out the placeholder `OPENAI_API_KEY=your_api_key_here`. This prevents it from overriding valid system environment variables when using `env_file` or `load_dotenv()`.

#### [MODIFY] [docker-compose.yml](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/docker-compose.yml)
- Add `OPENAI_API_KEY` and `DEEPSEEK_API_KEY` to the `environment` section *without* explicit values. This allows Docker Compose to pass these variables from the host's environment into the container.

#### [MODIFY] [SETUP.md](file:///Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-basic/SETUP.md)
- Clarify that users should either update the `.env` file with their real keys OR ensure their host system variables are properly exported before running Docker.

## Verification Plan

### Manual Verification
- Verify that if `OPENAI_API_KEY` is not in `.env`, the application can still access the host's version when run via Docker Compose (with the proposed yaml change).
- Ensure the `.env` file remains a valid template for users who prefer file-based configuration.
