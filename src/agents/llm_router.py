# agents/llm_router.py
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.ollama import ChatOllama
import requests
import os

def get_available_llms(include_local: bool = True):
    from src.agents.local_llm_discovery import list_ollama_models, detect_lmstudio

    models = [
        "openai:gpt-4o-mini",
        "openai:gpt-4o",
        "deepseek:deepseek-chat",
        "deepseek:deepseek-reasoner",
        "google:gemini-1.5-pro",
        "anthropic:claude-3-5-sonnet-20240620",
        "anthropic:claude-3-opus-20240229",
    ]

    if include_local:
        ollama = list_ollama_models()
        lmstudio = detect_lmstudio()
        models += ollama + lmstudio

    models.append("custom:http")
    return models

def get_api_key(key_name: str) -> str:
    """
    Priority order (highest to lowest):
    1. System environment variable (set outside the app)
    2. .env file
    3. Streamlit session state (sidebar input)
    """
    import streamlit as st
    
    # Priority 1: Check system environment variable first
    # This gets both system env vars AND .env file vars (loaded by python-dotenv)
    env_value = os.getenv(key_name)
    if env_value and not env_value.startswith("your") and not env_value.startswith("sk-your"):
        # Valid key found in environment (system or .env)
        return env_value
    
    # Priority 2: Fall back to sidebar input if env var is missing or placeholder
    sidebar_mapping = {
        "OPENAI_API_KEY": "sidebar_openai_key",
        "DEEPSEEK_API_KEY": "sidebar_deepseek_key",
        "GOOGLE_API_KEY": "sidebar_google_key",
        "ANTHROPIC_API_KEY": "sidebar_anthropic_key"
    }
    
    state_key = sidebar_mapping.get(key_name)
    if state_key and state_key in st.session_state and st.session_state[state_key]:
        return st.session_state[state_key]
    
    # Return empty or placeholder if nothing found
    return env_value or ""

def _get_local_url(port: int, path: str = ""):
    """Try to find the correct local endpoint (Docker vs Local)."""
    for host in ["localhost", "host.docker.internal"]:
        url = f"http://{host}:{port}{path}"
        try:
            # Quick check if reachable
            requests.get(url.replace("/v1", ""), timeout=0.5)
            return url
        except Exception:
            continue
    return f"http://localhost:{port}{path}"

def init_llm(model_id: str):
    # --- OpenAI ---
    if model_id.startswith("openai:"):
        name = model_id.split(":", 1)[1]
        return ChatOpenAI(
            model=name,
            api_key=get_api_key("OPENAI_API_KEY"),
            temperature=0.1,
        )

    # --- DeepSeek ---
    elif model_id.startswith("deepseek:"):
        name = model_id.split(":", 1)[1]
        return ChatOpenAI(
            model=name,
            api_key=get_api_key("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1",
            temperature=0.1,
        )

    # --- Ollama ---
    elif model_id.startswith("local_ollama:"):
        name = model_id.split(":", 1)[1]
        base_url = _get_local_url(11434)
        return ChatOllama(
            model=name,
            base_url=base_url,
            temperature=0.1,
        )

    # --- LM Studio (OpenAI-compatible endpoint) ---
    elif model_id.startswith("local_lmstudio:"):
        name = model_id.split(":", 1)[1]
        base_url = _get_local_url(1234, "/v1")
        return ChatOpenAI(
            model=name,
            base_url=base_url,
            api_key="lm-studio",
            temperature=0.1,
        )

    # --- Google Gemini ---
    elif model_id.startswith("google:"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        name = model_id.split(":", 1)[1]
        return ChatGoogleGenerativeAI(
            model=name,
            google_api_key=get_api_key("GOOGLE_API_KEY"),
            temperature=0.1,
        )

    # --- Anthropic Claude ---
    elif model_id.startswith("anthropic:"):
        from langchain_anthropic import ChatAnthropic
        name = model_id.split(":", 1)[1]
        return ChatAnthropic(
            model=name,
            anthropic_api_key=get_api_key("ANTHROPIC_API_KEY"),
            temperature=0.1,
        )

    # --- Custom HTTP Endpoint ---
    elif model_id.startswith("custom:http"):
        url = os.getenv("CUSTOM_LLM_URL", "http://localhost:8080/v1")
        model = os.getenv("CUSTOM_LLM_MODEL", "local-model")
        return ChatOpenAI(model=model, base_url=url, api_key="none")

    raise ValueError(f"Unknown LLM: {model_id}")
