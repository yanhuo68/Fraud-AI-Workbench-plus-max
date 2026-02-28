# User Manual: Model Comparison

Compare different machine learning algorithms to find the champion model.

## How to Use
1.  **Select Target**: Choose your fraud label column.
2.  **Pick Models**: Select multiple algorithms (e.g., Random Forest AND XGBoost).
3.  **Set Split**: Choose how much data for training vs. testing (usually 80/20).
4.  **Run**: The system trains all selected models.

## Analyzing Results
*   **Leaderboard**: Sort the table by **Recall** or **F1-Score**. The top model is your "Champion".
*   **ROC Curve**: The line providing the most area under the curve (top-left) is generally the best model.
*   **Time**: Consider training time. A model that is 0.1% better but takes 10x longer might not be worth it.
