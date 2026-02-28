# Implementation Plan - Guideline Comparison Redesign

## Goal
Simplify the Guideline Comparison tab by removing guideline selection dropdowns and generating assessments directly, using templates only as conceptual reference.

## Changes

### 1. Remove Guideline Selection UI
- Remove the two-column guideline selection section (fraud detection dropdown and fraud risk dropdown)
- Keep only: Data selection, LLM selection, and the "Compare Guidelines" button (rename to "Generate Assessment")

### 2. Simplified Analysis Prompts
Instead of showing templates to the LLM, we'll ask it to write comprehensive assessments:

**Fraud Detection Assessment Prompt:**
```
Analyze the provided data for fraud detection purposes.

Write a comprehensive fraud detection assessment covering:
- Executive summary of detection effectiveness
- Analysis of fraud patterns and anomalies found in the data
- Model performance metrics (if applicable from data)
- Operational effectiveness observations
- Recommendations for detection improvements

Use specific examples from the data sample.
```

**Fraud Risk Assessment Prompt:**
```
Analyze the provided data for fraud risk assessment purposes.

Write a comprehensive fraud risk assessment covering:
- Inherent fraud risk identification
- Risk control effectiveness
- Residual risk evaluation
- Risk appetite and thresholds
- Risk mitigation recommendations

Use specific examples from the data sample.
```

### 3. Files to Modify
- `app/tabs/tab_guideline_comparison.py`:
  - Remove guideline filtering and dropdown code (lines 50-83)
  - Remove template file reading (no longer needed in prompts)
  - Simplify prompts to not reference any templates or guidelines
  - Update button text and section headers

### 4. What Templates Become
The template files (`fraud-detection-assessment-template.md` and `fraud-risk-assessment-template.md`) remain in `docs/` as documentation but are NOT used in the LLM workflow.

## Benefits
1. Eliminates the template regurgitation problem entirely
2. Simpler user experience
3. LLM generates natural, data-driven analysis
4. Still provides the comparison feature
