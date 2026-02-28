# UI Design: Guideline Comparison (`tab_guideline_comparison.py`)

## 1. Purpose
The **Guideline Comparison** (Fraud Assessment) tab is an agentic workflow that compares specific fraud cases (rows in a table) against established investigation guidelines (documents) to generate an automated assessment.

## 2. Layout & Structure

### A. Selection
-   **Table**: Select the transactions/cases table.
-   **Case/Row**: Dropdown to pick a specific transaction ID.
-   **Guidelines**: Select relevant policy documents (e.g., "AML Policy v2").

### B. Assessment Generation
-   **"Generate Assessment"** Button.
-   **Prompt Strategy**: Constructs a robust prompt incorporating:
    -   The Case Data (JSON format).
    -   The Guideline Content.
    -   Output Template (Risk Level, Flagged Indicators, Recommended Actions).

### C. Output
-   **Risk Score**: High/Medium/Low badge.
-   **Analysis**: Detailed Markdown report explaining *why* the transaction violates (or complies with) the selected guidelines.

## 3. Key Logic & State
-   **`table_dataframes`**: Source of case data.
-   **`docs/`**: Source of guidelines.
-   **LLM Role**: Acts as a "Senior Investigator" applying rules to facts.
