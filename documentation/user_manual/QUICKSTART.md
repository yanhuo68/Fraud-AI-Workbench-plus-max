# 🚀 Quick Setup Guide

**Welcome!** This guide will help you get started after cloning the project.

---

## Step 1: Get Your API Key

1. Visit [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Create a new API key (starts with `sk-proj-...`)
3. Copy it for the next step

---

## Step 2: Configure API Key

Choose **one** method:

### 🎯 Method A: System Environment (Recommended)

**Mac/Linux:**
```bash
# Add to your shell profile (~/.zshrc or ~/.bash_profile)
export OPENAI_API_KEY=sk-proj-your-actual-key

# Or set temporarily for current session
export OPENAI_API_KEY=sk-proj-your-actual-key
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-proj-your-actual-key"
```

### 📝 Method B: Edit .env File

1. Open `.env` in project root
2. Replace placeholder:
   ```bash
   # Before
   OPENAI_API_KEY=sk-your-openai-key-here
   
   # After
   OPENAI_API_KEY=sk-proj-your-actual-key
   ```

### 💡 Method C: Use Sidebar (Testing Only)

- Start the app first (see Step 3)
- Open sidebar → "🔑 API Keys"
- Enter your key
- ⚠️ Session-based only - not persistent

---

## Step 3: Start the Application

### Using Docker Compose (Recommended):
```bash
docker compose up --build
```

### Using Docker Run:
```bash
docker build -t fraud-lab-plus-max .
docker run -p 8503:8503 \
  -e OPENAI_API_KEY=sk-proj-your-key \
  fraud-lab-plus-max
```

### Local Python (Without Docker):
```bash
pip install -r requirements.txt
streamlit run app/dashboard.py
```

---

## Step 4: Access the Application

Open your browser:
- **URL:** http://localhost:8503
- You should see the Fraud Analytics AI Workbench

---

## Step 5: Upload Sample Data

1. Go to **"📁 Upload Data"** tab
2. **Option A (Quick):**
   - Look for **"🎯 Load Demo Guidelines"**
   - Click **📥 Load Selected Guidelines** to populate the Knowledge Base
   - Look for **"Quick Start: Load Demo Dataset"** and click **📥 Load Demo** to populate the Database
3. **Option B (Custom):**
   - Drag & drop your CSVs into the upload area

**Sample dataset:** Use any fraud detection dataset from Kaggle or create your own.
**Note:** All uploaded data is automatically consolidated into a single database, making it immediately available for SQL RAG and ML training.

---

## Step 6: Explore Fraud Guidelines
1.  Open the **Sidebar** (left panel).
2.  Expand **"🛡️ Fraud Guidelines"**.
3.  Select a category (Risk vs Detection) to see available documents.
4.  Click **View Guideline** to overlay the document on your workspace.

---

## 🎉 You're Ready!

### Quick Tour:

- **📁 Upload Data** - Import your fraud dataset.
- **📈 ML Dashboard** - Train models (RF, Gradient Boosting) on **any** uploaded table.
- **🧠 SQL RAG** - Ask questions in natural language (errors are auto-corrected).
- **� KB RAG** - Query fraud guidelines and rules.
- **🧭 Graph RAG** - Advanced retrieval with filters.
- **⚖️ RAG Comparison** - Compare responses from different RAG pipelines.
- **📊 Model Comparison** - Compare multiple trained models side-by-side.
- **� Guideline Comparison** - Analyze differences between fraud policies.
- **🤖 ERD Diagram** - Visualize database schema (requires manual generation).
- **🤖 Agent Workflow** - Inspect and debug autonomous agent steps.

---

## ⚠️ Troubleshooting

### "API key not configured" warning?

**Cause:** API key not properly set

**Fix:**
1. Check you set it via one of the methods in Step 2
2. If using .env or system env, restart Docker:
   ```bash
   docker compose down
   docker compose up --build
   ```
3. Verify your key is valid at [OpenAI Platform](https://platform.openai.com/account/api-keys)

### Port 8503 already in use?

**Fix:**
```bash
# Change port in docker-compose.yml
ports:
  - "8504:8503"  # Use 8504 instead
```

### Docker build fails?

**Fix:**
1. Ensure Docker is running
2. Check you have enough disk space
3. Try: `docker system prune` to clean up

### Changes not appearing?

**Cause:** Docker container using stale code.

**Fix:**
We have updated `docker-compose.yml` to mount the source code directly. To apply this fix:
```bash
docker compose down
docker compose up --build
```

---

## 📚 Additional Resources

- **User Manual:** `other/guide/user_manual.md` (if available)
- **API Key Guide:** See artifacts in this conversation
- **Design Document:** `other/guide/design_document.md` (if available)

---

## 🆘 Need Help?

- Check error messages carefully - they often include fix instructions
- Review the README.md for detailed features
- Ensure all requirements are installed: `pip install -r requirements.txt`

**Happy Investigating! 🕵️**
