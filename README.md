# Data Operations Labs

Five small, reproducible Python case studies in financial controls, operations, reliability and model evaluation. Created with AI assistance in October 2026; prepared for public publication on 2026-11-23. These are portfolio exercises with synthetic inputs, not employment, coursework, client engagements or production systems.

| Case | Main question / method |
|---|---|
| [Payment controls](P1_payments_controls/README.md) | SQLite reconciliation with currency-aware exception classification. |
| [Process improvement](P2_process_improvement/README.md) | Paired queue-routing scenarios and service-level metrics. |
| [Commercial credit scenarios](P3_commercial_credit/README.md) | Debt and working-capital sensitivity for a fictional borrower. |
| [HTTP reliability](P4_reliability_lab/README.md) | Loopback HTTP fault injection, request traces and SLI/SLO accounting. |
| [Governed ML evaluation](P5_governed_ml/README.md) | NumPy logistic model with leakage exclusion and train-only preprocessing. |

## Run a case

Python 3.11+ is recommended. P1-P4 use only the standard library; P5 also needs NumPy (`python -m pip install -r requirements.txt`). Run from the individual case directory so imports are unambiguous:

```powershell
cd P1_payments_controls
python run.py
python -m unittest -v test_case.py
```

Repeat with another case directory. P4 binds only to loopback on an ephemeral port. Generated files are written under each case's `output/`; CSVs and SQLite databases are regenerated instead of committed. Saved JSON metrics and text reports remain inspectable. `run.py` can overwrite generated outputs, so keep personal notes separately.

## More developed applications

- [Clearset Close](https://github.com/Lxkideis/clearset-close): seven-source financial controls with independent bank evidence and review separation.
- [Payment Operations Lab](https://github.com/Lxkideis/payment-ops-lab): PostgreSQL reconciliation and versioned exception investigation.

## Interpretation

Numerical results describe explicitly constructed synthetic scenarios or small local measurements. They do not establish business savings, real credit decisions, production reliability, or superiority on external data. Each case includes tests and its own assumptions and limits.
