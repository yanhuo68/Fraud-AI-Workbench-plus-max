# Fraud Detection & Control Matrix

## 1. Preventive & Detective Control Mapping

| Control ID | Fraud Risk | Control Type (Preventive/Detective) | Automated/Manual | Description | Data Source | Frequency | Control Owner | KPI | KRI |
|------------|------------|--------------------------------------|------------------|-------------|-------------|-----------|---------------|-----|-----|
| DC-01 | Account Takeover | Preventive | Automated | MFA enforcement | IAM Logs | Real-time | IT Security | MFA Adoption % | Login Failure Spike |
| DC-02 | Claims Fraud | Detective | Automated | Claims anomaly scoring model | Claims DB | Daily | Fraud Analytics | Detection Rate | False Positive Rate |

---

## 2. Control Effectiveness Rating

| Rating | Definition |
|--------|------------|
| Effective | Control operates as designed, no material gaps |
| Partially Effective | Minor gaps identified |
| Ineffective | Significant breakdown or missing control |

---

## 3. Control Testing Plan

- Design Effectiveness Testing
- Operating Effectiveness Testing
- Data Integrity Validation
- Model Validation (if applicable)
- Exception Handling Review
