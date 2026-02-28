# Implementation Plan - Fix Template Regurgitation (Take 3)

## Problem
The LLM persistently outputs the raw, blank template instead of filling it out, even with strict "fill it out" instructions. This is likely because providing the full template text leads the model to pattern-match and copy-paste.

## Solution: "Structure, Don't Copy"
We will alter the prompting strategy to treat the template as a **Format Definition** query rather than a **Completion** query.

### Changes
1.  **Renaming in Prompt**: Change "Assessment Template" to "Required Report Structure".
2.  **System Message Update**: 
    -   Explicitly state: "You are generating a NEW document."
    -   "Use the provided structure as a SCAFFOLD."
    -   "Do not output the scaffolding instructions."
3.  **Template Injection**: Instead of just `{template_content}`, we might inject "Instructions: [WRITE FINDINGS HERE]" into the template string programmatically before sending it (optional, but good backup).
4.  **Chain of Thought**: Ask the model to "First, list 3 findings. Then, format them into the report." (This might clutter the output, so maybe just internal CoT).

### Proposed Prompt Structure
**System:**
"You are a Senior Auditor. You must write a detailed assessment report.
Input: Data + Guideline + Report Structure.
Output: A fully written report following the structure.
CRITICAL: Do not just copy the structure. You must write sentences and fill tables."

**Human:**
...
### 4. Required Report Structure
(Follow this exact hierarchy and table layout)
{template_content}
...
**TASK:**
Write the report now.
