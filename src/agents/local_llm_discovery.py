# agents/local_llm_discovery.py
import subprocess
import requests

def list_ollama_models():
    """Return a list of locally installed Ollama models via REST API."""
    urls = ["http://localhost:11434/api/tags", "http://host.docker.internal:11434/api/tags"]
    for url in urls:
        try:
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                return [f"local_ollama:{m}" for m in models]
        except Exception:
            continue
    return []

def detect_lmstudio():
    """Check if LM Studio server is running."""
    urls = ["http://localhost:1234/v1/models", "http://host.docker.internal:1234/v1/models"]
    for url in urls:
        try:
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                models = [m["id"] for m in data.get("data", [])]
                return [f"local_lmstudio:{m}" for m in models]
        except Exception:
            continue
    return []
