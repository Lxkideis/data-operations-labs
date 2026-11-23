# HTTP reliability

Loopback HTTP fault injection, request traces and SLI/SLO accounting.

## Run and verify

From this directory:

```powershell
python run.py
python -m unittest -v test_case.py
```

Uses only the Python standard library.

## Saved result and limits

180 actual local requests across baseline, injected-fault and recovery phases.

Windows local experiment; no production-scale or Linux validation claim. Latency depends on the host. All business inputs are fictional. Re-running writes generated evidence to `output/`. [Saved results and assumptions](结果报告.html).
