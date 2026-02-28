# User Manual: ML Dashboard

The ML Dashboard allows you to train and evaluate fraud detection models without writing code.

## Prerequisites
*   You must have uploaded data in the **Upload Data** tab.

## How to Train a Model
1.  **Select Target**: In the sidebar, choose the column that indicates fraud (e.g., `is_fraud`).
2.  **Select Features**: Choose the columns to use for prediction (e.g., `amount`, `merchant`, `category`).
    *   *Tip*: Exclude ID columns like `transaction_id` or `user_id` as they don't help prediction.
3.  **Choose Model**: Select an algorithm (Random Forest is usually a good start).
4.  **Adjust Settings**: Use the sliders to tune the model (optional).
5.  **Train**: The model trains automatically when settings change.

## Interpreting Results
*   **Metrics**: Look at **Recall**. In fraud detection, high Recall is often more important than high Accuracy because you want to catch as many fraud cases as possible.
*   **Confusion Matrix**:
    *   **Top-Left**: True Negatives (Legitimate transactions correctly identified).
    *   **Bottom-Right**: True Positives (Fraud correctly caught).
*   **Feature Importance**: The bar chart shows which factors drive the fraud model (e.g., "amount" might be the biggest predictor).
