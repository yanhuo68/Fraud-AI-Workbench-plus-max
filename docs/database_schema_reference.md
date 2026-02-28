# Database Schema Reference for Fraud Transactions

This document provides exact schema definitions for the `transactions` table stored in SQLite. LLMs must refer to these field names to avoid SQL hallucinations.

---

# Table: transactions

| Column Name | Type | Description |
|-------------|------|-------------|
| `step` | INTEGER | Time step (hour index). |
| `type` | TEXT | Transaction type (`CASH-IN`, `CASH-OUT`, `TRANSFER`, `PAYMENT`, `DEBIT`). |
| `amount` | REAL | Transaction amount. |
| `nameOrig` | TEXT | Sender account ID. |
| `oldbalanceOrg` | REAL | Sender balance before transaction. |
| `newbalanceOrig` | REAL | Sender balance after transaction. |
| `nameDest` | TEXT | Receiver account ID. |
| `oldbalanceDest` | REAL | Receiver balance before transaction. |
| `newbalanceDest` | REAL | Receiver balance after transaction. |
| `isFraud` | INTEGER | 1 if fraudulent. |
| `isFlaggedFraud` | INTEGER | 1 if flagged suspicious by the system. |

---

# Key Schema Characteristics

- `step` increases monotonically and represents hours.
- Only certain fields change for each transaction.
- `nameOrig` and `nameDest` are identifiers, not actual names.
- `oldbalanceDest` or `newbalanceDest` may be zero for new accounts.
- Fraud normally appears only in `TRANSFER` and `CASH_OUT` types.

---

# Purpose of This Document
LLMs rely on the schema to:
- Avoid invalid SQL queries,
- Construct correct joins and filters,
- Reference applicable columns for fraud analysis.
