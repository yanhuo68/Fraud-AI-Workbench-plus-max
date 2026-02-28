# Implementation Plan - Project Structure Refactoring

## Goal
Reorganize the project structure for better maintainability and clarity:
1. Move all Python code under `src/` directory
2. Create `documentation/` with subdirectories: `design/`, `user_manual/`, `screen/`
3. Keep `tests/` and `README.md` at root
4. Move all markdown files (except README.md) to `documentation/`

## Current Structure Analysis

### Python Code Directories
- `app/` - Streamlit application code
- `agents/` - Agent implementations
- `ml/` - Machine learning code
- `rag_sql/` - RAG SQL implementations
- `tools/` - Utility tools
- `config/` - Configuration files

### Markdown Files to Move
- Root level: `OPERATIONS.md`, `QUICKSTART.md`, `TEST.md` → `documentation/user_manual/`
- Implementation plans from brain artifacts → `documentation/design/`

### Directories/Files to Keep at Root
- `README.md`
- `docs/` - **Keep entire directory as-is** (contains 50+ fraud/ML documentation files)
- `tests/` - Test files
- `data/` - Runtime data
- `logs/` - Log files
- `requirements.txt`
- `Dockerfile`, `docker-compose.yml`
- `.env`, `.env.example`
- `.gitignore`, `.dockerignore`
- `Makefile`
- `langgraph_agent_map_diagram.mermaid`
- `rebuild_KB.bat`

## Proposed New Structure

```
Fraud-AI-Workbench-plus-max/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
├── .dockerignore
├── Makefile
├── langgraph_agent_map_diagram.mermaid
├── rebuild_KB.bat
├── src/
│   ├── app/           # Streamlit UI code
│   ├── agents/        # Agent implementations
│   ├── ml/            # Machine learning code
│   ├── rag_sql/       # RAG SQL code
│   ├── tools/         # Utility tools
│   └── config/        # Configuration
├── tests/             # Test files (kept at root)
├── docs/              # Technical docs (kept at root, 50+ files)
├── data/              # Data files (kept at root, contains runtime data)
├── logs/              # Log files (kept at root)
└── documentation/
    ├── design/        # Implementation plans from brain artifacts
    ├── user_manual/   # User-facing docs (OPERATIONS.md, QUICKSTART.md, TEST.md)
    └── screen/        # Screenshots (placeholder for future)
```

## Implementation Steps

### 1. Create New Directory Structure
```bash
mkdir -p src
mkdir -p documentation/design
mkdir -p documentation/user_manual
mkdir -p documentation/screen
```

### 2. Move Python Code to src/
```bash
mv app src/
mv agents src/
mv ml src/
mv rag_sql src/
mv tools src/
mv config src/
```

### 3. Move Documentation Files

**Move to documentation/user_manual/**:
- `OPERATIONS.md` (from root)
- `QUICKSTART.md` (from root)
- `TEST.md` (from root)

**Copy to documentation/design/**:
- Implementation plan files from brain artifacts directory

**Keep in place**:
- `docs/` directory and all its contents (50+ technical documentation files)

### 4. Update Import Paths

All Python files that import from moved modules need updates:
- `app.` → `src.app.`
- `agents.` → `src.agents.`
- `ml.` → `src.ml.`
- `rag_sql.` → `src.rag_sql.`
- `tools.` → `src.tools.`
- `config.` → `src.config.`

**Files likely needing updates**:
- `src/app/dashboard.py` - imports from agents, ml, rag_sql
- All tab files in `src/app/tabs/`
- Test files in `tests/`
- Any scripts that import these modules

### 5. Update File Path References

**No changes needed for docs/ references** since the directory stays at root.

**Key files that already reference docs/**:
- `src/app/components/sidebar.py` - references `docs/ml_pipeline.jpg` ✓
- `src/rag_sql/build_kb_index.py` - uses `--docs-dir docs` ✓
- Various tab files reference guideline files in `docs/` ✓

**Update if needed**:
- Database paths (`data/db/`, `data/fraud.db`) - should already be relative to root
- Knowledge base paths (`data/kb/`) - should already be relative to root
- Upload paths (`data/uploads/`) - should already be relative to root

### 6. Copy Implementation Plans

Copy all implementation plan `.md` files from the brain artifacts directory to `documentation/design/`:
- `implementation_plan_*.md` files

## Files to Modify

### Python Import Updates
- [MODIFY] `src/app/dashboard.py`
- [MODIFY] All `src/app/tabs/tab_*.py` files
- [MODIFY] All `tests/test_*.py` files
- [MODIFY] `src/rag_sql/build_kb_index.py`
- [MODIFY] Any other files with cross-module imports

### Path Reference Updates
- [MODIFY] `src/app/components/sidebar.py`
- [MODIFY] Files referencing `docs/` directory
- [MODIFY] `Dockerfile` (if needed)
- [MODIFY] `rebuild_KB.bat`
- [MODIFY] `README.md` - update directory structure documentation

## Verification Plan

### Automated Tests
```bash
# Run existing tests to ensure imports still work
cd /Users/yanhuo68/ai-projects/ml/Fraud-Investigation-Use-Case/Fraud-AI-Workbench-plus-max
python -m pytest tests/
```

### Manual Verification
1. **Build Docker Container**:
   ```bash
   docker compose up --build
   ```
   - Verify no build errors related to missing files
   - Application should start successfully

2. **Test Application Features**:
   - Navigate to http://localhost:8503
   - Test each tab loads correctly
   - Upload data (verify file paths work)
   - Check sidebar (verify ML pipeline image loads)
   - Test KB rebuild button (verify docs path updated correctly)

3. **Verify Directory Structure**:
   ```bash
   ls -la src/
   ls -la documentation/
   ls -la tests/
   ```
   - Confirm `src/` contains: app, agents, ml, rag_sql, tools, config
   - Confirm `documentation/` contains: design/, user_manual/, screen/
   - Confirm `tests/` still at root

4. **Verify Documentation**:
   - Check `documentation/design/` contains all docs files
   - Check `documentation/user_manual/` contains OPERATIONS.md, QUICKSTART.md, TEST.md
   - Verify implementation plans copied to `documentation/design/`

## Risk Mitigation

> [!WARNING]
> **Breaking Changes**: This is a major refactoring that will affect all imports and many file paths.

**Mitigation Strategy**:
1. Create a git branch or backup before starting
2. Update imports systematically, testing after each major component
3. Use find/replace for common patterns
4. Run tests frequently during refactoring

## Post-Refactoring Tasks

1. Update `README.md` with new directory structure
2. Update any documentation references to old paths
3. Consider updating `.gitignore` if needed
4. Update any CI/CD configurations (if applicable)
