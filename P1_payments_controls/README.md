# Payment controls

SQLite reconciliation with currency-aware exception classification.

## Run and verify

From this directory:

```powershell
python run.py
python -m unittest -v test_case.py
```

Uses only the Python standard library.

## Saved result and limits

10,000 synthetic ledger rows; 210 injected exceptions (200 ledger exceptions and 10 partner orphans).

Amounts are simulated exposure, not real losses or recoveries. All business inputs are fictional. Re-running writes generated evidence to `output/`. [Saved results and assumptions](结果报告.html).
