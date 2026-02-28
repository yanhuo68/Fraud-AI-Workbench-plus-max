# Fraud Detection AI Workbench

Streamlit + LangGraph + RAG workspace for fraud analytics. Upload data, explore with SQL+RAG, train/evaluate ML pipelines, compare models, inspect ERDs, and chat with docs/KB. Agents and graph tools are wired in for advanced workflows.

## Features
- **Professional Light Theme**: Clean, high-contrast UI with Sapphire Blue action buttons and Red system control indicators for a command-center feel.
- **Fraud Guidelines Library**: Integrated sidebar access to fraud detection rules, risk policies, and investigation playbooks.
- **Risk Guideline Management**:
    - **Upload**: Securely upload internal risk policy documents (Markdown).
    - **Demo Loader**: Quickly load standard fraud frameworks (KPIs, Risk Registers) for testing.
    - **Auto-Indexing**: Automatically updates the Knowledge Graph and Vector Store upon document addition.
- **Graph RAG**: Hybrid TF‑IDF/embedding retrieval over docs/uploads/DB previews; structured filters; filtered fraud counts; side‑by‑side context + data slice; confidence/snippet scores; regression logs.
- **SQL RAG**: Plan/fix/rank SQL over uploaded tables; schema grounding; fraud risk scoring; training dataset builder; scrollable SQL; sample questions.
- **ML Dashboard**: Feature selection/auto-drop, SMOTE, split sliders, cost-based threshold tuning, AUC/PR, ROC/PR plots, persistence/load, data quality/drift checks, CSV downloads.
- **Model Comparison**: Choose table/label, supervised + anomaly models, scalar metrics, ROC, PDF export.
- **ERD**: Select tables, generate Mermaid + PNG preview/download; PK/FK inferred from DB PRAGMAs; relationship list shown.
- **Agent workflow**: Sidebar mermaid/JPG preview with abbreviation legend; uses `langgraph_agent_map_diagram.mermaid` or session graph.
- **KB Chat**: RAG answers with context inspector and RAG vs No-RAG comparison.
- **Logs/artifacts**: KB rebuild logs, Graph RAG logs, ML runs, ERD outputs, agent workflow images in `data/generated/`.

## Paths
- Data: `data/` (uploads, db, kb, ml, graph, erd, generated)
- Logs: `logs/`
- Docs/schemas: `docs/` (schema markdowns, pipeline image, agent workflow)
- Generated: `data/generated/agent_workflow*.jpg`, `data/generated/langgraph_agent_map_diagram.mermaid`

## Requirements
See `requirements.txt`. Notable: `graphviz`, `faiss-cpu`, `sentence-transformers`, `langchain*`, `altair`, `matplotlib`, `imbalanced-learn`.

## 🚀 Quick Setup (First Time)

**New to this project? Start here:**

1. **Get OpenAI API Key:** [platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
2. **Set environment variable:**
   ```bash
   export OPENAI_API_KEY=sk-proj-your-actual-key
   ```
3. **Start the app:**
   ```bash
   docker compose up --build
   ```
4. **Open browser:** http://localhost:8503

📖 **Detailed setup guide:** See [QUICKSTART.md](QUICKSTART.md)

## Run locally
```bash
pip install -r requirements.txt
streamlit run app/dashboard.py
```

## Docker

### Option 1: Docker Compose (Recommended)
```bash
docker compose up --build
```

### Option 2: Manual Docker Build
```bash
docker build -t fraud-detection-ai-workbench-plus-max .
docker run -p 8503:8503 fraud-detection-ai-workbench-plus-max
```

Visit **http://localhost:8503**.

## LLMs/Keys
Some flows use OpenAI or local LLMs (Ollama/LM Studio). Set the relevant API keys/environment variables as needed.

## Notes
- ERD/agent images require `graphviz` installed (Dockerfile includes it).
- Graph rebuild scans `docs/`, `data/uploads/`, and DB tables to populate graph corpus/index.

## 🧪 Testing
Run unit tests to verify the installation:
```bash
pytest tests/
```
See [Testing Guide](documentation/ui_user_manual/testing_guide.md) for details.

## 📚 Documentation
- **User Manuals**: [documentation/ui_user_manual/](documentation/ui_user_manual/)
- **UI Design**: [documentation/ui_design/](documentation/ui_design/)
