# Implementation Plan - Template Fix V4 (Aggressive Placeholders)

## Root Cause Analysis
The previous fix (V3) injected instructions only at `\n\n` (paragraph breaks). It failed to touch the **Markdown Tables**, which consist of lines like `| Metric |     |`. The LLM sees these as completed structures and preserves them. 

## The Solution: "Aggressive Placeholder Injection"
We will programmatically "defac" the template before the LLM sees it. We will fill every empty void with a loud, ugly placeholder that the LLM cannot ignore.

### 1. Regex logic
We will use Python's `re` module to perform the following substitutions on `template_content`:
- **Tables**: Replace `|(\s+)|` (empty cells) with `| [DATA REQUIRED] |`.
- **Lists**: Replace `-` (empty list items) with `- [FINDING REQUIRED]`.
- **Blank Lines**: Replace `\n\n` with `\n\n[ANALYSIS REQUIRED]\n\n`.

### 2. Prompt Update
The Prompt will be simplified to a direct instruction:
"The text below contains placeholders like `[DATA REQUIRED]`. Your ONLY job is to replacing every single placeholder with actual analysis from the data. Do not leave any placeholder text remaining."

### 3. Files to Modify
- `app/tabs/tab_guideline_comparison.py`:
    - Add `import re`.
    - Implement the regex cleaning logic inside `render_guideline_comparison_tab`.
    - Update `SystemMessage` and `HumanMessage`.

## Verification
- User should see tables explicitly filled out.
- If the model fails this, it ends up printing "[DATA REQUIRED]" which is at least better debugging info than blank space.
