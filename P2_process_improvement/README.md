# Process improvement

Paired queue-routing scenarios and service-level metrics.

## Run and verify

From this directory:

```powershell
python run.py
python -m unittest -v test_case.py
```

Uses only the Python standard library.

## Saved result and limits

Median case time changes from 31.34h to 20.85h under the specified routing assumptions.

A scenario sensitivity exercise, not a measured causal improvement or actual headcount saving. All business inputs are fictional. Re-running writes generated evidence to `output/`. [Saved results and assumptions](结果报告.html).
