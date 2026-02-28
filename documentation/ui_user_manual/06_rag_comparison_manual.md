# User Manual: RAG Comparison

Not sure which tool (SQL, KB, or Graph) is best for your question? Run them all at once!

## How to Use
1.  **Enter Question**: Type your query or select a sample question.
2.  **Select Judge**: Choose a "Judge" AI model (e.g., OpenAI GPT-4) to evaluate the answers.
3.  **Click "Run All"**: The system will simultaneously:
    *   Run a SQL Query.
    *   Search the Knowledge Base.
    *   Traverse the Knowledge Graph.
4.  **Compare Results**:
    *   View the three answers side-by-side.
    *   Read the "Consistency Analysis" to see if they agree.
    *   Check the "Performance Table" to see which was fastest.

## When to use what?
*   **SQL RAG**: Best for precise counts, sums, and averages ("How many...?").
*   **KB RAG**: Best for policy and text lookups ("What is the rule...?").
*   **Graph RAG**: Best for complex investigations ("How are they linked...?").
